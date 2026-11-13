# Sources

Checked 2026-11-13.

| Source | Contributed |
|---|---|
| AWS Prescriptive Guidance — migration strategies (the 7 Rs) https://docs.aws.amazon.com/prescriptive-guidance/latest/large-migration-guide/migration-strategies.html | the 7 Rs (retire, retain, rehost, relocate, repurchase, replatform, refactor), applied at portfolio level; "infrastructure strategy follows the application"; refactor is highest-complexity, avoid at scale |
| AWS Prescriptive Guidance — iterating 7 Rs selection https://docs.aws.amazon.com/prescriptive-guidance/latest/application-portfolio-assessment-guide/iterating-7-rs-migration-strategy-selection.html | R per application drives the wave plan |
| ColdAI — Data migration validation & reconciliation https://coldai.org/capabilities/implementation/data-migration-reconciliation/ | completeness/accuracy/integrity/usability; source profiling; mapping specification; the four reconciliation levels; reject dispositions; evidence pack; regulatory triggers (SOX, 21 CFR Part 11, BCBS 239, GDPR) |
| ColdAI — Cutover planning: runbook, go/no-go, rollback https://coldai.org/capabilities/implementation/cutover-planning/ | big-bang/phased/parallel/pilot comparison; freeze→load→reconcile→smoke→go/no-go→open sequence; mock cutovers; go/no-go criteria with named evidence; point of no return; command centre; hypercare |
| ColdAI — Strangler fig modernization https://coldai.org/capabilities/implementation/strangler-fig-modernization/ (referenced) | incremental replace-in-place pattern for live systems |
| SkillDB — Migration Strategies https://skilldb.dev/skills/autonomous-agent-skills/migration-strategies | reversible-until-proven; expand-contract schema change; dry-run / idempotent / resumable / batched scripts; rollback written before cutover; "temporary bridge" anti-pattern; feature-flag rollouts |

Portable tools named in `references/` (rclone, rsync, restic/borg, imapsync, pgloader, ora2pg, virt-v2v, Debezium, Terraform/Ansible) are standard open/neutral utilities — no single vendor. Provider-specific limits are deliberately not hard-coded; verify against current docs at plan time.
