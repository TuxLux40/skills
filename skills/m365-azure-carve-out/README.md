# m365-azure-carve-out

IT carve-outs and tenant splits for Microsoft 365, Entra ID, Active Directory and Azure. The skill builds an inventory, turns it into a dependency graph and an entanglement register, picks a separation approach per system, scopes the TSA, and plans migration waves with the Microsoft-native cross-tenant tools.

- `scripts/user-footprint.ps1`: **standard-user** collector (no admin) — your own My Apps, groups, teams, shares via Graph `/me`; run per colleague and merge
- `scripts/m365-inventory.ps1`: Entra / Exchange / SharePoint / Teams, read-only, writes `edges.csv`
- `scripts/azure_inventory.py`: Azure Resource Graph (hierarchy, network, RBAC, managed identities, IaC tags), writes `edges.csv`
- `scripts/ad-inventory.ps1`: on-prem AD (trusts, OUs, GPO links, SPNs, DNS), writes `edges.csv`
- `scripts/entanglement_graph.py`: merges the edges, labels nodes divest/retain/shared, and writes the entanglement register, GraphML and a summary with Mermaid
- `templates/`: entanglement register, RACI matrix, colleague dependency survey, example edges/seeds

Works from a **standard non-admin account** as the baseline (map your own and colleagues' footprint read-only); admin collectors are the fallback that enriches the same graph.

## Install

```bash
mkdir -p ~/.claude/skills && curl -fsSL https://github.com/TuxLux40/skills/archive/refs/heads/master.tar.gz | tar -xz --strip-components=2 -C ~/.claude/skills skills-master/skills/m365-azure-carve-out
```

## Quick test

```bash
python3 scripts/entanglement_graph.py --edges templates/edges.example.csv --seeds templates/seeds.example.csv --out /tmp/carveout
cat /tmp/carveout/summary.md
```

Full marketplace: [TuxLux40/skills](https://github.com/TuxLux40/skills) · details in `SKILL.md`
