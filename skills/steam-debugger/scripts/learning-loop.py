#!/usr/bin/env python3
"""steam-debugger learning loop — a Claude Code hook that makes the skill grow
from the sessions that use it.

Two hook events, both stdlib-only and fail-open (any error = no effect):

  session-start  Point the session at the local learnings file, so what earlier
                 sessions on this machine learned is looked up before re-deriving it.
  stop           After a stretch of Steam/game debugging, block the stop once and
                 ask Claude to write down what it learned, with evidence.

Two tiers of knowledge:

  Local learnings  ${XDG_DATA_HOME:-~/.local/share}/steam-debugger/learnings.md
                   Every machine has its own. Claude records findings here without
                   asking anyone, including unconfirmed ones (marked as such).
  The skill        Only when this machine has a writable checkout of the skill's
                   repo, named in ${XDG_CONFIG_HOME:-~/.config}/steam-debugger/repo
                   (one line: the path of the skill directory inside the checkout).
                   Findings that are confirmed and general are promoted into the
                   skill's reference files and pushed. Users without that file
                   only ever get the local tier.

Wire it up in settings.json (or pass the same JSON with `claude --settings`):

  "hooks": {
    "SessionStart": [{"hooks": [{"type": "command",
        "command": "python3 /path/to/steam-debugger/scripts/learning-loop.py session-start"}]}],
    "Stop": [{"hooks": [{"type": "command",
        "command": "python3 /path/to/steam-debugger/scripts/learning-loop.py stop"}]}]
  }

The same session may run two copies of this hook (user settings plus a
plugin's --settings); per-session state behind a file lock makes the second
one a no-op.
"""

import fcntl
import json
import os
import sys
import time

# Steam-related tool calls since the last review before the stop hook asks for
# one, and the most reviews per session. Short sessions stay untouched.
NUDGE_AFTER_CALLS = 6
MAX_NUDGES = 3

_STEAM_WORDS = (
    "steam", "proton", "gamescope", "compatdata", "wine", "decky", "plugin_loader",
    "mangohud", "gamemode", "pipewire", "radv", "amdgpu", "xdotool", "steam-debugger",
)


def _xdg(var: str, default: str) -> str:
    return os.environ.get(var) or os.path.join(os.path.expanduser("~"), default)


LEARNINGS = os.path.join(_xdg("XDG_DATA_HOME", ".local/share"), "steam-debugger", "learnings.md")
REPO_FILE = os.path.join(_xdg("XDG_CONFIG_HOME", ".config"), "steam-debugger", "repo")
STATE_DIR = os.path.join(_xdg("XDG_STATE_HOME", ".local/state"), "steam-debugger", "loop")

LEARNINGS_HEADER = """# steam-debugger — local learnings

Written by Claude through the steam-debugger learning loop. One entry per
finding, newest at the bottom. Status: confirmed (the user saw it work),
observed (Claude saw it in logs/output), unverified (plausible, not checked).
"""


def maintainer_skill_dir() -> str | None:
    """The skill directory of a writable git checkout, if this machine has one."""
    try:
        with open(REPO_FILE) as f:
            path = os.path.expanduser(f.readline().strip())
    except OSError:
        return None
    if not path or not os.path.isfile(os.path.join(path, "SKILL.md")):
        return None
    probe = path
    while probe != os.path.dirname(probe):
        if os.path.exists(os.path.join(probe, ".git")):
            return path if os.access(path, os.W_OK) else None
        probe = os.path.dirname(probe)
    return None


def is_steam_call(block: dict) -> bool:
    name = block.get("name") or ""
    if name.startswith("mcp__steamdeck__"):
        return True
    text = json.dumps(block.get("input") or {}).lower()
    return any(w in text for w in _STEAM_WORDS)


def count_steam_calls(transcript: str, start_line: int) -> tuple[int, int]:
    """Steam-related tool calls after `start_line`, and the transcript's line count."""
    calls = 0
    lines = 0
    with open(transcript, errors="replace") as f:
        for lines, raw in enumerate(f, 1):
            if lines <= start_line or '"tool_use"' not in raw:
                continue
            try:
                content = json.loads(raw).get("message", {}).get("content")
            except ValueError:
                continue
            if isinstance(content, list):
                calls += sum(1 for b in content
                             if isinstance(b, dict) and b.get("type") == "tool_use" and is_steam_call(b))
    return calls, lines


def with_state(session_id: str, fn):
    """Run fn(state) -> result under an exclusive per-session lock; persist state."""
    os.makedirs(STATE_DIR, exist_ok=True)
    safe = "".join(c for c in session_id if c.isalnum() or c in "-_") or "unknown"
    path = os.path.join(STATE_DIR, safe + ".json")
    with open(path, "a+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.seek(0)
        try:
            state = json.loads(f.read() or "{}")
        except ValueError:
            state = {}
        result = fn(state)
        f.seek(0)
        f.truncate()
        f.write(json.dumps(state))
        return result


def review_prompt(repo_skill: str | None) -> str:
    lines = [
        "[steam-debugger learning loop] Before you stop, review the Steam/game work since the last review.",
        "",
        f"1. Record locally in {LEARNINGS} (create it if missing; grep it first and update an entry instead of",
        "   duplicating it). One entry per real finding: a fix that worked, a documented fix that failed, a root",
        "   cause, a tool or game quirk, a dead end worth not repeating. Format:",
        "     ## YYYY-MM-DD — <symptom in a few words>",
        "     - Context: game/appid, distro, GPU, Gaming/Desktop Mode — only what you actually know",
        "     - Finding: what was tried and what happened",
        "     - Status: confirmed (the user said it works) | observed (you saw it in output/logs) | unverified",
        "     - Evidence: the command, log line or result that shows it",
        "   Write only what happened in this session. Never invent, generalise beyond the evidence or upgrade",
        "   the status; an honest 'unverified' beats a confident guess. Skip trivia. No secrets or personal data.",
    ]
    if repo_skill:
        lines += [
            "",
            f"2. Promote into the skill at {repo_skill} (a writable checkout on this machine): only findings that",
            "   are confirmed or reproduced, general (true beyond this one machine; machine-specific details stay",
            "   local) and not already covered. Put each in the reference file SKILL.md routes that symptom to, at",
            "   its fix tier (anecdotal fixes go to tribal.md with provenance, per its format). Keep the file's",
            "   style and length discipline. Commit and push to the default branch, following the repo's rules.",
        ]
    lines += [
        "",
        "If there is nothing new, do nothing. Either way tell the user at most one short line about what you",
        "recorded (or nothing at all), then stop.",
    ]
    return "\n".join(lines)


def on_stop(event: dict) -> None:
    if event.get("stop_hook_active"):
        return
    transcript = event.get("transcript_path")
    if not transcript or not os.path.isfile(transcript):
        return

    def decide(state: dict) -> bool:
        if state.get("nudges", 0) >= MAX_NUDGES:
            return False
        calls, lines = count_steam_calls(transcript, state.get("reviewed_line", 0))
        if calls < NUDGE_AFTER_CALLS:
            return False
        state["nudges"] = state.get("nudges", 0) + 1
        state["reviewed_line"] = lines
        return True

    if with_state(event.get("session_id", ""), decide):
        print(json.dumps({"decision": "block", "reason": review_prompt(maintainer_skill_dir())}))


def on_session_start(event: dict) -> None:
    def once(state: dict) -> bool:
        # A second copy of this hook in the same session start is a duplicate.
        if time.time() - state.get("started", 0) < 30:
            return False
        state["started"] = time.time()
        return True

    if not with_state(event.get("session_id", ""), once):
        return
    if not os.path.exists(LEARNINGS):
        os.makedirs(os.path.dirname(LEARNINGS), exist_ok=True)
        with open(LEARNINGS, "w") as f:
            f.write(LEARNINGS_HEADER)
    titles = []
    with open(LEARNINGS, errors="replace") as f:
        titles = [l[3:].strip() for l in f if l.startswith("## ")]
    text = (
        f"steam-debugger local learnings: {LEARNINGS} ({len(titles)} entries) holds what earlier sessions on "
        "this machine found while debugging Steam, Proton, gamescope and games. For that kind of work, grep it "
        "for the symptom before diagnosing from scratch."
    )
    if titles:
        text += "\nMost recent: " + "; ".join(titles[-8:])
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": text}}))


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    try:
        if sys.argv[1:] == ["stop"]:
            on_stop(event)
        elif sys.argv[1:] == ["session-start"]:
            on_session_start(event)
    except Exception as exc:  # a broken hook must never block the session
        print(f"learning-loop: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
