# Separation programme, TSA and governance

Based mainly on ColdAI, *Carve-Out IT Separation and TSA Planning* (2026-10-10), and the Coherence carve-out vs integration article (2026-07-23), with M365/Azure specifics added.

## Carve-out or integration?

- **Integration**: merge identity, M365, Azure and security into one estate. This gives long-term efficiency, governance and a single user experience.
- **Carve-out**: create a standalone environment so the unit can run independently or be sold. Choose it for divestitures, regulated or contractually separate units, or when integration has to wait.
- Decide from the business objective (own brand? full consolidation within months? regulatory separation?), not from the tooling. Then check against the dependency assessment: which apps rely on shared infrastructure, identity/auth dependencies, compliance limits on data movement, processes that can't tolerate downtime.

## Seller vs buyer

- **Seller**: protect the retained business, minimal disruption to shared systems, short TSA, no costs left behind.
- **Buyer**: Day One continuity, free choice of target platforms, a clear view of standalone run-cost.
- Shared artifacts: entanglement register, Day One requirements, TSA schedules. Each side owns its own plan. Joint governance with named separation leads on both sides.

## Sequence

1. **Entanglement inventory**: everything the sold business uses that it doesn't own outright (before signing)
2. **Approach per system**: clone / logical separation / extract-and-migrate / rebuild
3. **Day One design**: the minimum that must work at completion, and who provides it
4. **TSA schedules**: services the seller keeps providing, with levels, prices, end dates
5. **Migration waves**: dependency order, each with rollback
6. **TSA exit**: services switched off one by one; stranded costs resolved

## Entanglement inventory checklist

- [ ] **Applications**: ERP, CRM, HR, finance, product/plant systems. Shared instance or dedicated? For M365: enterprise apps and SSO.
- [ ] **Shared infrastructure**: data centres, cloud accounts/subscriptions, networks, identity providers, email, security tooling, monitoring
- [ ] **Data**: databases/file stores holding both businesses' records; reports/models built on combined data (Power BI, Fabric, data lakes)
- [ ] **Software licences**: parent-held EAs and their affiliate-use/assignment terms (Microsoft EA, Adobe, SAP, Oracle…)
- [ ] **Third-party contracts**: outsourcing, telecom, cloud, support, MSSP
- [ ] **People**: shared-service staff, admins, contractors whose knowledge or employment may move
- [ ] **Security & compliance controls**: certifications (ISO 27001, TISAX, SOC 2), audit evidence and policies owned by the parent that must be re-established

## Approaches

| Approach | How | Works best when | Main risk |
|---|---|---|---|
| Clone-and-go | copy system + config, purge seller data from the copy | speed matters, buyer has no target yet | incomplete purge; clone needs licences the buyer lacks |
| Logical separation | one instance, access + data partitioned by company, under TSA | buyer migrates soon, short TSA acceptable | data leakage; TSA never ends |
| Extract-and-migrate | move the unit's data/processes into the buyer's platform | buyer already runs a suitable platform | mapping effort; hard cutover |
| Rebuild | stand up new systems | legacy near EOL or heavily customised | longest timeline, longest TSA |

Choose by system, not by programme.

**M365 "logical separation" reality check:** inside one tenant you can partition with administrative units, Exchange RBAC scopes / address book policies, information barriers, SharePoint site permissions and `Sites.Selected` app access. But Global Admins, tenant-wide app permissions, audit logs and eDiscovery still see both sides. State this explicitly in the TSA and the DPA.

## Programme steps, outputs, owners

| Step | Output | Owner |
|---|---|---|
| Build and agree the inventory | entanglement register | separation leads (both sides) |
| Define the Day One minimum: bank/payroll, identity & access, email & domains, financial close, customer-facing systems, security monitoring | Day One requirements | buyer separation lead |
| Draft TSA schedules (service level = pre-sale standard) | service catalogue | seller service owners |
| Price + terms: cost-based, base term, extension options with notice, stepped price after base term | priced TSA | deal teams + counsel |
| Plan migration waves: dependency order, test with real data, rollback criteria before each cutover | migration plan | buyer IT |
| Exit service by service, data returned/deleted, stranded costs resolved | TSA exit certificates | both TSA managers |

## TSA scoping rules

- **Longer than the base term may be needed** → agree an extension option with notice period and stepped pricing *now*. Late extensions are priced by whichever side needs them less.
- **Licence can't be extended to a non-affiliate** → the buyer procures its own before Day One, or vendor consent becomes a closing deliverable. Running a non-affiliate on the parent's licence can breach it. *(Microsoft: after closing, the divested users on the seller's EA are typically no longer affiliates. Check the EA's divestiture clause and agree a transition with Microsoft.)*
- **Seller processes the buyer's personal data while providing a service** → DPA under GDPR Art. 28. The seller is usually the buyer's processor.
- **The sold business also serves the seller** → a **reverse TSA** with the same discipline.
- **Term per service**, not one term for everything. Tie each service's end to a migration milestone.
- Pricing: at cost, sometimes with a modest markup, stepping up after the base term. Define how costs are calculated, how third-party costs pass through, and how changes are charged.

## Licences, contracts, data, people

- Licences are often the **slowest** item. Request consents early, and budget for new licences where consent is refused or priced.
- Data separation is harder than infrastructure separation. Decide record by record who owns what. Cleanse clones before handover, including backups, analytics copies and reports. Document what each side deletes.
- EU staff transfer: Directive 2001/23/EC (DE: §613a BGB; UK: TUPE). Plan knowledge transfer with HR and counsel.
- Germany: per-employee log analysis (sign-ins, audit logs) for dependency mapping → **Betriebsrat** co-determination (BetrVG §87(1) Nr. 6). Prefer aggregated/pseudonymised analysis.

## Why TSAs overrun

| Failure | Early signal | Mitigation |
|---|---|---|
| TSA becomes permanent | extension requests before any migration has been tested | tie each service to a migration milestone; monthly joint governance review |
| Seller stranded costs | licences, DC space, contracts sized for the combined group remain after exit | identify them during scoping; reduce contracts in step with each exit (Azure reservations, EA true-down, E5 counts) |
| Service-level disputes | buyer expects improvements; seller delivers the pre-sale standard | define the standard as historical levels with evidence; improvements via change control |
| Buyer can't staff its operations | no hiring plan for roles the TSA covers | recruit or contract a managed service **before** closing for the first-exited functions |

## Cutover discipline (each wave)

- Mock cutover at least once with production-like data
- Go/no-go criteria written before the window (e.g. ≥ 99.5% of mailboxes synced, zero holds in batch, DNS TTL ≤ 300 s)
- Rollback criteria and a tested rollback. For **⚠ one-way** steps (OneDrive/SPO moves, subscription transfer), "rollback" means a forward fix, so say so up front
- Reconciliation afterwards: counts and sizes per mailbox/site and a sample of item-level checks, with the evidence filed
- Comms: users told what changes (new sign-in, MFA re-registration, Teams client switch, mobile re-setup)
