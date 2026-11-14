#!/usr/bin/env python3
"""GEDCOM plausibility check / GEDCOM-Plausibilitaetspruefung.

Read-only. Python standard library only. Flags items for human review:

  * chronological impossibilities (parent ages, events after death, ...)
  * facts without a source citation, and "sources" that are just other trees
  * possible duplicate individuals

A clean report means the file is internally consistent, not that it is correct.

Usage:
    python3 gedcom_plausi.py tree.ged [--lang de|en] [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import defaultdict
from datetime import date

MONTHS = {
    "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
    "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12,
    # German month abbreviations occasionally exported by tools
    "MAI": 5, "OKT": 10, "DEZ": 12, "MRZ": 3, "MÄR": 3,
}
APPROX = ("ABT", "EST", "CAL", "BEF", "AFT", "BET", "FROM", "TO", "INT")
EVENTS = ("BIRT", "CHR", "BAPM", "DEAT", "BURI", "MARR")
TREE_SOURCE_RE = re.compile(
    r"family\s*tree|stammb[aä]um|smart\s*match|geni\b|world\s*tree|"
    r"ancestry\s*member|onetree|gedbas|wikitree|familysearch\s*family\s*tree",
    re.I,
)

T = {
    "de": {
        "title": "GEDCOM-Plausibilitätsprüfung",
        "persons": "Personen", "families": "Familien", "findings": "Befunde",
        "none": "Keine Auffälligkeiten.",
        "note": "Hinweis: Ein sauberer Bericht bedeutet widerspruchsfrei, nicht richtig.",
        "ERROR": "FEHLER", "WARN": "WARNUNG", "INFO": "INFO",
        "death_before_birth": "Tod/Begräbnis vor Geburt/Taufe",
        "bapt_before_birth": "Taufe vor Geburt",
        "burial_before_death": "Begräbnis vor Tod",
        "lifespan": "Lebensdauer {n} Jahre",
        "mother_young": "Mutter bei Geburt von {c} erst {n} Jahre alt",
        "mother_old": "Mutter bei Geburt von {c} bereits {n} Jahre alt",
        "father_young": "Vater bei Geburt von {c} erst {n} Jahre alt",
        "father_old": "Vater bei Geburt von {c} bereits {n} Jahre alt",
        "born_after_mother_death": "Kind {c} nach Tod der Mutter geboren",
        "born_after_father_death": "Kind {c} mehr als 9 Monate nach Tod des Vaters geboren",
        "sibling_gap": "Geschwister {a} und {b} weniger als 9 Monate auseinander",
        "marr_young": "Heirat mit {n} Jahren",
        "marr_after_death": "Heirat nach dem Tod",
        "marr_before_birth": "Heirat vor der Geburt",
        "no_source": "Ohne Quellenangabe: {ev}",
        "tree_source": "Nur Stammbaum/Match als Quelle (kein Beleg): {ev}",
        "no_events": "Keine datierten Ereignisse",
        "duplicate": "Mögliches Duplikat von {o}",
        "bad_date": "Datum nicht interpretierbar: {ev} '{d}'",
        "multi_famc": "Mehreren Elternfamilien zugeordnet ({n})",
    },
    "en": {
        "title": "GEDCOM plausibility check",
        "persons": "Individuals", "families": "Families", "findings": "Findings",
        "none": "Nothing flagged.",
        "note": "Note: a clean report means consistent, not correct.",
        "ERROR": "ERROR", "WARN": "WARNING", "INFO": "INFO",
        "death_before_birth": "Death/burial before birth/baptism",
        "bapt_before_birth": "Baptism before birth",
        "burial_before_death": "Burial before death",
        "lifespan": "Lifespan of {n} years",
        "mother_young": "Mother only {n} at birth of {c}",
        "mother_old": "Mother already {n} at birth of {c}",
        "father_young": "Father only {n} at birth of {c}",
        "father_old": "Father already {n} at birth of {c}",
        "born_after_mother_death": "Child {c} born after mother's death",
        "born_after_father_death": "Child {c} born more than 9 months after father's death",
        "sibling_gap": "Siblings {a} and {b} less than 9 months apart",
        "marr_young": "Married at age {n}",
        "marr_after_death": "Marriage after death",
        "marr_before_birth": "Marriage before birth",
        "no_source": "No source citation: {ev}",
        "tree_source": "Only a tree/match cited (not evidence): {ev}",
        "no_events": "No dated events",
        "duplicate": "Possible duplicate of {o}",
        "bad_date": "Unparseable date: {ev} '{d}'",
        "multi_famc": "Child in several parent families ({n})",
    },
}


def read_text(path: str) -> str:
    raw = open(path, "rb").read()
    for enc in ("utf-8-sig", "utf-16", "cp1252", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeError:
            continue
    return raw.decode("latin-1", "replace")


def parse_date(value: str):
    """Return (ordinal_day, exact: bool) or None. Year-only dates use 1 July."""
    if not value:
        return None
    v = value.upper().strip()
    v = re.sub(r"@#D[A-Z ]+@", "", v).strip()  # calendar escapes
    exact = not any(v.startswith(a) or f" {a} " in f" {v} " for a in APPROX)
    v = re.sub(r"\b(" + "|".join(APPROX) + r"|AND)\b", " ", v)
    m = re.search(r"(?:(\d{1,2})\s+)?([A-ZÄ]{3})?\.?\s*(\d{3,4})(?:/\d{2})?", v)
    if not m:
        m2 = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{3,4})", value)  # 14.03.1788
        if not m2:
            return None
        d, mo, y = int(m2.group(1)), int(m2.group(2)), int(m2.group(3))
    else:
        d = int(m.group(1)) if m.group(1) else 0
        mo = MONTHS.get(m.group(2) or "", 0)
        y = int(m.group(3))
    if not d or not mo:
        exact = False
    try:
        return date(y, mo or 7, d or 1).toordinal(), exact
    except ValueError:
        try:
            return date(y, 7, 1).toordinal(), False
        except ValueError:
            return None


def norm_name(name: str) -> str:
    n = unicodedata.normalize("NFKD", name.replace("/", " ").lower())
    n = "".join(c for c in n if not unicodedata.combining(c))
    n = n.replace("ß", "ss")
    n = re.sub(r"ae", "a", n)
    n = re.sub(r"oe", "o", n)
    n = re.sub(r"ue", "u", n)
    n = re.sub(r"(th)", "t", n)
    n = re.sub(r"(ck|k)", "c", n)
    n = re.sub(r"(dt|tt|tz|ts)\b", "t", n)
    n = re.sub(r"[yj]", "i", n)
    n = re.sub(r"[ae]i", "e", n)  # Heinrich/Henrich, Meier/Maier/Meyer
    n = re.sub(r"(.)\1", r"\1", n)
    return " ".join(sorted(re.findall(r"[a-z]+", n)))


def parse(path: str):
    indi, fam, sources = {}, {}, {}
    rec = None
    kind = None
    stack = []  # (level, tag)
    cur_event = None
    for line in read_text(path).splitlines():
        m = re.match(r"\s*(\d+)\s+(?:(@[^@]+@)\s+)?(\S+)(?:\s(.*))?$", line)
        if not m:
            continue
        level, xref, tag, val = int(m.group(1)), m.group(2), m.group(3).upper(), (m.group(4) or "").strip()
        if level == 0:
            cur_event = None
            if tag == "INDI":
                kind = "I"
                rec = indi.setdefault(xref, {"id": xref, "name": "", "sex": "", "ev": {}, "famc": [], "fams": [], "src": False})
            elif tag == "FAM":
                kind = "F"
                rec = fam.setdefault(xref, {"id": xref, "husb": None, "wife": None, "chil": [], "ev": {}})
            elif tag == "SOUR" and xref:
                kind = "S"
                rec = sources.setdefault(xref, {"title": ""})
            else:
                kind, rec = None, None
            continue
        if rec is None:
            continue
        stack = [s for s in stack if s[0] < level] + [(level, tag)]
        if kind == "S":
            if tag in ("TITL", "ABBR", "AUTH", "PUBL") and level == 1:
                rec["title"] += " " + val
            continue
        if level == 1:
            cur_event = None
            if tag in EVENTS:
                cur_event = rec["ev"].setdefault(tag, {"date": "", "plac": "", "src": []})
            elif kind == "I" and tag == "NAME" and not rec["name"]:
                rec["name"] = val
            elif kind == "I" and tag == "SEX":
                rec["sex"] = val[:1].upper()
            elif kind == "I" and tag == "FAMC":
                rec["famc"].append(val)
            elif kind == "I" and tag == "FAMS":
                rec["fams"].append(val)
            elif kind == "I" and tag == "SOUR":
                rec["src"] = True
            elif kind == "F" and tag == "HUSB":
                rec["husb"] = val
            elif kind == "F" and tag == "WIFE":
                rec["wife"] = val
            elif kind == "F" and tag == "CHIL":
                rec["chil"].append(val)
        elif level == 2 and cur_event is not None:
            if tag == "DATE" and not cur_event["date"]:
                cur_event["date"] = val
            elif tag == "PLAC" and not cur_event["plac"]:
                cur_event["plac"] = val
            elif tag == "SOUR":
                cur_event["src"].append(val)
    return indi, fam, sources


def years(a: int, b: int) -> int:
    return int((b - a) / 365.25)


def check(indi, fam, sources):
    out = []  # (severity, id, name, key, params)

    def add(sev, p, key, **kw):
        out.append({"severity": sev, "id": p["id"], "name": p.get("name", "").replace("/", "").strip(), "key": key, "params": kw})

    dates = {}
    for pid, p in indi.items():
        d = {}
        for ev, e in p["ev"].items():
            if e["date"]:
                parsed = parse_date(e["date"])
                if parsed is None:
                    add("INFO", p, "bad_date", ev=ev, d=e["date"])
                else:
                    d[ev] = parsed
        dates[pid] = d
        birth = d.get("BIRT") or d.get("CHR") or d.get("BAPM")
        death = d.get("DEAT") or d.get("BURI")
        p["_b"], p["_d"] = birth, death

        if birth and death:
            if death[0] < birth[0] - (0 if birth[1] and death[1] else 366):
                add("ERROR", p, "death_before_birth")
            elif years(birth[0], death[0]) > 105:
                add("WARN", p, "lifespan", n=years(birth[0], death[0]))
        if "BIRT" in d:
            for b in ("CHR", "BAPM"):
                if b in d and d[b][1] and d["BIRT"][1] and d[b][0] < d["BIRT"][0]:
                    add("ERROR", p, "bapt_before_birth")
        if "DEAT" in d and "BURI" in d and d["DEAT"][1] and d["BURI"][1] and d["BURI"][0] < d["DEAT"][0]:
            add("ERROR", p, "burial_before_death")

        # sourcing
        if not p["ev"]:
            add("INFO", p, "no_events")
        for ev, e in p["ev"].items():
            if not e["src"] and not p["src"]:
                add("WARN", p, "no_source", ev=ev)
            elif e["src"]:
                titles = [sources.get(s, {}).get("title", s) for s in e["src"]]
                if all(TREE_SOURCE_RE.search(t or "") for t in titles):
                    add("WARN", p, "tree_source", ev=ev)

        if len(p["famc"]) > 1:
            add("INFO", p, "multi_famc", n=len(p["famc"]))


    for f in fam.values():
        father, mother = indi.get(f["husb"]), indi.get(f["wife"])
        marr = parse_date(f["ev"].get("MARR", {}).get("date", "")) if "MARR" in f["ev"] else None
        for sp in (father, mother):
            if sp and marr:
                if sp["_b"] and marr[0] < sp["_b"][0]:
                    add("ERROR", sp, "marr_before_birth")
                elif sp["_b"] and years(sp["_b"][0], marr[0]) < 14:
                    add("WARN", sp, "marr_young", n=years(sp["_b"][0], marr[0]))
                if sp["_d"] and marr[0] > sp["_d"][0] + 366:
                    add("ERROR", sp, "marr_after_death")
        kids = []
        for cid in f["chil"]:
            c = indi.get(cid)
            if not c or not c["_b"]:
                continue
            cb = c["_b"][0]
            cname = c["name"].replace("/", "").strip() or cid
            kids.append((cb, c["_b"][1], cname))
            if mother:
                if mother["_b"]:
                    n = years(mother["_b"][0], cb)
                    if n < 15:
                        add("ERROR" if n < 12 else "WARN", mother, "mother_young", n=n, c=cname)
                    elif n > 50:
                        add("ERROR" if n > 55 else "WARN", mother, "mother_old", n=n, c=cname)
                if mother["_d"] and cb > mother["_d"][0] + (0 if mother["_d"][1] and c["_b"][1] else 366):
                    add("ERROR", mother, "born_after_mother_death", c=cname)
            if father:
                if father["_b"]:
                    n = years(father["_b"][0], cb)
                    if n < 15:
                        add("ERROR" if n < 12 else "WARN", father, "father_young", n=n, c=cname)
                    elif n > 75:
                        add("WARN", father, "father_old", n=n, c=cname)
                if father["_d"] and cb > father["_d"][0] + 280 + (0 if father["_d"][1] and c["_b"][1] else 366):
                    add("ERROR", father, "born_after_father_death", c=cname)
        kids.sort()
        for (a, ae, an), (b, be, bn) in zip(kids, kids[1:]):
            if ae and be and 2 < b - a < 270:
                anchor = mother or father or {"id": f["id"], "name": ""}
                add("WARN", anchor, "sibling_gap", a=an, b=bn)

    # duplicates: same normalised name + birth year within 1
    buckets = defaultdict(list)
    for p in indi.values():
        if p["name"] and p["_b"]:
            buckets[norm_name(p["name"])].append(p)
    for group in buckets.values():
        group.sort(key=lambda p: p["_b"][0])
        for a, b in zip(group, group[1:]):
            if abs(a["_b"][0] - b["_b"][0]) <= 366 and a["id"] != b["id"]:
                # same-named siblings (Nachbenennung) are expected: only flag
                # when they do not share a parent family
                if not set(a["famc"]) & set(b["famc"]):
                    add("WARN", b, "duplicate", o=f"{a['id']} {a['name'].replace('/', '').strip()}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("gedcom")
    ap.add_argument("--lang", choices=("de", "en"), default="de")
    ap.add_argument("--json", action="store_true", help="machine-readable output (stable for diffing)")
    args = ap.parse_args()

    indi, fam, sources = parse(args.gedcom)
    findings = check(indi, fam, sources)
    order = {"ERROR": 0, "WARN": 1, "INFO": 2}
    findings.sort(key=lambda f: (order[f["severity"]], f["id"], f["key"], json.dumps(f["params"], sort_keys=True)))

    if args.json:
        json.dump({"individuals": len(indi), "families": len(fam), "findings": findings}, sys.stdout, ensure_ascii=False, indent=1)
        print()
    else:
        t = T[args.lang]
        print(f"{t['title']}: {args.gedcom}")
        print(f"{t['persons']}: {len(indi)}  {t['families']}: {len(fam)}  {t['findings']}: {len(findings)}")
        counts = defaultdict(int)
        for f in findings:
            counts[f["severity"]] += 1
        print("  ".join(f"{t[s]}: {counts[s]}" for s in ("ERROR", "WARN", "INFO")))
        print()
        if not findings:
            print(t["none"])
        for f in findings:
            print(f"[{t[f['severity']]}] {f['id']} {f['name']}: {t[f['key']].format(**f['params'])}")
        print()
        print(t["note"])
    return 1 if any(f["severity"] == "ERROR" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
