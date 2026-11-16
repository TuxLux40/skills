#!/usr/bin/env python3
"""GEDCOM -> OKF notes / GEDCOM -> OKF-Notizen.

Writes one Markdown note per person and per family from a GEDCOM export:
vital data, relationships, citations and notes as the tree has them. The
data is copied by rule, never retyped. Python standard library only.

  * Dry run by default; nothing is written without --write.
  * An existing note is never overwritten. With --update only the block
    between <!-- BEGIN gedcom --> and <!-- END gedcom --> is replaced;
    frontmatter and everything outside the block stay as they are.
  * A fact carries the status found as a prefix in its citation or note
    ([belegt], [wahrscheinlich] ...). Without one it is "ungeprüft":
    taken over from the tree, not evaluated.

Usage:
    python3 gedcom_to_okf.py tree.ged --root NOTES_ROOT [--write] [--update]
        [--persons-dir DIR] [--families-dir DIR] [--id-map FILE]
        [--lang de|en] [--by ACTOR] [--no-chart]
    python3 gedcom_to_okf.py tree.ged --list-ids      # xref;name;born;died
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys

MONTHS = {
    "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6, "JUL": 7,
    "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12,
    "MAI": 5, "OKT": 10, "DEZ": 12, "MRZ": 3, "MÄR": 3,
}
INDI_EVENTS = [
    "BIRT", "CHR", "BAPM", "CONF", "EDUC", "OCCU", "RELI", "RESI", "NATI",
    "EMIG", "IMMI", "NATU", "CENS", "TITL", "EVEN", "FACT", "DEAT", "BURI", "CREM",
]
FAM_EVENTS = ["ENGA", "MARB", "MARR", "DIV", "ANUL", "EVEN"]
STATUS_RE = re.compile(
    r"\[(belegt|wahrscheinlich|möglich|ungeklärt|widerlegt|"
    r"proven|probable|possible|unresolved|disproven)\]", re.I)
STATUS_EN = {"proven": "belegt", "probable": "wahrscheinlich", "possible": "möglich",
             "unresolved": "ungeklärt", "disproven": "widerlegt"}
TREE_SOURCE_RE = re.compile(
    r"family\s*tree|stammb[aä]um|smart\s*match|geni\b|world\s*tree|"
    r"ancestry\s*member|onetree|gedbas|wikitree|familysearch\s*family\s*tree", re.I)
BEGIN, END = "<!-- BEGIN gedcom -->", "<!-- END gedcom -->"
DOC_BEGIN, DOC_END = "<!-- BEGIN dokumente -->", "<!-- END dokumente -->"
UNREVIEWED = "ungeprüft"

T = {
    "de": {
        "BIRT": "Geburt", "CHR": "Taufe", "BAPM": "Taufe", "CONF": "Konfirmation/Firmung",
        "EDUC": "Ausbildung", "OCCU": "Beruf", "RELI": "Konfession", "RESI": "Wohnort",
        "NATI": "Staatsangehörigkeit", "EMIG": "Auswanderung", "IMMI": "Einwanderung",
        "NATU": "Einbürgerung", "CENS": "Zählung", "TITL": "Titel", "EVEN": "Ereignis",
        "FACT": "Angabe", "DEAT": "Tod", "BURI": "Begräbnis", "CREM": "Einäscherung",
        "ENGA": "Verlobung", "MARB": "Aufgebot", "MARR": "Heirat", "DIV": "Scheidung",
        "ANUL": "Aufhebung",
        "desc": "Aus dem Baum übernommen (GEDCOM {x}); noch nicht ausgewertet.",
        "banner": "> Stand des Baums laut `{f}`. Dieser Block wird neu erzeugt – Änderungen gehören in den Baum oder unter den Block.",
        "vital": "## Stammdaten laut Baum",
        "cols": "| Ereignis | Datum | Ort | Status | Quelle laut Baum |",
        "family": "## Familie laut Baum", "child_in": "Kind in", "union": "Ehe / Partnerschaft",
        "notes": "## Notizen laut Baum", "couple": "## Paar laut Baum", "partner": "Partner",
        "children": "## Kinder laut Baum", "child_cols": "| Kind | Geburt | Zuordnung |",
        "tree_only": "nur anderer Baum", "none": "keine",
        "chart": "## Kernfamilie laut Baum",
        "chart_legend": "Gestrichelt: Beziehung laut Baum, nicht ausgewertet. Das Diagramm erzeugt keine Links im Graphen.",
        "more": "+{n} weitere",
        "tail_person": "## Belege\n\n## Dokumente\n\n{db}\n{de}\n\n## Offene Fragen\n\n## Nicht identisch mit\n",
        "tail_family": "## Belege\n\n## Dokumente\n\n{db}\n{de}\n\n## Offene Fragen\n",
        "before": "vor ", "after": "nach ",
        "create": "anlegen", "update": "Block erneuern", "same": "unverändert",
        "skip_exists": "vorhanden – übersprungen (mit --update wird nur der Block erneuert)",
        "skip_nomarker": "vorhanden, aber ohne Block-Marker – nicht angefasst",
        "summary": "{c} anlegen · {u} Block erneuern · {s} unverändert · {k} übersprungen",
        "dry": "Probelauf – nichts geschrieben. Mit --write ausführen.",
    },
    "en": {
        "BIRT": "Birth", "CHR": "Baptism", "BAPM": "Baptism", "CONF": "Confirmation",
        "EDUC": "Education", "OCCU": "Occupation", "RELI": "Religion", "RESI": "Residence",
        "NATI": "Nationality", "EMIG": "Emigration", "IMMI": "Immigration",
        "NATU": "Naturalisation", "CENS": "Census", "TITL": "Title", "EVEN": "Event",
        "FACT": "Fact", "DEAT": "Death", "BURI": "Burial", "CREM": "Cremation",
        "ENGA": "Engagement", "MARB": "Banns", "MARR": "Marriage", "DIV": "Divorce",
        "ANUL": "Annulment",
        "desc": "Taken over from the tree (GEDCOM {x}); not evaluated yet.",
        "banner": "> The tree as of `{f}`. This block is regenerated – changes belong in the tree or below the block.",
        "vital": "## Vital data as in the tree",
        "cols": "| Event | Date | Place | Status | Source as in the tree |",
        "family": "## Family as in the tree", "child_in": "Child in", "union": "Marriage / partnership",
        "notes": "## Notes as in the tree", "couple": "## Couple as in the tree", "partner": "Partner",
        "children": "## Children as in the tree", "child_cols": "| Child | Birth | Assignment |",
        "tree_only": "another tree only", "none": "none",
        "chart": "## Immediate family as in the tree",
        "chart_legend": "Dashed: relationship as in the tree, not evaluated. The diagram adds no links to the graph.",
        "more": "+{n} more",
        "tail_person": "## Evidence\n\n## Documents\n\n{db}\n{de}\n\n## Open questions\n\n## Not identical with\n",
        "tail_family": "## Evidence\n\n## Documents\n\n{db}\n{de}\n\n## Open questions\n",
        "before": "before ", "after": "after ",
        "create": "create", "update": "renew block", "same": "unchanged",
        "skip_exists": "exists – skipped (--update renews the block only)",
        "skip_nomarker": "exists but has no block markers – left alone",
        "summary": "{c} to create · {u} blocks to renew · {s} unchanged · {k} skipped",
        "dry": "Dry run – nothing written. Run with --write.",
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


class Node:
    __slots__ = ("level", "xref", "tag", "value", "children")

    def __init__(self, level, xref, tag, value):
        self.level, self.xref, self.tag, self.value, self.children = level, xref, tag, value, []

    def first(self, tag):
        return next((c for c in self.children if c.tag == tag), None)

    def all(self, tag):
        return [c for c in self.children if c.tag == tag]

    def val(self, tag):
        node = self.first(tag)
        return node.value.strip() if node else ""


def parse(path: str):
    records, stack = [], []
    for line in read_text(path).splitlines():
        m = re.match(r"\s*(\d+)\s+(?:(@[^@]+@)\s+)?(\S+)(?: (.*))?$", line)
        if not m:
            continue
        level, tag, value = int(m.group(1)), m.group(3).upper(), m.group(4) or ""
        stack = stack[:level]
        if tag in ("CONT", "CONC") and stack:
            stack[-1].value += ("\n" if tag == "CONT" else "") + value
            continue
        node = Node(level, m.group(2), tag, value)
        if level == 0:
            records.append(node)
        elif stack:
            stack[-1].children.append(node)
        else:
            continue
        stack.append(node)
    return records


def fmt_one(text: str) -> str:
    m = re.match(r"^(?:(\d{1,2})\s+)?(?:([A-ZÄ]{3})\.?\s+)?(\d{3,4})(?:/\d{2})?$", text.strip())
    if not m:
        return text.strip()
    day, mon, year = m.group(1), MONTHS.get(m.group(2) or ""), m.group(3).zfill(4)
    if m.group(2) and not mon:
        return text.strip()
    if day and mon:
        return f"{year}-{mon:02d}-{int(day):02d}"
    return f"{year}-{mon:02d}" if mon else year


def fmt_date(value: str, t) -> str:
    v = re.sub(r"@#D[A-Z ]+@", "", value.upper()).strip()
    if not v:
        return ""
    m = re.match(r"^BET\s+(.+?)\s+AND\s+(.+)$", v)
    if m:
        return f"{fmt_one(m.group(1))}/{fmt_one(m.group(2))}"
    m = re.match(r"^FROM\s+(.+?)\s+TO\s+(.+)$", v)
    if m:
        return f"{fmt_one(m.group(1))}–{fmt_one(m.group(2))}"
    for prefix, out in (("ABT", "~"), ("EST", "~"), ("CAL", "~"), ("BEF", t["before"]),
                        ("AFT", t["after"]), ("FROM", ""), ("TO", "–"), ("INT", "")):
        if v.startswith(prefix + " "):
            return out + fmt_one(v[len(prefix):].split("(")[0])
    return fmt_one(v)


def year_of(value: str) -> str:
    m = re.search(r"(\d{4})", value or "")
    return m.group(1) if m else ""


def cell(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("|", "/")).strip()


def yaml_str(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def slug(text: str) -> str:
    text = re.sub(r"\s+", "-", text.strip())
    return re.sub(r"[^0-9A-Za-zÀ-ÖØ-öø-ÿ-]", "", text).strip("-")


def split_name(value: str):
    m = re.match(r"^(.*?)/(.*?)/(.*)$", value)
    if not m:
        return value.strip(), ""
    given = " ".join((m.group(1) + " " + m.group(3)).split())
    return given, m.group(2).strip()


def citations(node, sources, t):
    out, status = [], None
    texts = []
    for s in node.all("SOUR"):
        ref = s.value.strip()
        if ref.startswith("@"):
            title = sources.get(ref, ref)
            page = s.val("PAGE")
            text = ", ".join(x for x in (title, page) if x)
            texts.append(page + " " + s.val("NOTE"))
        else:
            title, text = ref, ref
            texts.append(ref)
        if TREE_SOURCE_RE.search(title):
            text += f" ({t['tree_only']})"
        out.append(text)
    texts += [n.value for n in node.all("NOTE")]
    for text in texts:
        m = STATUS_RE.search(text or "")
        if m:
            status = STATUS_EN.get(m.group(1).lower(), m.group(1).lower())
            break
    return "; ".join(out) or t["none"], status or UNREVIEWED


def event_rows(rec, tags, sources, t):
    rows = []
    for node in rec.children:
        if node.tag not in tags:
            continue
        if not node.children and node.tag in ("OCCU", "RELI", "NATI", "TITL", "EDUC", "FACT") and not node.value.strip():
            continue
        label = t[node.tag]
        kind = node.val("TYPE")
        detail = node.value.strip()
        if detail.upper() == "Y":
            detail = ""
        if node.tag in ("EVEN", "FACT") and kind:
            label = kind
        elif kind:
            detail = ", ".join(x for x in (detail, kind) if x)
        if detail:
            label = f"{label}: {detail}"
        cite, status = citations(node, sources, t)
        rows.append((label, fmt_date(node.val("DATE"), t), node.val("PLAC"), status, cite))
    return rows


MAX_KIN = 12


def mm_label(text: str) -> str:
    return text.replace('"', "#quot;").replace("\n", " ")


def family_chart(x, people, fam_info, t):
    """Mermaid flowchart: parents, siblings, partners and children of one person.

    Every edge is dashed: the generator only knows what the tree asserts.
    Mermaid edges are not links, so the Obsidian graph stays governed by the
    link rules; the diagram is a picture of the tree, not a claim."""
    rec = people[x]["rec"]
    nodes, edges, seen = [], [], set()

    def nid(xref):
        return "n" + re.sub(r"[^0-9A-Za-z]", "", xref)

    def person(xref, cls=""):
        if xref in seen:
            return
        seen.add(xref)
        p = people[xref]
        nodes.append(f'  {nid(xref)}["{mm_label(p["title"])}"]' + (f":::{cls}" if cls else ""))

    def union(fx):
        info = fam_info[fx]
        marr = info["rec"].first("MARR")
        year = year_of(marr.val("DATE")) if marr else ""
        uid = "u" + re.sub(r"[^0-9A-Za-z]", "", fx)
        if uid not in seen:
            seen.add(uid)
            nodes.append(f'  {uid}(("∞{" " + year if year else ""}"))')
        return uid

    def kids(fx, skip, cap):
        out = [c.value.strip() for c in fam_info[fx]["rec"].all("CHIL")
               if c.value.strip() in people and c.value.strip() != skip]
        return out[:cap], max(0, len(out) - cap)

    person(x, "self")
    for famc in rec.all("FAMC"):
        fx = famc.value.strip()
        if fx not in fam_info:
            continue
        u = union(fx)
        for parent in fam_info[fx]["partners"]:
            person(parent)
            edges.append(f"  {nid(parent)} -.- {u}")
        edges.append(f"  {u} -.-> {nid(x)}")
        sibs, rest = kids(fx, x, MAX_KIN)
        for s in sibs:
            person(s)
            edges.append(f"  {u} -.-> {nid(s)}")
        if rest:
            more = f"m{nid(fx)}"
            nodes.append(f'  {more}["{t["more"].format(n=rest)}"]')
            edges.append(f"  {u} -.-> {more}")
    for fams in rec.all("FAMS"):
        fx = fams.value.strip()
        if fx not in fam_info:
            continue
        u = union(fx)
        edges.append(f"  {nid(x)} -.- {u}")
        for partner in fam_info[fx]["partners"]:
            if partner != x:
                person(partner)
                edges.append(f"  {nid(partner)} -.- {u}")
        children, rest = kids(fx, None, MAX_KIN)
        for c in children:
            person(c)
            edges.append(f"  {u} -.-> {nid(c)}")
        if rest:
            more = f"m{nid(fx)}"
            nodes.append(f'  {more}["{t["more"].format(n=rest)}"]')
            edges.append(f"  {u} -.-> {more}")
    if not edges:
        return []
    return (["```mermaid", "flowchart TB", "  classDef self stroke-width:3px"]
            + nodes + edges + ["```", "", t["chart_legend"]])


def load_id_map(path):
    mapping = {}
    if not path:
        return mapping
    for line in read_text(path).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in re.split(r"[;,\t]", line)]
        if len(parts) >= 2 and parts[0].strip("@") and parts[1]:
            mapping["@" + parts[0].strip("@") + "@"] = parts[1]
    return mapping


def existing_notes(root):
    """Map `id` -> path for every Markdown note under root that declares one."""
    found = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for name in filenames:
            if not name.lower().endswith(".md"):
                continue
            path = os.path.join(dirpath, name)
            try:
                head = open(path, encoding="utf-8").read(4000)
            except (OSError, UnicodeDecodeError):
                continue
            if not head.startswith("---"):
                continue
            m = re.search(r"^id:\s*[\"']?([^\"'\n#]+?)[\"']?\s*$", head.split("\n---", 1)[0], re.M)
            if m:
                found.setdefault(m.group(1).strip(), path)
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("gedcom")
    ap.add_argument("--root")
    ap.add_argument("--persons-dir", default="20_personen")
    ap.add_argument("--families-dir", default="30_familien-orte")
    ap.add_argument("--id-map")
    ap.add_argument("--list-ids", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--update", action="store_true")
    ap.add_argument("--no-chart", action="store_true",
                    help="no Mermaid diagram of the immediate family in person notes")
    ap.add_argument("--lang", choices=("de", "en"), default="de")
    ap.add_argument("--by", default="process:gedcom-to-okf")
    args = ap.parse_args()
    t = T[args.lang]

    records = parse(args.gedcom)
    sources = {r.xref: (r.val("TITL") or r.val("ABBR") or r.xref) for r in records if r.tag == "SOUR" and r.xref}
    notes_rec = {r.xref: r.value for r in records if r.tag == "NOTE" and r.xref}
    indis = [r for r in records if r.tag == "INDI" and r.xref]
    fams = [r for r in records if r.tag == "FAM" and r.xref]

    people = {}
    for r in indis:
        names = [n.value for n in r.all("NAME") if n.value.strip()]
        given, surname = split_name(names[0]) if names else ("", "")
        birth = r.first("BIRT")
        bapt = r.first("CHR") or r.first("BAPM")
        death = r.first("DEAT")
        b_year = year_of(birth.val("DATE")) if birth else ""
        approx = "~" if birth and re.match(r"\s*(ABT|EST|CAL|BEF|AFT|BET|FROM|TO)\b", birth.val("DATE").upper()) else ""
        if not b_year and bapt and year_of(bapt.val("DATE")):
            b_year, approx = year_of(bapt.val("DATE")), "~"
        place = (birth.val("PLAC") if birth else "") or (bapt.val("PLAC") if bapt else "")
        place = place.split(",")[0].strip()
        when = f"{'~' if approx else '*'}{b_year}" if b_year else "?"
        title = f"{(surname or '?').upper()}, {given or '?'} ({' '.join(x for x in (when, place) if x)})"
        aliases = []
        for n in names:
            g, s = split_name(n)
            full = " ".join(x for x in (g, s) if x)
            if full and full not in aliases:
                aliases.append(full)
        first_name = r.first("NAME")
        if first_name:
            for tag in ("_MARNM", "NICK"):
                for extra in first_name.all(tag):
                    value = " ".join(extra.value.replace("/", " ").split())
                    if value and value not in aliases:
                        aliases.append(value)
        people[r.xref] = {
            "rec": r, "given": given, "surname": surname, "title": title, "aliases": aliases,
            "b_year": b_year, "birth": fmt_date(birth.val("DATE"), t) if birth else "",
            "death": fmt_date(death.val("DATE"), t) if death else "",
        }

    if args.list_ids:
        print("xref;name;born;died")
        for x, p in people.items():
            name = " ".join(s for s in (p["given"], p["surname"]) if s)
            print(f"{x.strip('@')};{name};{p['birth']};{p['death']}")
        for f in fams:
            pair = " ∞ ".join(
                " ".join(s for s in (people[x]["given"], people[x]["surname"]) if s)
                for x in (f.val("HUSB"), f.val("WIFE")) if x in people)
            marr = f.first("MARR")
            print(f"{f.xref.strip('@')};{pair};{fmt_date(marr.val('DATE'), t) if marr else ''};")
        return 0

    if not args.root:
        ap.error("--root is required unless --list-ids is given")
    id_map = load_id_map(args.id_map)
    ident = lambda x: id_map.get(x, x.strip("@"))  # noqa: E731
    known = existing_notes(args.root) if os.path.isdir(args.root) else {}
    pdir = os.path.join(args.root, args.persons_dir)
    fdir = os.path.join(args.root, args.families_dir)

    paths = {}
    for x, p in people.items():
        pid = ident(x)
        name = "-".join(s for s in (slug(p["surname"]).upper(), slug(p["given"])) if s) or "unbekannt"
        default = os.path.join(pdir, f"{pid}_{name}_{p['b_year'] or '0000'}.md")
        paths[x] = known.get(pid, default)
    fam_info = {}
    for f in fams:
        fid = ident(f.xref)
        partners = [x for x in (f.val("HUSB"), f.val("WIFE")) if x in people]
        marr = f.first("MARR")
        m_year = year_of(marr.val("DATE")) if marr else ""
        m_place = marr.val("PLAC").split(",")[0].strip() if marr else ""
        pair = " ∞ ".join(f"{(people[x]['surname'] or '?').upper()}, {people[x]['given'] or '?'}" for x in partners) or "?"
        extra = " ".join(x for x in (m_year, m_place) if x)
        title = f"{pair} ({extra})" if extra else pair
        surn = "-".join(slug(people[x]["surname"]).upper() or "X" for x in partners) or "unbekannt"
        default = os.path.join(fdir, f"{fid}_{surn}{'_' + m_year if m_year else ''}.md")
        fam_info[f.xref] = {"rec": f, "id": fid, "title": title, "partners": partners}
        paths[f.xref] = known.get(fid, default)

    def link(src_xref, dst_xref, text):
        rel = os.path.relpath(paths[dst_xref], os.path.dirname(paths[src_xref])).replace(os.sep, "/")
        rel = rel.replace(" ", "%20").replace("(", "%28").replace(")", "%29")
        return f"[{text}]({rel})"

    def table(header, rows):
        sep = "|" + "|".join("---" for _ in header.strip("|").split("|")) + "|"
        return [header, sep] + ["| " + " | ".join(cell(c) or "–" for c in row) + " |" for row in rows]

    def note_lines(rec):
        out = []
        for n in rec.all("NOTE"):
            text = notes_rec.get(n.value.strip(), n.value) if n.value.strip().startswith("@") else n.value
            if text.strip():
                out.append(text.strip())
        return out

    src_name = os.path.basename(args.gedcom)
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    plan = []

    for x, p in people.items():
        r = p["rec"]
        block = [BEGIN, t["banner"].format(f=src_name), "", t["vital"], ""]
        block += table(t["cols"], event_rows(r, INDI_EVENTS, sources, t) or [("–", "", "", "", "")])
        rel_lines = []
        for famc in r.all("FAMC"):
            if famc.value.strip() in fam_info:
                fx = famc.value.strip()
                rel_lines.append(f"- {t['child_in']}: {link(x, fx, fam_info[fx]['id'] + ' ' + fam_info[fx]['title'])} – {UNREVIEWED}")
        for fams_ in r.all("FAMS"):
            if fams_.value.strip() in fam_info:
                fx = fams_.value.strip()
                rel_lines.append(f"- {t['union']}: {link(x, fx, fam_info[fx]['id'] + ' ' + fam_info[fx]['title'])} – {UNREVIEWED}")
        block += ["", t["family"], ""] + (rel_lines or [f"- {t['none']}"])
        chart = [] if args.no_chart else family_chart(x, people, fam_info, t)
        if chart:
            block += ["", t["chart"], ""] + chart
        notes = note_lines(r)
        if notes:
            block += ["", t["notes"], ""] + notes
        block.append(END)
        sex = r.val("SEX")[:1].upper()
        front = ["---", "type: Person", f"id: {ident(x)}", f"title: {yaml_str(p['title'])}",
                 f"description: {yaml_str(t['desc'].format(x=x.strip('@')))}"]
        if p["aliases"]:
            front += ["aliases:"] + [f"  - {yaml_str(a)}" for a in p["aliases"]]
        if sex in ("M", "F"):
            front.append(f"sex: {sex}")
        front += [f"conclusion: {UNREVIEWED}", "status: draft", f"gedcom_xref: {x.strip('@')}",
                  f"generated: {{ by: {args.by}, at: {now} }}", "---"]
        tail = t["tail_person"].format(db=DOC_BEGIN, de=DOC_END)
        plan.append((paths[x], "\n".join(front) + f"\n\n# {p['title']}\n\n", "\n".join(block), "\n\n" + tail))

    for fx, info in fam_info.items():
        f = info["rec"]
        block = [BEGIN, t["banner"].format(f=src_name), "", t["couple"], ""]
        block += [f"- {t['partner']}: {link(fx, x, people[x]['title'])}" for x in info["partners"]] or [f"- {t['none']}"]
        rows = event_rows(f, FAM_EVENTS, sources, t)
        if rows:
            block += [""] + table(t["cols"], rows)
        kids = [c.value.strip() for c in f.all("CHIL") if c.value.strip() in people]
        block += ["", t["children"], ""]
        if kids:
            block += table(t["child_cols"], [(link(fx, k, people[k]["title"]), people[k]["birth"], UNREVIEWED) for k in kids])
        else:
            block.append(f"- {t['none']}")
        notes = note_lines(f)
        if notes:
            block += ["", t["notes"], ""] + notes
        block.append(END)
        front = ["---", "type: Family", f"id: {info['id']}", f"title: {yaml_str(info['title'])}",
                 f"description: {yaml_str(t['desc'].format(x=fx.strip('@')))}",
                 f"conclusion: {UNREVIEWED}", "status: draft", f"gedcom_xref: {fx.strip('@')}",
                 f"generated: {{ by: {args.by}, at: {now} }}", "---"]
        tail = t["tail_family"].format(db=DOC_BEGIN, de=DOC_END)
        plan.append((paths[fx], "\n".join(front) + f"\n\n# {info['title']}\n\n", "\n".join(block), "\n\n" + tail))

    counts = {"create": 0, "update": 0, "same": 0, "skip": 0}
    for path, head, block, tail in sorted(plan):
        rel = os.path.relpath(path, args.root)
        if not os.path.exists(path):
            counts["create"] += 1
            print(f"[{t['create']}] {rel}")
            if args.write:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(head + block + tail)
            continue
        old = open(path, encoding="utf-8").read()
        if BEGIN not in old or END not in old:
            counts["skip"] += 1
            print(f"[{t['skip_nomarker']}] {rel}")
            continue
        start, end = old.index(BEGIN), old.index(END) + len(END)
        if old[start:end] == block:
            counts["same"] += 1
            continue
        if not args.update:
            counts["skip"] += 1
            print(f"[{t['skip_exists']}] {rel}")
            continue
        counts["update"] += 1
        print(f"[{t['update']}] {rel}")
        if args.write:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(old[:start] + block + old[end:])

    print(t["summary"].format(c=counts["create"], u=counts["update"], s=counts["same"], k=counts["skip"]))
    if not args.write:
        print(t["dry"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
