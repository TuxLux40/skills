---
name: migration-planner
description: Plan and run any migration — move data, systems, accounts or infrastructure from one place to another, safely and in the right order. Platform-agnostic and scales from a single person leaving a provider to an enterprise programme. Use when the user says migrate, move, switch, port, transfer, consolidate, decommission, "get off X", "move to Y", lift-and-shift, replatform, re-host, data migration, cutover, go-live, rollback, or asks how to change email/file/hosting/database/SaaS/server/cloud provider, or how to leave a vendor and take their data. Covers: deciding a strategy per item (the 7 Rs), inventory and dependency ordering, data-migration correctness (profiling, mapping, four reconciliation levels), cutover strategy (big-bang / phased / parallel-run / pilot / strangler-fig), go/no-go, rollback, validation and decommission. For a Microsoft 365 / Entra / Azure tenant split or carve-out specifically, prefer the `m365-azure-carve-out` skill; use this one for everything else or when the platform is mixed or non-Microsoft.
---

# Migration planner

Goal: get from "we need to move X from A to B" to a **sequenced plan that migrates in dependency order, proves the data arrived complete and correct, and can be rolled back** — whether X is one person's email or an enterprise's datacenter.

The method, one line: **know what you have → decide a strategy per item → order the moves by dependency → move the data with a dry-run and reconciliation → cut over with a tested rollback → prove it and decommission.**

Nothing here is tied to one vendor. Where a tool helps, neutral/portable ones are named (`rclone`, `rsync`, `imapsync`, `pgloader`, `restic`, …) — swap in whatever fits.

## Match the effort to the scale (don't over-engineer)

The same six steps apply at every size; the ceremony scales. Read `references/by-scale.md` and pick the lane first — doing enterprise governance for a one-person mailbox move wastes everyone's time, and doing a weekend-checklist job on an ERP cutover loses data.

| Scale | Looks like | What to keep, what to drop |
|---|---|---|
| **Individual** | leave Gmail/Dropbox/a host; move to a new laptop; take your data out of a service | Keep: inventory, a backup, reconciliation ("did it all come across?"), DNS/TTL if a domain is involved. Drop: waves, RACI, TSA, command centre. It's a checklist — `templates/individual-checklist.md`. |
| **KMU / SMB** | switch email or file server, move the website/host, change accounting or CRM SaaS, server room → cloud | Keep: inventory + dependencies, strategy per system, a cutover window with rollback, reconciliation, user comms. Light governance: one owner per system. |
| **Enterprise** | datacenter exit, cloud migration, app-portfolio rationalization, post-M&A consolidation | All of it: portfolio assessment, waves, mock cutovers, go/no-go board, reconciliation evidence pack, hypercare, decommission with stranded-cost cleanup. Governance and RACI matter. |

## Ground rules

- **Back up before you move, and verify the backup restores.** The one rule that has no exceptions, at every scale. A migration you can't roll back to is a gamble, not a plan.
- **Reversible until proven.** Never make a change that can't be undone until you're sure it's correct (skilldb migration-strategies). Keep the source intact and read-only during and after the move until reconciliation passes and a grace period elapses — then decommission deliberately, not as a side effect.
- **Prefer parallel over big-bang** where the data coupling allows it: stand the new beside the old, move in slices, remove the old only once the new is proven (strangler-fig / expand-contract). Big-bang only when temporary interfaces would cost more than one clean outage.
- **A "temporary" bridge with no deadline becomes permanent.** Give every coexistence/sync/compatibility shim an owner and an end date.
- **One-way doors get labelled ⚠.** Deleting the source, releasing a domain, cancelling the old subscription, porting a number, overwriting the target — mark them in the plan and do them last, after verification.
- **Scripts that move data are dry-run first, idempotent, resumable, batched, and reconciled after.** See `references/data-migration.md`.

## Workflow

### 0. Frame it (ask first)
1. **What's moving, from where to where?** The item(s), source platform, target platform.
2. **Why?** Cost, end-of-life, a deal, consolidation, leaving a vendor, better tool. The reason sets what "done" means.
3. **What can't break, and for how long can it be down?** The tolerance for downtime and for data loss (RTO/RPO, even informally — "email can be down an evening but not a day").
4. **Scale & governance** — individual / KMU / enterprise (sets the lane above).
5. **Deadline / forcing event** — contract end, lease expiry, licence renewal, closing date.
6. **Constraints** — regulatory (GDPR, financial/medical records), data residency, who must sign off.

### 1. Inventory what you have
List every item in scope and what it holds. At small scale this is a spreadsheet of accounts/files; at enterprise scale it's an application-portfolio assessment. For each item capture: name, type, owner, size/volume, criticality, and — critically — **what it depends on and what depends on it** (the app → its database → its auth → its DNS name → the firewall rule). `references/discovery.md` lists what to look for per domain and how to find dependencies you can't see from config alone (observed traffic, logs, "what breaks if we turn it off"). Template: `templates/inventory.example.csv` + `templates/deps.example.csv`.

### 2. Decide a strategy per item — the 7 Rs
Not everything should move the same way, and some things shouldn't move at all. For each item pick one (full guide + decision tree in `references/strategy-7rs.md`):

**Retire** (switch it off — nobody needs it) · **Retain** (leave it where it is, for now, with a review date) · **Rehost** (lift-and-shift, no changes) · **Relocate** (move at the hypervisor/container level) · **Repurchase** (drop-and-shop: replace with a different product/SaaS) · **Replatform** (lift-and-reshape: small changes to fit the target) · **Refactor** (re-architect — most work, do it rarely and rarely *during* the move).

A big chunk of value is in **Retire** and **Retain**: the cheapest thing to migrate is the thing you don't.

### 3. Order the moves by dependency
Something that others depend on moves (or gets a bridge) before the things that depend on it. Feed the inventory and dependencies to the planner — it produces dependency-ordered **waves** and flags circular dependencies (which you break with a temporary bridge):
```bash
python3 scripts/wave_planner.py --items templates/inventory.example.csv --deps templates/deps.example.csv --out out/plan
```
Output: `waves.csv` (each item's wave number), `summary.md` (the wave plan + a Mermaid dependency diagram + any cycles to resolve), ranked by risk×effort within each wave. Typical generic order: **identity/accounts → DNS/networking → data stores → the apps on them → integrations/automation → endpoints/clients → decommission the source.**

### 4. Move the data — correctly
The heart of most migrations. Profile the source first, write down the mapping, move with a dry-run, then **reconcile at four levels** (counts → control/hash totals → field-level → business-process). Full method, reject handling and the evidence pack: `references/data-migration.md`. For a simple file/mailbox copy this collapses to "copy, then check counts and spot-check content"; for a regulated ledger it's the full evidence pack.

### 5. Cut over — with a tested rollback
Choose the cutover strategy (big-bang / phased / parallel-run / pilot), build a **runbook** of timed, owned tasks, **rehearse it on a copy** until the timings are real, set **go/no-go criteria with named evidence**, and write the **rollback and its point-of-no-return before you start**. Lower DNS TTLs days ahead if a cutover involves a domain. Full method: `references/cutover-rollback.md`, runbook template: `templates/migration-runbook.md`.

### 6. Validate, then decommission
Reconciliation and real-process tests pass → run a grace/hypercare period with the source still available → then decommission the source deliberately: cancel subscriptions, release licences/reservations, remove the temporary bridges, archive under the retention schedule, and clear **stranded costs** (contracts/capacity sized for the old world). Deleting the source is the last ⚠ one-way door — do it only after sign-off.

## Output contract
Deliver (scaled to the lane):
1. **Scope & assumptions** — the step-0 answers, downtime/data-loss tolerance, open questions.
2. **Inventory** with the 7-R strategy per item (incl. what you're retiring/retaining).
3. **Wave plan** — dependency-ordered, cycles flagged, ⚠ one-way doors marked.
4. **Data plan** — mapping + which reconciliation levels apply.
5. **Cutover + rollback** — strategy, go/no-go criteria, the way back, the point of no return.
6. **Sources** for any provider-specific limit you quote (verify current docs; limits change).

Offer to write the plan into the user's knowledge base — migrations run long and decisions get lost.

## References
- `references/strategy-7rs.md`: the 7 Rs with a decision tree and worked examples at each scale
- `references/discovery.md`: inventory + dependency discovery per domain, incl. finding hidden runtime dependencies
- `references/data-migration.md`: profiling, mapping spec, the four reconciliation levels, rejects, evidence pack, portable tools
- `references/cutover-rollback.md`: cutover strategies, runbook, mock cutovers, go/no-go, rollback, DNS/TTL
- `references/by-domain.md`: concrete playbooks — email, files, web+DNS, databases, servers/cloud, SaaS, accounts/secrets, domains/phone numbers
- `references/by-scale.md`: how the method shrinks to a checklist and grows to a programme
- `references/sources.md`: source URLs and what each contributed
