#!/usr/bin/env python3
"""Minimal iFixit API v2.0 client (stdlib only).

Usage:
  ifixit.py suggest "thinkcentre"              # resolve device names
  ifixit.py search "pixel 8 battery" [-n 10]   # find guides
  ifixit.py device "Google Pixel 8"            # device page: guides, children, score
  ifixit.py guide 166180 [--lang de]           # full guide as Markdown
  add --json to any command for raw JSON

Read-only, no API key needed. Respects HTTPS_PROXY / SSL_CERT_FILE env vars.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

BASE = "https://www.ifixit.com/api/2.0"
UA = "ifixit-skill/1.0 (+https://github.com/TuxLux40/skills)"
BULLET_FLAG = {
    "icon_caution": "⚠️ CAUTION",
    "icon_reminder": "🔁 REMINDER",
    "icon_note": "ℹ️ NOTE",
}


def get(path: str, **params: Any) -> Any:
    qs = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    url = f"{BASE}{path}" + (f"?{qs}" if qs else "")
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} for {url}")
    except urllib.error.URLError as e:
        sys.exit(f"Network error for {url}: {e.reason}\n"
                 "Hint: if a proxy blocks ifixit.com, fetch the same URL with a web-scrape tool.")


def q(s: str) -> str:
    return urllib.parse.quote(s, safe="")


def strip_markup(s: str) -> str:
    # iFixit raw text uses [link|...] and [guide|id|text] wiki markup; keep the label.
    s = re.sub(r"\[(?:link|guide|product)\|[^|\]]*\|([^\]]*)\]", r"\1", s)
    s = re.sub(r"\[(?:link|guide|product)\|([^\]]*)\]", r"\1", s)
    # MediaWiki leftovers: [[Link|Text]] -> Text, [[Text]] -> Text
    s = re.sub(r"\[\[(?:[^\]]+\|)?([^\]]+)\]\]", r"\1", s)
    return s.replace("''", "")


def minutes(sec: Any) -> str:
    try:
        m = int(sec) // 60
    except (TypeError, ValueError):
        return "?"
    return f"{m // 60}h{m % 60:02d}m" if m >= 60 else f"{m}m"


def cmd_suggest(a: argparse.Namespace) -> Any:
    data = get(f"/suggest/{q(a.query)}", doctypes="device")
    if a.json:
        return data
    rows = data.get("results", [])
    if not rows:
        print("No devices. Try fewer words, or the manufacturer + series only.")
    for r in rows:
        print(f"- {r.get('display_title') or r.get('title')}  →  {r.get('url')}")
        if r.get("summary"):
            print(f"    {r['summary'][:140]}")
    return None


def cmd_search(a: argparse.Namespace) -> Any:
    data = get(f"/search/{q(a.query)}", filter="guide", limit=a.n)
    if a.json:
        return data
    rows = data.get("results", [])
    print(f"{data.get('totalResults', 0)} guide(s) for '{a.query}'")
    for r in rows:
        star = "★ " if "GUIDE_STARRED" in (r.get("flags") or []) else ""
        print(f"- {star}[{r.get('guideid')}] {r.get('title')} — {r.get('difficulty')}, "
              f"≤{minutes(r.get('time_required_max'))}  ({r.get('category')})")
        print(f"    {r.get('url')}")
    if not rows:
        print("Nothing. Run `suggest` to get the canonical device title, then retry.")
    return None


def cmd_device(a: argparse.Namespace) -> Any:
    data = get(f"/wikis/CATEGORY/{q(a.title)}")
    if a.json:
        return data
    print(f"# {data.get('display_title') or data.get('title')}")
    anc = data.get("ancestors") or []
    if anc:
        print("Ancestors: " + " · ".join(str(x) for x in anc))
    score = data.get("repairability_score")
    if score:
        print(f"Repairability score: {score}")
    if data.get("description"):
        print(f"\n{data['description']}")
    guides = data.get("guides") or []
    print(f"\n## Guides ({len(guides)})")
    for g in guides:
        print(f"- [{g.get('guideid')}] {g.get('title')} — {g.get('difficulty', '?')}  {g.get('url', '')}")
    if not guides:
        print("(none — see references/fallbacks.md)")
    children = data.get("children") or []
    if children:
        print(f"\n## Child models ({len(children)})")
        for c in children:
            print(f"- {c.get('display_title') or c.get('title') if isinstance(c, dict) else c}")
    sols = data.get("solutions_url")
    if sols:
        print(f"\nTroubleshooting / Answers: {sols}")
    return None


def cmd_guide(a: argparse.Namespace) -> Any:
    data = get(f"/guides/{int(a.guideid)}", langid=a.lang)
    if a.json:
        return data
    out = [f"# {data.get('title')}",
           f"Source: {data.get('url')}  (iFixit, CC BY-NC-SA)",
           f"Device: {data.get('category')} · Difficulty: {data.get('difficulty')} · "
           f"Time: {data.get('time_required') or minutes(data.get('time_required_max'))}"]
    if data.get("introduction_raw"):
        out += ["", strip_markup(data["introduction_raw"]).strip()]
    prereq = data.get("prerequisites") or []
    if prereq:
        out += ["", "## Prerequisites (do these first)"]
        out += [f"- [{p.get('guideid')}] {p.get('title')}  {p.get('url', '')}" for p in prereq]
    for key, label in (("tools", "Tools"), ("parts", "Parts")):
        items = data.get(key) or []
        if items:
            out += ["", f"## {label}"]
            for t in items:
                opt = " (optional)" if t.get("isoptional") else ""
                qty = f"{t.get('quantity')}× " if t.get("quantity") not in (None, 1, "1") else ""
                note = f" — {t['notes']}" if t.get("notes") else ""
                out.append(f"- {qty}{t.get('text')}{opt}{note}")
    out += ["", "## Steps"]
    for i, s in enumerate(data.get("steps") or [], 1):
        title = s.get("title") or ""
        out.append(f"\n### {i}. {title}".rstrip(". ") if title else f"\n### {i}.")
        for ln in s.get("lines") or []:
            indent = "  " * int(ln.get("level") or 0)
            flag = BULLET_FLAG.get(ln.get("bullet") or "")
            text = strip_markup(ln.get("text_raw") or "")
            out.append(f"{indent}- {flag + ': ' if flag else ''}{text}")
    if data.get("conclusion_raw"):
        out += ["", "## Conclusion", strip_markup(data["conclusion_raw"]).strip()]
    print("\n".join(out))
    return None


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", help="print raw API JSON")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("suggest", parents=[common]); s.add_argument("query"); s.set_defaults(fn=cmd_suggest)
    s = sub.add_parser("search", parents=[common]); s.add_argument("query")
    s.add_argument("-n", type=int, default=10); s.set_defaults(fn=cmd_search)
    s = sub.add_parser("device", parents=[common]); s.add_argument("title"); s.set_defaults(fn=cmd_device)
    s = sub.add_parser("guide", parents=[common]); s.add_argument("guideid")
    s.add_argument("--lang", default=None, help="langid, e.g. de")
    s.set_defaults(fn=cmd_guide)
    a = p.parse_args(argv)
    res = a.fn(a)
    if res is not None:
        json.dump(res, sys.stdout, indent=2, ensure_ascii=False)
        print()


if __name__ == "__main__":
    main()
