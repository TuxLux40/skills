#!/usr/bin/env python3
"""Order migration items into dependency waves and flag circular dependencies.

Input  items.csv : id,name,type,strategy,effort,risk,owner   (effort/risk: 1-5, optional)
       deps.csv  : item,depends_on                            (item needs depends_on migrated/available first)
Output <out>/waves.csv, summary.md (wave plan + Mermaid diagram + any cycles)

A thing that others depend on migrates (or gets a bridge) before the things that depend on it.
Wave 0 = items whose dependencies are all retired/out-of-scope or have none. Each later wave
holds items all of whose in-scope dependencies are in an earlier wave. Items in a cycle can't be
ordered — they're reported so you can break the loop with a temporary bridge.

Stdlib only. Ids compared case-insensitively. `retire`/`retain` strategy items still order
(a retained dependency is "already there" = wave 0) but are marked so.
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path
from xml.sax.saxutils import escape  # noqa: F401  (kept for parity; mermaid is escaped manually)


def norm(s: str) -> str:
    return (s or "").strip().lower()


def load_items(path: Path):
    items = {}
    with path.open(newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            i = norm(row["id"])
            if not i:
                continue
            items[i] = {
                "id": i,
                "name": row.get("name", "") or row["id"],
                "type": row.get("type", "") or "",
                "strategy": norm(row.get("strategy", "")) or "rehost",
                "effort": _int(row.get("effort")),
                "risk": _int(row.get("risk")),
                "owner": row.get("owner", "") or "",
            }
    return items


def _int(v):
    try:
        return max(1, min(5, int(float(v))))
    except (TypeError, ValueError):
        return 3


def load_deps(path: Path):
    deps = defaultdict(set)
    with path.open(newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            a, b = norm(row["item"]), norm(row["depends_on"])
            if a and b and a != b:
                deps[a].add(b)
    return deps


def assign_waves(items, deps):
    """Kahn-style longest-path layering. Returns {id: wave} and the set of ids stuck in cycles."""
    ids = set(items)
    # Only in-scope dependencies constrain ordering. A dependency that's 'retain' is already
    # present (wave 0 anchor); out-of-scope deps are ignored.
    def blocking(i):
        out = set()
        for d in deps.get(i, ()):
            if d in ids and items[d]["strategy"] != "retain":
                out.add(d)
        return out

    wave = {}
    # Iteratively place items whose blocking deps are all placed.
    remaining = set(ids)
    progress = True
    while remaining and progress:
        progress = False
        for i in sorted(remaining):
            b = blocking(i)
            if b & remaining:
                continue  # still waiting on something unplaced
            wave[i] = 0 if not b else 1 + max(wave[d] for d in b)
            remaining.discard(i)
            progress = True
    # Whatever's left is in a dependency cycle.
    return wave, remaining


def find_cycles(stuck, deps, ids):
    """Return simple cycles among the stuck nodes (for the report)."""
    cycles, seen = [], set()
    def dfs(node, path, pathset):
        for d in sorted(deps.get(node, ())):
            if d not in stuck:
                continue
            if d in pathset:
                cyc = path[path.index(d):] + [d]
                key = frozenset(cyc)  # same loop from any start point = one cycle
                if key not in seen:
                    seen.add(key)
                    cycles.append(cyc)
                continue
            dfs(d, path + [d], pathset | {d})
    for n in sorted(stuck):
        dfs(n, [n], {n})
    return cycles


ORDER_HINT = ["identity", "account", "dns", "network", "database", "datastore", "storage",
              "app", "application", "integration", "automation", "endpoint", "client"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--items", required=True, type=Path)
    ap.add_argument("--deps", type=Path)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()

    items = load_items(a.items)
    if not items:
        sys.exit("no items found")
    deps = load_deps(a.deps) if a.deps and a.deps.exists() else defaultdict(set)
    # warn on dangling deps (typo-catching)
    dangling = {d for i in deps for d in deps[i] if d not in items}
    wave, stuck = assign_waves(items, deps)
    cycles = find_cycles(stuck, deps, set(items)) if stuck else []

    a.out.mkdir(parents=True, exist_ok=True)
    with (a.out / "waves.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["wave", "id", "name", "type", "strategy", "effort", "risk", "risk_x_effort", "owner", "depends_on"])
        placed = sorted(wave, key=lambda i: (wave[i], -(items[i]["risk"] * items[i]["effort"]), i))
        for i in placed:
            it = items[i]
            w.writerow([wave[i], i, it["name"], it["type"], it["strategy"], it["effort"], it["risk"],
                        it["risk"] * it["effort"], it["owner"], ";".join(sorted(deps.get(i, ())))])
        for i in sorted(stuck):
            it = items[i]
            w.writerow(["CYCLE", i, it["name"], it["type"], it["strategy"], it["effort"], it["risk"],
                        it["risk"] * it["effort"], it["owner"], ";".join(sorted(deps.get(i, ())))])

    # summary
    nwaves = (max(wave.values()) + 1) if wave else 0
    L = ["# Migration wave plan", "",
         f"- items: {len(items)}  ·  waves: {nwaves}  ·  in cycles: {len(stuck)}  ·  dangling deps: {len(dangling)}",
         ""]
    by_strat = defaultdict(int)
    for it in items.values():
        by_strat[it["strategy"]] += 1
    L += ["Strategy mix: " + ", ".join(f"{k} {v}" for k, v in sorted(by_strat.items())), ""]
    for wv in range(nwaves):
        members = sorted((i for i in wave if wave[i] == wv),
                         key=lambda i: (-(items[i]["risk"] * items[i]["effort"]), i))
        if not members:
            continue
        L.append(f"## Wave {wv}")
        L.append("")
        L.append("| item | type | strategy | effort | risk | R×E | owner | depends on |")
        L.append("|---|---|---|---|---|---|---|---|")
        for i in members:
            it = items[i]
            L.append(f"| {it['name']} | {it['type']} | {it['strategy']} | {it['effort']} | {it['risk']} | "
                     f"{it['risk']*it['effort']} | {it['owner']} | {', '.join(sorted(deps.get(i, ()))) or '—'} |")
        L.append("")
    if stuck:
        L += ["## ⚠ Circular dependencies — break these with a temporary bridge", ""]
        if cycles:
            for c in cycles:
                L.append("- " + " → ".join(items[x]["name"] for x in c))
        else:
            L.append("- stuck items: " + ", ".join(sorted(items[x]["name"] for x in stuck)))
        L.append("")
    if dangling:
        L += ["## Dangling dependencies (not in inventory — typo or out of scope?)", "",
              "- " + ", ".join(sorted(dangling)), ""]
    # Mermaid
    L += ["## Dependency diagram", "", "```mermaid", "flowchart TD"]
    nid = {i: f"n{k}" for k, i in enumerate(sorted(items))}
    for i in sorted(items):
        lab = items[i]["name"].replace('"', "'")[:40]
        tag = f"<br/>w{wave.get(i, '?')}·{items[i]['strategy']}"
        L.append(f'  {nid[i]}["{lab}{tag}"]')
    for i in sorted(deps):
        if i not in nid:
            continue
        for d in sorted(deps[i]):
            if d in nid:
                L.append(f"  {nid[d]} --> {nid[i]}")
    L += ["```", ""]
    (a.out / "summary.md").write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {a.out}/waves.csv, summary.md — {len(items)} items in {nwaves} waves, "
          f"{len(stuck)} in cycles, {len(dangling)} dangling")
    if stuck:
        print("WARNING: circular dependencies, see summary.md", file=sys.stderr)


if __name__ == "__main__":
    main()
