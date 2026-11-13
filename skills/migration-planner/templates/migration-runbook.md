# Cutover runbook — <migration name>

Fill this in, rehearse it on a copy, then freeze it under change control. Every task has one owner, a duration, and its predecessors. Mark the critical path and the ⚠ point of no return.

## Summary
- **Window:** <start> → <end>  ·  **Strategy:** big-bang / phased / parallel / pilot
- **Cutover manager:** <name>  ·  **Go/no-go owner (final vote):** <name>
- **Rollback deadline (point of no return):** <time/step>

## Pre-cutover (days ahead)
| # | Task | Owner | When | Done |
|---|---|---|---|---|
| P1 | Verified backup of source taken and test-restored | | | ☐ |
| P2 | DNS TTL lowered to ≤300s on records to be changed | | | ☐ |
| P3 | Final rehearsal completed within window + buffer | | | ☐ |
| P4 | Users/customers/suppliers notified | | | ☐ |
| P5 | Rollback procedure tested | | | ☐ |

## Cutover tasks (in order)
| # | Task | Owner | Backup | Depends on | Est. | Actual | Crit? | Done |
|---|---|---|---|---|---|---|---|---|
| 1 | Freeze changes on source | | | — | | | | ☐ |
| 2 | Stop integrations / scheduled jobs | | | 1 | | | | ☐ |
| 3 | Final data extract + load | | | 1 | | | ✔ | ☐ |
| 4 | **Reconciliation checkpoint** (L1/L2 pass?) | | | 3 | | | ✔ | ☐ |
| 5 | Switch DNS / routing / connections | | | 4 | | | ✔ | ☐ |
| 6 | Technical smoke tests (login, a real process) | | | 5 | | | ✔ | ☐ |
| 7 | **GO / NO-GO decision** | | | 6 | | | ✔ | ☐ |
| 8 | ⚠ POINT OF NO RETURN — enable writes on target | | | 7 | | | ✔ | ☐ |
| 9 | Open to users / re-enable integrations | | | 8 | | | | ☐ |

## Go/no-go criteria (evidence named, decided in advance)
- [ ] Backup verified and restorable — evidence: <restore test log>
- [ ] Reconciliation L1 + L2 pass, no unexplained break — evidence: <recon report>
- [ ] Smoke tests pass (a real login + a real process) — evidence: <test results>
- [ ] All critical-path supplier/infra dependencies confirmed in writing
- [ ] Known defects have agreed workarounds briefed to super-users

## Rollback
- **Triggers (any of):** unexplained blocking recon break · smoke test fails · critical dependency unconfirmed · overrun past the point-of-no-return deadline
- **Procedure:** <step-by-step back to source — re-point DNS/routing, re-enable source writes, notify>
- **Point of no return:** task 8. After it, rollback = forward-fix only; data created on the new system would be lost on a revert.
- **Data created during window captured by:** <owner / how re-keyed>

## Post-cutover
- [ ] Hypercare staffed; issue triage running
- [ ] Source kept read-only & available during grace period (<length>)
- [ ] Reconciliation L3/L4 complete; business sign-off obtained
- [ ] Decommission source; cancel subscriptions/licences; remove temporary bridges; clear stranded costs
