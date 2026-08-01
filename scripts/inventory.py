#!/usr/bin/env python3
"""Inventarisiert einen Ordner: listet Dateien mit Größe, Datum, Endung.
Rein lesend - macht keine Änderungen. Dient als Grundlage, bevor eine
Ablagestruktur vorgeschlagen wird.

Usage: python3 inventory.py <verzeichnis> [--json]
"""
import sys
import os
import json
import datetime

def scan(root):
    entries = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for name in filenames:
            path = os.path.join(dirpath, name)
            try:
                stat = os.stat(path)
            except OSError:
                continue
            rel = os.path.relpath(path, root)
            ext = os.path.splitext(name)[1].lower().lstrip(".")
            mtime = datetime.datetime.fromtimestamp(stat.st_mtime).date().isoformat()
            entries.append({
                "path": rel,
                "ext": ext,
                "size_kb": round(stat.st_size / 1024, 1),
                "modified": mtime,
            })
    return entries

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    root = sys.argv[1]
    as_json = "--json" in sys.argv[2:]
    entries = sorted(scan(root), key=lambda e: e["path"])

    if as_json:
        print(json.dumps(entries, ensure_ascii=False, indent=2))
        return

    by_ext = {}
    for e in entries:
        by_ext.setdefault(e["ext"] or "(ohne Endung)", []).append(e)

    print(f"Gesamt: {len(entries)} Dateien in {root}\n")
    print("Nach Dateityp:")
    for ext, items in sorted(by_ext.items(), key=lambda kv: -len(kv[1])):
        total_kb = sum(i["size_kb"] for i in items)
        print(f"  .{ext:<8} {len(items):>4} Dateien  ({total_kb/1024:.1f} MB)")

    print("\nAlle Dateien:")
    for e in entries:
        print(f"  {e['modified']}  {e['size_kb']:>9.1f} KB  {e['path']}")

if __name__ == "__main__":
    main()
