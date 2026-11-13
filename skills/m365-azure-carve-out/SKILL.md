---
name: m365-azure-carve-out
description: IT carve-out / divestiture / tenant split for Microsoft 365, Entra ID, on-prem Active Directory and Azure — discovery, infrastructure and topology mapping, dependency and relationship analysis, separation approach per system, Day One design, TSA scoping and exit, and Microsoft-native tenant-to-tenant migration (cross-tenant mailbox, OneDrive, SharePoint, Migration Orchestrator, Azure subscription directory transfer). Use whenever the user mentions carve-out, divestiture, spin-off, separation, TSA / transition services agreement, entanglement, "split the tenant", "move users to the new company's tenant", tenant-to-tenant (T2T) migration, cross-tenant migration, M&A IT integration, domain move between tenants, AD forest separation, or asks how to find which apps, groups, sites, subscriptions, networks or identities are shared between two business units. Also use for building an inventory, dependency graph or entanglement register of an M365/Azure estate, even when no deal is mentioned.
---

# M365 / Azure carve-out

Goal: turn "we're selling business unit X" into a **sourced, dated, dependency-ordered separation plan** — where every shared object is known, every one has an owner and a separation approach, and nothing is found for the first time after signing.

The method in one line: **inventory everything → express it as a graph → label the nodes by owner (divest / retain) → the edges between the two sides are your entanglements → each entanglement gets an approach, a Day One answer and, if needed, a TSA line with an end date.**

## Ground rules

- **Discovery before approach.** Do not recommend "just transfer the subscription" or "use the Orchestrator" before the inventory exists. Gaps found after signing become TSA services nobody priced.
- **Read-only first.** All discovery here is read-only (Graph `*.Read.All`, `Reader` on Azure, `View-Only` roles in Exchange). Say so, and never suggest write permissions for discovery.
- **One-way doors are labelled.** Several steps can't be undone: Azure subscription directory transfer (deletes all RBAC), OneDrive / SharePoint cross-tenant moves (no delta pass), `Set-User -PermanentlyClearPreviousMailboxInfo`, domain removal. Mark them **⚠ irreversible** in any plan you write.
- **Limits change; verify them.** Microsoft's cross-tenant limits and licensing move fast, and the docs even contradict each other (OneDrive size limit: 5 TB on the main page, 2 TB in the FAQ). Quote `references/m365-tenant-migration.md` as the starting point and tell the user to check the linked Learn page before committing to a number. When the Microsoft Learn MCP is available, fetch the page instead of quoting from memory.
- **Labour and privacy law apply in Germany and the EU.** Analysing sign-in logs per employee is monitoring data: involve the works council (*Betriebsrat*, BetrVG §87(1) Nr. 6) and the DPO, and aggregate where you can. Seller-run TSA services that touch the buyer's personal data need a GDPR Art. 28 DPA. Staff who move with the business: Directive 2001/23/EC / §613a BGB. Flag these; don't give legal advice.

## Workflow

### 0. Frame the deal (ask before anything else)
Ask these first. Each answer changes the plan:
1. **Direction**: is the divested unit going into an **existing buyer tenant** (extract-and-migrate), a **new standalone tenant** (clone / rebuild), or **staying put while the parent leaves** (rare, but sometimes the cheapest)?
2. **Seed of truth**: which attribute says who belongs to the divested unit: `companyName`, `department`, OU, cost centre, license group, HR extract? Without a seed you can't label the graph.
3. **Dates**: signing, closing (Day One), target TSA end.
4. **Licensing channel**: EA, MCA or CSP. CSP subscriptions **cannot** change Entra directory, and cross-tenant SharePoint licensing is EA-only.
5. **Hybrid?** On-prem AD, Entra Connect / Cloud Sync, hybrid Exchange, ADFS.
6. **Regulatory**: holds/eDiscovery, Customer Key, sensitivity-label encryption, data residency / Multi-Geo, GCC.

### 1. Inventory: collect raw facts per layer
Run, or have the user run, the collectors in `scripts/`. They emit raw CSVs and one normalized `edges.csv`:

| Layer | Collector | What it finds |
|---|---|---|
| Entra ID, Exchange Online, SharePoint/OneDrive, Teams | `scripts/m365-inventory.ps1` | users, groups (+nesting), app registrations / enterprise apps and who is assigned, OAuth consents, directory roles, CA policies, domains, mailboxes + delegations + holds, connectors, transport rules, sites + owners + group links, teams |
| Azure | `scripts/azure_inventory.py` (Azure Resource Graph via `az graph`) | management groups/subscriptions, resources with tenant-bound properties, managed identities, RBAC, VNet peerings, private endpoints, private DNS links, gateways/ExpressRoute, UDR next hops, IaC provenance (`yor_trace`/`mapping_tag` → Defender for Cloud IaC mapping) |
| On-prem AD | `scripts/ad-inventory.ps1` | trusts, OUs, GPO links, SPNs (service accounts → servers), DNS zones, sites, ADFS relying parties, Entra Connect scope |

Static config misses runtime dependencies. Pair it with **observed** evidence, `references/discovery-dependency-mapping.md` §Runtime: Entra sign-in logs (users → apps, service principals → resources), DC Kerberos/LDAP/NTLM events, VNet flow logs / Traffic Analytics, Azure Migrate agentless dependency analysis, mail flow / message trace for connectors.

### 2. Model: build the graph and label it
```bash
python3 scripts/entanglement_graph.py --edges out/m365/edges.csv out/azure/edges.csv out/ad/edges.csv \
    --aliases out/m365/aliases.csv out/ad/aliases.csv --seeds seeds.csv --out out/graph
```
- Nodes: user, group, mailbox, site, team, app/SP, role, domain, subscription, resource, vnet, server, GPO…
- Seeds label known nodes `divest` / `retain` (from step 0.2).
- Labels propagate along ownership-type edges (`member_of`, `owns`, `contains`). A node reached from both sides becomes **`shared`**. Anything unreachable stays **`unknown`** and goes on the open questions list.
- Outputs: `entanglements.csv` (every edge that crosses sides or touches `shared`), `nodes.csv` with labels, `graph.graphml` (open in Gephi / yEd), `summary.md` with a Mermaid overview of the shared hubs.

The **shared nodes with the highest cross-degree** are the real work: the ERP enterprise app everyone signs into, the hub VNet, the `All Staff` group nested into 40 others, the shared mailbox with delegates on both sides. Rank by cross-degree and by business criticality.

### 3. Decide: an approach per system, not per programme
For every shared node, pick one approach (details and risks in `references/tsa-governance.md`):

| Approach | Use when | Main risk |
|---|---|---|
| **Clone-and-go** | speed matters, no buyer target platform yet | incomplete data purge; clone needs licenses the buyer lacks |
| **Logical separation (TSA)** | buyer migrates soon, short TSA acceptable | data leakage, a TSA that never ends |
| **Extract-and-migrate** | buyer already runs a suitable platform (typical for M365: buyer tenant) | mapping effort, hard cutover date |
| **Rebuild** | legacy near end of life or heavily customized | longest timeline, longest TSA dependency |

Typical M365/Azure split: **extract-and-migrate** for identity, mail, OneDrive, Teams chats (native cross-tenant tools); **clone/re-deploy via IaC** or **subscription transfer** for Azure; **rebuild** for line-of-business apps that are welded to the parent's Entra tenant.

### 4. Design: Day One minimum + TSA schedule
Day One must cover at least: identity and sign-in for the divested users, email and domains (inbound mail must not bounce), payroll/finance access, customer-facing systems, security monitoring/EDR coverage, endpoint management. Everything the buyer can't run itself on Day One becomes a **TSA service line** with service level (= historical level), cost-based price, base term, extension option with notice period and stepped price, and an **exit milestone** tied to a migration wave. Template: `templates/entanglement-register.csv`.

### 5. Sequence: migration waves in dependency order
Order from the graph: **identity → domains/mail routing → mailboxes → OneDrive + Teams chats → SharePoint/Teams shared data → apps/SSO → Azure workloads → endpoints → decommission.** Each wave: test with real data, go/no-go criteria, rollback criteria defined *before* cutover. The M365 tool details, prerequisites and known limits are in `references/m365-tenant-migration.md`. Azure in `references/azure-separation.md`. AD/Entra identity in `references/identity-ad-entra.md`.

### 6. Exit: per service, with evidence
Switch off each TSA service only once its replacement is proven. Get a confirmation that data has been returned or deleted (an exit certificate). Remove cross-tenant access settings, B2B guests, org relationships, app consents and Lighthouse delegations. Resolve the seller's **stranded costs**: licenses, reserved instances and contracts sized for the combined group.

## Output contract
When the user asks for a plan, deliver (adjust to what they asked):
1. **Scope & assumptions**: the step 0 answers, with open questions marked.
2. **Inventory summary**: counts per layer, plus which collectors ran and which didn't.
3. **Entanglement register**: top shared nodes, approach, owner, Day One answer, TSA line.
4. **Wave plan**: dependency-ordered, with ⚠ irreversible steps flagged and rollback points.
5. **Risks**: from `references/tsa-governance.md` §Overrun and from the per-workload "blocks" lists.
6. **Sources**: Learn URLs for every limit or prerequisite you quoted.

If the user keeps a knowledge base, offer to write the register and decisions there. A carve-out runs for months and decisions get lost.

## References
- `references/discovery-dependency-mapping.md`: **how to find relations**: per-layer queries, runtime evidence, graph schema, interpretation heuristics
- `references/m365-tenant-migration.md`: Microsoft-native cross-tenant tools, prerequisites, limits, licensing, what does *not* move
- `references/azure-separation.md`: subscription directory transfer impact matrix, resource-move-then-transfer pattern, Lighthouse for the TSA period
- `references/identity-ad-entra.md`: AD forest/domain separation, Entra Connect re-scoping, cross-tenant sync / MTO for coexistence, domain move
- `references/tsa-governance.md`: entanglement inventory checklist, approaches, TSA scoping rules, overrun signals, licenses/contracts/data/people
- `references/sources.md`: source URLs and what each contributed
