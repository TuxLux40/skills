#!/usr/bin/env python3
"""Build a dependency graph from normalized edges, label nodes divest/retain/shared,
and emit the entanglement register.

Input  edges.csv   : src_id,src_type,rel,dst_id,dst_type[,evidence,source]   (one or more files)
       seeds.csv   : node_id,side            (side = divest | retain)
       aliases.csv : alias,canonical         (optional; e.g. Entra objectId -> UPN, so Azure
                                              RBAC principalIds join onto M365 identities)
Output <out>/nodes.csv, entanglements.csv, graph.graphml, summary.md

Stdlib only. Node ids are compared case-insensitively.
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict, deque
from pathlib import Path
from xml.sax.saxutils import escape

# Relations along which an owner label flows, with direction.
#   "up"   : label flows src -> dst  (user member_of group => group used by user's side)
#   "down" : label flows dst -> src? no: parent contains child => child inherits parent
PROPAGATE_UP = {"member_of", "owns", "linked_to"}   # src's side marks dst
PROPAGATE_DOWN = {"contains"}                       # src (parent) marks dst (child)
# Usage relations: never propagate, but crossing them makes an entanglement.
SIDES = ("divest", "retain")


def norm(s: str) -> str:
    return (s or "").strip().lower()


def load_aliases(paths):
    alias = {}
    for path in paths or []:
        with path.open(newline="", encoding="utf-8-sig") as fh:
            for row in csv.DictReader(fh):
                if row.get("alias") and row.get("canonical"):
                    alias[norm(row["alias"])] = norm(row["canonical"])
    return alias


def load_edges(paths, alias):
    edges, types = [], {}
    for path in paths:
        with path.open(newline="", encoding="utf-8-sig") as fh:
            for row in csv.DictReader(fh):
                s, d = norm(row["src_id"]), norm(row["dst_id"])
                s, d = alias.get(s, s), alias.get(d, d)
                if not s or not d or s == d:
                    continue
                types.setdefault(s, row.get("src_type", "") or "")
                types.setdefault(d, row.get("dst_type", "") or "")
                edges.append({
                    "src": s, "dst": d, "rel": norm(row["rel"]),
                    "evidence": row.get("evidence", "") or "",
                    "source": row.get("source", "") or "",
                })
    return edges, types


def load_seeds(path: Path):
    seeds = {}
    with path.open(newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            side = norm(row["side"])
            if side not in SIDES:
                sys.exit(f"seed {row['node_id']!r}: side must be divest|retain, got {side!r}")
            seeds[norm(row["node_id"])] = side
    return seeds


def propagate(edges, seeds):
    """Multi-source BFS per side along propagating edges. A node reached by both = shared."""
    adj = defaultdict(list)
    for e in edges:
        if e["rel"] in PROPAGATE_UP or e["rel"] in PROPAGATE_DOWN:
            adj[e["src"]].append(e["dst"])
    reached = {side: set() for side in SIDES}
    for side in SIDES:
        q = deque(n for n, s in seeds.items() if s == side)
        seen = reached[side]
        seen.update(q)
        while q:
            n = q.popleft()
            for m in adj[n]:
                # Seeds of the *other* side are hard boundaries: don't flow through them.
                if seeds.get(m, side) != side or m in seen:
                    continue
                seen.add(m)
                q.append(m)
    labels = {}
    for n in set().union(*reached.values()):
        a, b = n in reached["divest"], n in reached["retain"]
        labels[n] = "shared" if a and b else ("divest" if a else "retain")
    for n, s in seeds.items():          # seeds always win
        labels[n] = s
    return labels


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--edges", required=True, type=Path, nargs="+")
    ap.add_argument("--aliases", type=Path, nargs="*")
    ap.add_argument("--seeds", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--top", type=int, default=25, help="hubs to show in summary")
    a = ap.parse_args()

    edges, types = load_edges(a.edges, load_aliases(a.aliases))
    seeds = load_seeds(a.seeds)
    labels = propagate(edges, seeds)
    nodes = set(types)
    for n in nodes:
        labels.setdefault(n, "unknown")

    # Usage edges can turn a single-side node into shared: if a node is used (any rel)
    # by both sides' nodes, mark it shared.
    # A shared source counts as usage by both sides. Iterate to a fixed point so that
    # shared group -> app -> resource chains resolve.
    changed = True
    while changed:
        changed = False
        users_of = defaultdict(set)
        for e in edges:
            s = labels[e["src"]]
            users_of[e["dst"]].update(SIDES if s == "shared" else (s,))
        for n, sides in users_of.items():
            if n in seeds or labels[n] == "shared":
                continue
            if "divest" in sides and "retain" in sides:
                labels[n] = "shared"
                changed = True

    # Entanglements: any edge whose endpoints differ in side, or touches shared.
    ent = []
    cross_deg = defaultdict(int)
    for e in edges:
        ls, ld = labels[e["src"]], labels[e["dst"]]
        pair = {ls, ld}
        if "shared" in pair:
            kind = "shared"          # touches a shared hub
        elif pair == {"divest", "retain"}:
            kind = "cross"           # direct cross-boundary dependency
        elif "unknown" in pair and len(pair) == 2:
            kind = "unlabelled"      # one side known, other needs an owner decision
        else:
            continue                 # same side, or both unknown
        ent.append({**e, "src_type": types[e["src"]], "dst_type": types[e["dst"]],
                    "src_side": ls, "dst_side": ld, "kind": kind})
        cross_deg[e["src"]] += 1
        cross_deg[e["dst"]] += 1

    a.out.mkdir(parents=True, exist_ok=True)
    with (a.out / "nodes.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["node_id", "type", "side", "seeded", "cross_degree"])
        for n in sorted(nodes):
            w.writerow([n, types[n], labels[n], n in seeds, cross_deg.get(n, 0)])

    with (a.out / "entanglements.csv").open("w", newline="", encoding="utf-8") as fh:
        cols = ["kind", "src_id", "src_type", "src_side", "rel", "dst_id", "dst_type", "dst_side", "evidence", "source"]
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for e in sorted(ent, key=lambda x: (x["kind"], x["dst"], x["src"])):
            w.writerow({"kind": e["kind"], "src_id": e["src"], "src_type": e["src_type"], "src_side": e["src_side"],
                        "rel": e["rel"], "dst_id": e["dst"], "dst_type": e["dst_type"], "dst_side": e["dst_side"],
                        "evidence": e["evidence"], "source": e["source"]})

    # GraphML for Gephi / yEd
    ids = {n: f"n{i}" for i, n in enumerate(sorted(nodes))}
    with (a.out / "graph.graphml").open("w", encoding="utf-8") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                 '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">\n'
                 '<key id="label" for="node" attr.name="label" attr.type="string"/>\n'
                 '<key id="type" for="node" attr.name="type" attr.type="string"/>\n'
                 '<key id="side" for="node" attr.name="side" attr.type="string"/>\n'
                 '<key id="rel" for="edge" attr.name="rel" attr.type="string"/>\n'
                 '<graph edgedefault="directed">\n')
        for n in sorted(nodes):
            fh.write(f'<node id="{ids[n]}"><data key="label">{escape(n)}</data>'
                     f'<data key="type">{escape(types[n])}</data><data key="side">{labels[n]}</data></node>\n')
        for i, e in enumerate(edges):
            fh.write(f'<edge id="e{i}" source="{ids[e["src"]]}" target="{ids[e["dst"]]}">'
                     f'<data key="rel">{escape(e["rel"])}</data></edge>\n')
        fh.write("</graph>\n</graphml>\n")

    # Summary
    count = defaultdict(lambda: defaultdict(int))
    for n in nodes:
        count[types[n] or "?"][labels[n]] += 1
    hubs = sorted((n for n in nodes if labels[n] == "shared"), key=lambda n: -cross_deg.get(n, 0))[: a.top]
    unknown = [n for n in nodes if labels[n] == "unknown"]
    lines = ["# Entanglement summary", "",
             f"- nodes: {len(nodes)}  edges: {len(edges)}  seeds: {len(seeds)}",
             f"- entanglement edges: {len(ent)} "
             f"(cross {sum(e['kind']=='cross' for e in ent)}, shared {sum(e['kind']=='shared' for e in ent)}, "
             f"unlabelled {sum(e['kind']=='unlabelled' for e in ent)})",
             f"- unknown nodes (need an owner decision): {len(unknown)}", "",
             "## Nodes by type and side", "", "| type | divest | retain | shared | unknown |", "|---|---|---|---|---|"]
    for t in sorted(count):
        c = count[t]
        lines.append(f"| {t} | {c['divest']} | {c['retain']} | {c['shared']} | {c['unknown']} |")
    lines += ["", f"## Top {len(hubs)} shared hubs (by cross-degree)", "", "| node | type | cross-degree |", "|---|---|---|"]
    lines += [f"| {n} | {types[n]} | {cross_deg.get(n, 0)} |" for n in hubs]
    lines += ["", f"## Unknown nodes (first {min(len(unknown), a.top)} of {len(unknown)}): assign an owner",
              "", "| node | type | edges |", "|---|---|---|"]
    deg = defaultdict(int)
    for e in edges:
        deg[e["src"]] += 1
        deg[e["dst"]] += 1
    lines += [f"| {n} | {types[n]} | {deg[n]} |" for n in sorted(unknown, key=lambda n: -deg[n])[: a.top]]
    lines += ["", "## Overview", "", "```mermaid", "flowchart LR",
              '  D["divest"]:::d', '  R["retain"]:::r']
    for i, n in enumerate(hubs[:12]):
        lab = n.replace('"', "'")[:60]
        lines.append(f'  H{i}["{lab}<br/>({types[n]})"]:::s')
        lines.append(f"  D --- H{i} --- R")
    lines += ["  classDef d fill:#fde2e1,stroke:#c0392b", "  classDef r fill:#e1effd,stroke:#2c6fbb",
              "  classDef s fill:#fff4d6,stroke:#b7950b", "```", ""]
    (a.out / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {a.out}/nodes.csv, entanglements.csv, graph.graphml, summary.md "
          f"({len(ent)} entanglements, {len(hubs)} shared hubs, {len(unknown)} unknown)")


if __name__ == "__main__":
    main()
