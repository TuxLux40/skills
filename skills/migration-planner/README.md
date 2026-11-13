# migration-planner

Plan and run any migration — move data, systems, accounts or infrastructure from one place to another, safely and in the right order. Platform-agnostic; scales from one person leaving a provider to an enterprise programme.

Method: **know what you have → strategy per item (7 Rs) → order by dependency → move data with dry-run + reconciliation → cut over with a tested rollback → validate & decommission.**

- `scripts/wave_planner.py`: turns an inventory + dependencies into dependency-ordered **waves**, flags circular dependencies and typos, ranks by risk×effort, draws a Mermaid diagram
- `references/`: the 7 Rs, discovery & dependency mapping, data-migration correctness (four reconciliation levels), cutover & rollback, per-domain playbooks (email/files/web/db/cloud/SaaS/accounts), and how the method scales by size
- `templates/`: inventory + deps CSVs, a cutover runbook, and a personal "leaving a provider" checklist

For a Microsoft 365 / Entra / Azure tenant split specifically, use the companion `m365-azure-carve-out` skill. Use this one for everything else or mixed/non-Microsoft moves.

## Install

```bash
mkdir -p ~/.claude/skills && curl -fsSL https://github.com/TuxLux40/skills/archive/refs/heads/master.tar.gz | tar -xz --strip-components=2 -C ~/.claude/skills skills-master/skills/migration-planner
```

## Quick test

```bash
python3 scripts/wave_planner.py --items templates/inventory.example.csv --deps templates/deps.example.csv --out /tmp/plan
cat /tmp/plan/summary.md
```

Full marketplace: [TuxLux40/skills](https://github.com/TuxLux40/skills) · details in `SKILL.md`
