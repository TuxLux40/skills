# Scaling the method: individual → KMU → enterprise

Same six steps everywhere; the ceremony scales. Over-governing a small move wastes time; under-planning a big one loses data. Pick the lane, then apply only that column.

| Step | Individual | KMU / SMB | Enterprise |
|---|---|---|---|
| **0. Frame** | one sentence to yourself: what, from where to where, by when | a short brief, agreed with whoever's affected | formal scope, RTO/RPO, regulatory constraints, sign-off authority |
| **1. Inventory** | a list: accounts, where files live, what uses your email | a spreadsheet; ask each team what they use | portfolio assessment + CMDB + observed dependency mapping; its own workstream |
| **2. Strategy (7 Rs)** | retire the junk, repurchase/rehost the rest | one R per system, one owner each | R per application, portfolio-wide, with rationalization |
| **3. Waves** | usually one or two obvious steps | a handful of waves over a few evenings/weekends | many waves over months; `wave_planner.py` earns its keep; dependency cycles are real |
| **4. Data** | copy, then count & spot-check | counts + control totals + spot-check; mapping if shapes differ | full four-level reconciliation, mapping spec under version control, evidence pack |
| **5. Cutover** | do it on a quiet evening; keep the old until sure | a planned window, a written rollback, user comms | mock cutovers, go/no-go board, command centre, DNS TTL lowered ahead |
| **6. Validate & decommission** | check it works for a week, then delete the old | reconcile, short grace period, cancel old service | hypercare, signed acceptance, decommission + stranded-cost cleanup |

## What only matters at enterprise scale
- **Governance / RACI** — one Accountable per workstream; who signs go/no-go. (Below enterprise, "the owner decides" is enough.)
- **TSA / transition services** — only in carve-outs/divestitures where another company keeps running something for you temporarily.
- **Evidence pack & auditors** — when data feeds financial reporting, regulated records, or risk data.
- **Command centre & hypercare staffing** — a room running the cutover against the clock.

## What individuals must not skip (even though it's "small")
- **A verified backup before you move.** Non-negotiable at every size.
- **Count check after copying.** "Looks done" hides silent loss.
- **Recovery-email/2FA repointing before closing the old account.** The classic self-lockout.
- **Keep the old thing until the new one is proven.** Don't cancel/delete on day one.

## What enterprises most often get wrong
- Skipping **Retire/Retain** — migrating dead weight because inventorying what to kill felt like extra work.
- **Refactoring during the move** — turning a migration into a rebuild and missing the date.
- **Untested rollback** and late, uncontrolled runbook edits.
- A **"temporary" coexistence bridge** that outlives the programme because no one gave it a deadline.
- Decommissioning too early (breaks a missed dependency) or too late (stranded cost).
