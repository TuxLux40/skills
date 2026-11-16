#!/usr/bin/env python3
"""OKF note check / Pruefung der OKF-Notizen.

Read-only. Python standard library only. Walks a folder of Markdown notes
written in the genealogy skill's OKF form (YAML frontmatter with `type`,
relative Markdown links) and reports what makes the bundle non-conformant,
the link graph misleading, or a conclusion rest on an unchecked reading:

  * notes without frontmatter or without `type`
  * duplicate IDs, IDs missing from the file name, unknown `conclusion` /
    `status` values
  * persons or families in the tree with a conclusion below "wahrscheinlich"
    ("ungeprüft" - taken over from the tree, not evaluated - is counted,
    not flagged)
  * wikilinks, absolute links, links to files that do not exist
  * direct person-to-person links (kinship belongs in a Family note)
  * a line that says "belegt" but cites a reading no human has checked
  * person links out of an unchecked reading of handwriting

A clean report means the notes are consistent, not that they are correct.

Usage:
    python3 okf_check.py <bundle-root> [--lang de|en] [--json]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from urllib.parse import unquote

TYPES = {
    "Person", "Family", "Place", "Source", "Hypothesis", "Proof",
    "ResearchLog", "Session", "Register",
}
NEEDS_ID = {"Person", "Family"}
CONCLUSION_EN = {
    "proven": "belegt", "probable": "wahrscheinlich", "possible": "möglich",
    "unresolved": "ungeklärt", "disproven": "widerlegt",
}
CONCLUSION_EN["unreviewed"] = "ungeprüft"
CONCLUSIONS = set(CONCLUSION_EN.values())
TREE_OK = {"belegt", "wahrscheinlich", "ungeprüft"}
NEEDS_CONCLUSION = {"Person", "Family", "Hypothesis", "Proof"}
LIFECYCLE = {"draft", "stable", "deprecated"}
RESERVED = {"index.md", "log.md"}

KEY_RE = re.compile(r"^([A-Za-z_][\w-]*):\s*(.*)$")
FENCE_RE = re.compile(r"^(\s*)(```|~~~)")
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
LINK_RE = re.compile(r"(!?)\[([^\]]*)\]\(\s*(<[^>]+>|[^)\s]+)(?:\s+\"[^\"]*\")?\s*\)")
WIKI_RE = re.compile(r"\[\[[^\]\n]+\]\]")
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
PROVEN_RE = re.compile(r"(?<![\wäöüÄÖÜß])(belegt|proven)(?![\wäöüÄÖÜß])")
HAND_RE = re.compile(r"kurrent|s[uü]e?tterlin|handschrift|handwrit|fraktur", re.I)

T = {
    "de": {
        "ERROR": "FEHLER", "WARN": "WARNUNG", "INFO": "HINWEIS",
        "no_frontmatter": "Kein Frontmatter – für OKF braucht jede Notiz einen Block mit `type`",
        "no_type": "Frontmatter ohne `type`",
        "unknown_type": "Unbekannter `type` {v!r} (zulässig, aber außerhalb des Skill-Vokabulars)",
        "reserved_frontmatter": "{name} ist ein reservierter Name und trägt kein Frontmatter (Ausnahme: `okf_version` in der index.md der Wurzel)",
        "dup_id": "ID {v} mehrfach vergeben: {others}",
        "id_not_in_name": "Dateiname enthält die ID {v} nicht",
        "no_id": "{t} ohne `id`",
        "bad_conclusion": "`conclusion` {v!r} gehört nicht zum Status-Vokabular",
        "no_conclusion": "{t} ohne `conclusion`",
        "weak_in_tree": "{t} mit conclusion {v!r}: unterhalb von 'wahrscheinlich' gehört das in eine Hypothese, nicht in den Baum",
        "bad_status": "`status` {v!r} ist kein OKF-Lebenszyklus (draft, stable, deprecated)",
        "status_is_conclusion": "`status` {v!r} ist ein Beweisstatus – dafür ist `conclusion` da",
        "wikilink": "{n} Wikilink(s) – nur Markdown-Links sind portabel",
        "abs_link": "Zeile {line}: absoluter Link {v!r} – relativen Pfad verwenden",
        "broken_link": "Zeile {line}: Linkziel fehlt: {v}",
        "missing_file": "Zeile {line}: Datei fehlt: {v}",
        "person_to_person": "Zeile {line}: direkter Link Person → Person ({v}); Verwandtschaft gehört in eine Familien-Notiz, 'nicht identisch mit' als reiner Text",
        "belegt_on_unverified": "Zeile {line}: 'belegt' stützt sich auf eine ungeprüfte Lesung ({v})",
        "hand_link": "Zeile {line}: Link auf {v} aus einer ungeprüften Lesung von {script} – wer genannt ist, steht erst nach Prüfung am Bild fest",
        "unverified_source": "Lesung nicht von einem Menschen am Bild geprüft",
        "summary": "{n} Notizen · {types}",
        "trust": "Quellen: {h} von Menschen geprüft, {u} ungeprüft",
        "tree": "Baum (Personen und Familien): {v}",
        "counts": "{e} Fehler, {w} Warnungen, {i} Hinweise",
        "clean": "Hinweis: Ein sauberer Bericht bedeutet widerspruchsfrei, nicht richtig.",
    },
    "en": {
        "ERROR": "ERROR", "WARN": "WARNING", "INFO": "NOTE",
        "no_frontmatter": "No frontmatter – OKF needs a block with `type` on every note",
        "no_type": "Frontmatter without `type`",
        "unknown_type": "Unknown `type` {v!r} (allowed, but outside the skill's vocabulary)",
        "reserved_frontmatter": "{name} is a reserved name and carries no frontmatter (exception: `okf_version` in the root index.md)",
        "dup_id": "ID {v} used more than once: {others}",
        "id_not_in_name": "File name does not contain the ID {v}",
        "no_id": "{t} without `id`",
        "bad_conclusion": "`conclusion` {v!r} is not in the status vocabulary",
        "no_conclusion": "{t} without `conclusion`",
        "weak_in_tree": "{t} with conclusion {v!r}: below 'wahrscheinlich' this belongs in a hypothesis, not in the tree",
        "bad_status": "`status` {v!r} is not an OKF lifecycle value (draft, stable, deprecated)",
        "status_is_conclusion": "`status` {v!r} is a proof status – use `conclusion` for it",
        "wikilink": "{n} wikilink(s) – only Markdown links are portable",
        "abs_link": "line {line}: absolute link {v!r} – use a relative path",
        "broken_link": "line {line}: link target missing: {v}",
        "missing_file": "line {line}: file missing: {v}",
        "person_to_person": "line {line}: direct link person → person ({v}); kinship belongs in a Family note, 'not identical with' as plain text",
        "belegt_on_unverified": "line {line}: 'belegt' rests on a reading nobody has checked ({v})",
        "hand_link": "line {line}: link to {v} out of an unchecked reading of {script} – who is named is settled only after checking the image",
        "unverified_source": "Reading not checked against the image by a human",
        "summary": "{n} notes · {types}",
        "trust": "Sources: {h} human-reviewed, {u} unchecked",
        "tree": "Tree (persons and families): {v}",
        "counts": "{e} errors, {w} warnings, {i} notes",
        "clean": "Note: a clean report means consistent, not correct.",
    },
}


def parse_frontmatter(text: str):
    """Return (dict of top-level keys -> raw value, body, body line offset)."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, text, 0
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            break
    else:
        return None, text, 0
    data: dict[str, str] = {}
    key = None
    for ln in lines[1:i]:
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        m = KEY_RE.match(ln)
        if m and not ln.startswith((" ", "\t")):
            key = m.group(1)
            data[key] = m.group(2).strip()
        elif key is not None:
            data[key] += "\n" + ln.rstrip()
    return data, "\n".join(lines[i + 1:]), i + 1


def scalar(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if " #" in value and not value.startswith(('"', "'")):
        value = value.split(" #", 1)[0].strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return value or None


def body_lines(body: str):
    """Yield (line_no, text) with fenced code removed and inline code blanked."""
    fence = None
    for no, ln in enumerate(body.split("\n"), 1):
        m = FENCE_RE.match(ln)
        if m:
            fence = None if fence == m.group(2) else (fence or m.group(2))
            continue
        if fence:
            continue
        yield no, INLINE_CODE_RE.sub("", ln)


def scan(root: str):
    notes = {}
    findings = []

    def add(sev, code, path, line=None, **kw):
        findings.append({"severity": sev, "code": code, "file": path, "line": line, "args": kw})

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith(".") and d != "node_modules")
        for name in sorted(filenames):
            if not name.lower().endswith(".md"):
                continue
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            try:
                with open(full, encoding="utf-8") as fh:
                    text = fh.read()
            except (OSError, UnicodeDecodeError):
                continue
            fm, body, offset = parse_frontmatter(text)
            if name in RESERVED:
                allowed = name == "index.md" and "/" not in rel and set(fm or {}) <= {"okf_version"}
                if fm and not allowed:
                    add("WARN", "reserved_frontmatter", rel, name=name)
                continue
            if fm is None:
                add("WARN", "no_frontmatter", rel)
                continue
            ntype = scalar(fm.get("type"))
            if not ntype:
                add("ERROR", "no_type", rel)
                continue
            verified = fm.get("verified", "")
            note = {
                "type": ntype,
                "id": scalar(fm.get("id")),
                "conclusion": scalar(fm.get("conclusion")),
                "status": scalar(fm.get("status")),
                "human": "human:" in verified,
                "script": scalar(fm.get("script")) or "",
                "links": [],
                "wikilinks": 0,
            }
            for no, ln in body_lines(body):
                note["wikilinks"] += len(WIKI_RE.findall(ln))
                for m in LINK_RE.finditer(ln):
                    target = m.group(3).strip("<>")
                    if SCHEME_RE.match(target) or target.startswith("#"):
                        continue
                    target = unquote(target.split("#", 1)[0])
                    if not target:
                        continue
                    absolute = target.startswith("/")
                    base = "" if absolute else os.path.dirname(rel)
                    resolved = os.path.normpath(os.path.join(base, target.lstrip("/"))).replace(os.sep, "/")
                    note["links"].append({
                        "line": no + offset, "raw": m.group(3), "target": resolved,
                        "image": bool(m.group(1)), "absolute": absolute, "text": ln,
                    })
            notes[rel] = note

    by_id = defaultdict(list)
    for rel, n in notes.items():
        if n["id"]:
            by_id[n["id"]].append(rel)

    for rel, n in sorted(notes.items()):
        t = n["type"]
        if t not in TYPES:
            add("INFO", "unknown_type", rel, v=t)
        if t in NEEDS_ID and not n["id"]:
            add("WARN", "no_id", rel, t=t)
        if n["id"] and t in NEEDS_ID | {"Hypothesis", "Proof"}:
            token = r"(?<![0-9A-Za-zÀ-ÿ-])" + re.escape(n["id"]) + r"(?![0-9A-Za-zÀ-ÿ-])"
            if not re.search(token, os.path.basename(rel)[:-3]):
                add("WARN", "id_not_in_name", rel, v=n["id"])
        if n["id"] and len(by_id[n["id"]]) > 1:
            others = ", ".join(p for p in by_id[n["id"]] if p != rel)
            add("ERROR", "dup_id", rel, v=n["id"], others=others)

        concl = n["conclusion"]
        if concl:
            concl = CONCLUSION_EN.get(concl.lower(), concl.lower())
            if concl not in CONCLUSIONS:
                add("ERROR", "bad_conclusion", rel, v=n["conclusion"])
            elif t in ("Person", "Family") and concl not in TREE_OK:
                add("WARN", "weak_in_tree", rel, t=t, v=n["conclusion"])
        elif t in NEEDS_CONCLUSION:
            add("WARN", "no_conclusion", rel, t=t)

        status = n["status"]
        if status and status.lower() not in LIFECYCLE:
            norm = CONCLUSION_EN.get(status.lower(), status.lower())
            code = "status_is_conclusion" if norm in CONCLUSIONS else "bad_status"
            add("WARN", code, rel, v=status)

        if n["wikilinks"]:
            add("WARN", "wikilink", rel, n=n["wikilinks"])

        for link in n["links"]:
            if link["absolute"]:
                add("WARN", "abs_link", rel, link["line"], v=link["raw"])
            target = notes.get(link["target"])
            if target is None:
                if not os.path.exists(os.path.join(root, link["target"])):
                    code = "broken_link" if link["target"].lower().endswith(".md") else "missing_file"
                    add("WARN", code, rel, link["line"], v=link["target"])
                continue
            if t == "Person" and target["type"] == "Person":
                add("WARN", "person_to_person", rel, link["line"], v=link["target"])
            if (t in ("Person", "Family") and target["type"] == "Source"
                    and not target["human"] and PROVEN_RE.search(link["text"])):
                add("WARN", "belegt_on_unverified", rel, link["line"], v=link["target"])
            if (t == "Source" and not n["human"] and HAND_RE.search(n["script"])
                    and target["type"] in ("Person", "Family")):
                add("WARN", "hand_link", rel, link["line"], v=link["target"], script=n["script"])

        if t == "Source" and not n["human"]:
            add("INFO", "unverified_source", rel)

    sources = [n for n in notes.values() if n["type"] == "Source"]
    tree = Counter()
    for n in notes.values():
        if n["type"] in ("Person", "Family"):
            c = (n["conclusion"] or "").lower()
            tree[CONCLUSION_EN.get(c, c) or "–"] += 1
    summary = {
        "notes": len(notes),
        "types": dict(sorted(Counter(n["type"] for n in notes.values()).items())),
        "tree": dict(tree.most_common()),
        "sources_human_reviewed": sum(1 for n in sources if n["human"]),
        "sources_unchecked": sum(1 for n in sources if not n["human"]),
    }
    order = {"ERROR": 0, "WARN": 1, "INFO": 2}
    findings.sort(key=lambda f: (order[f["severity"]], f["file"], f["line"] or 0))
    return summary, findings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("root")
    ap.add_argument("--lang", choices=("de", "en"), default="de")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if not os.path.isdir(args.root):
        print(f"not a directory: {args.root}", file=sys.stderr)
        return 2

    summary, findings = scan(args.root)
    t = T[args.lang]
    for f in findings:
        f["message"] = t[f["code"]].format(line=f["line"], **f.pop("args"))
    counts = Counter(f["severity"] for f in findings)

    if args.json:
        print(json.dumps({"summary": summary, "findings": findings}, ensure_ascii=False, indent=2))
    else:
        types = ", ".join(f"{k} {v}" for k, v in summary["types"].items())
        print(t["summary"].format(n=summary["notes"], types=types))
        print(t["trust"].format(h=summary["sources_human_reviewed"], u=summary["sources_unchecked"]))
        if summary["tree"]:
            print(t["tree"].format(v=" · ".join(f"{v} {k}" for k, v in summary["tree"].items())))
        print()
        for f in findings:
            print(f"[{t[f['severity']]}] {f['file']}: {f['message']}")
        if findings:
            print()
        print(t["counts"].format(e=counts["ERROR"], w=counts["WARN"], i=counts["INFO"]))
        print(t["clean"])
    return 1 if counts["ERROR"] else 0


if __name__ == "__main__":
    sys.exit(main())
