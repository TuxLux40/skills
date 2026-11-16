#!/usr/bin/env python3
"""Document index per note / Dokumenten-Index je Notiz.

For every note that declares an `id` (person, family), lists the files in
the archive whose file name carries that ID, and writes the list into the
note between <!-- BEGIN dokumente --> and <!-- END dokumente -->. Works with
any naming scheme that puts the ID into the file name as a separate token,
for example `1964-06-09_SCH-IRI_GBUR.pdf`. Python standard library only.

  * Dry run by default; nothing is written without --write.
  * Only the marked block is replaced. A note without markers gets a
    "Dokumente" section appended.
  * The list says how files were filed, not what they prove: an ID in a
    file name is an assignment made when filing.

Usage:
    python3 okf_docindex.py ARCHIVE_ROOT [--notes DIR ...] [--write]
        [--lang de|en] [--ignore GLOB ...]
"""
from __future__ import annotations

import argparse
import fnmatch
import os
import re
import sys
from collections import defaultdict

BEGIN, END = "<!-- BEGIN dokumente -->", "<!-- END dokumente -->"
DATE_RE = re.compile(r"^(\d{4}(?:-\d{2}){0,2}(?:-\d{4})?c?|\d{4}-\d{4}|nd)(?=[_.\-]|$)", re.I)

T = {
    "de": {
        "note": "Nach Dateinamen dieser ID zugeordnet – eine Zuordnung der Ablage, kein Beleg.",
        "cols": "| Datum | Datei | Ordner |", "none": "Keine Datei mit dieser ID im Dateinamen.",
        "heading": "## Dokumente", "undated": "o. D.",
        "update": "Index erneuern", "append": "Abschnitt anhängen", "same": "unverändert",
        "summary": "{n} Notizen mit ID · {f} Dateien zugeordnet · {u} Dateien ohne bekannte ID",
        "changes": "{c} Notizen zu ändern",
        "dry": "Probelauf – nichts geschrieben. Mit --write ausführen.",
        "unknown": "Kennungen ohne Notiz (Auswahl): {v}",
    },
    "en": {
        "note": "Assigned by the ID in the file name – how it was filed, not evidence.",
        "cols": "| Date | File | Folder |", "none": "No file carries this ID in its name.",
        "heading": "## Documents", "undated": "n.d.",
        "update": "renew index", "append": "append section", "same": "unchanged",
        "summary": "{n} notes with an ID · {f} files assigned · {u} files without a known ID",
        "changes": "{c} notes to change",
        "dry": "Dry run – nothing written. Run with --write.",
        "unknown": "Tokens without a note (sample): {v}",
    },
}


def frontmatter_id(path: str):
    try:
        head = open(path, encoding="utf-8").read(4000)
    except (OSError, UnicodeDecodeError):
        return None
    if not head.startswith("---"):
        return None
    block = head.split("\n---", 1)[0]
    m = re.search(r"^id:\s*[\"']?([^\"'\n#]+?)[\"']?\s*$", block, re.M)
    return m.group(1).strip() if m else None


def walk(root, ignore):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
        for name in sorted(filenames):
            rel = os.path.relpath(os.path.join(dirpath, name), root).replace(os.sep, "/")
            if name.startswith(".") or any(fnmatch.fnmatch(rel, g) or fnmatch.fnmatch(name, g) for g in ignore):
                continue
            yield rel


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("root")
    ap.add_argument("--notes", action="append", default=[],
                    help="folder(s) below the root that hold the notes; default: the whole root")
    ap.add_argument("--ignore", action="append", default=[], help="glob of files to leave out")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--lang", choices=("de", "en"), default="de")
    args = ap.parse_args()
    t = T[args.lang]
    root = args.root
    if not os.path.isdir(root):
        print(f"not a directory: {root}", file=sys.stderr)
        return 2

    files = list(walk(root, args.ignore))
    note_dirs = [d.strip("/") for d in args.notes]
    notes = {}  # id -> rel path
    for rel in files:
        if not rel.lower().endswith(".md"):
            continue
        if note_dirs and not any(rel.startswith(d + "/") for d in note_dirs):
            continue
        nid = frontmatter_id(os.path.join(root, rel))
        if nid:
            notes.setdefault(nid, rel)
    note_paths = set(notes.values())

    token = {nid: re.compile(r"(?<![0-9A-Za-zÀ-ÿ-])" + re.escape(nid) + r"(?![0-9A-Za-zÀ-ÿ-])") for nid in notes}
    assigned = defaultdict(list)
    unassigned = 0
    for rel in files:
        if rel in note_paths:
            continue
        name = os.path.basename(rel)
        hit = False
        for nid, rx in token.items():
            if rx.search(name):
                assigned[nid].append(rel)
                hit = True
        if not hit and not rel.lower().endswith(".md"):
            unassigned += 1

    changes = 0
    for nid, note_rel in sorted(notes.items()):
        note_abs = os.path.join(root, note_rel)
        rows = []
        for rel in sorted(assigned.get(nid, []), key=lambda r: (os.path.basename(r), r)):
            name = os.path.basename(rel)
            m = DATE_RE.match(name)
            date = m.group(1) if m and m.group(1).lower() != "nd" else t["undated"]
            target = os.path.relpath(os.path.join(root, rel), os.path.dirname(note_abs)).replace(os.sep, "/")
            target = target.replace(" ", "%20").replace("(", "%28").replace(")", "%29")
            folder = os.path.dirname(rel) or "."
            rows.append(f"| {date} | [{name.replace('|', '/')}]({target}) | {folder} |")
        if rows:
            body = [t["note"], "", t["cols"], "|---|---|---|"] + rows
        else:
            body = [t["none"]]
        block = "\n".join([BEGIN] + body + [END])

        old = open(note_abs, encoding="utf-8").read()
        if BEGIN in old and END in old:
            start, end = old.index(BEGIN), old.index(END) + len(END)
            if old[start:end] == block:
                continue
            new, action = old[:start] + block + old[end:], t["update"]
        else:
            if not rows:
                continue
            new, action = old.rstrip("\n") + f"\n\n{t['heading']}\n\n{block}\n", t["append"]
        changes += 1
        print(f"[{action}] {note_rel}: {len(rows)}")
        if args.write:
            with open(note_abs, "w", encoding="utf-8") as fh:
                fh.write(new)

    print(t["summary"].format(n=len(notes), f=sum(len(v) for v in assigned.values()), u=unassigned))
    print(t["changes"].format(c=changes))
    if not args.write:
        print(t["dry"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
