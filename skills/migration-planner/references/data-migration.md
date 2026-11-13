# Moving the data correctly

Most migrations live or die here. The discipline is the same whether you're copying a photo library or a customer ledger — the *amount* of it scales. Core principle: **a migration is only done when you've proven the data arrived complete and correct**, not when the copy job exits 0.

## Script discipline (any data-moving job)

- **Dry-run first.** The job reports what it *would* do before it does it. Never let the first real run be the first run.
- **Idempotent.** Running it twice = running it once. Safe to re-run after a partial failure.
- **Resumable.** If it dies at 60%, it restarts near 60%, not at 0. (`rclone`, `rsync`, `restic`, `imapsync` all checkpoint; a hand-written loop needs a cursor.)
- **Batched.** Process in chunks; don't load millions of rows into memory or hold one giant transaction.
- **Logged + reconciled.** Count what you read and what you wrote; compare at the end. Log rejects with a reason, don't silently skip.
- **Keep the source read-only and intact** until reconciliation passes and the grace period ends.

## Profile the source before you write any mapping

Measure what the data *actually* contains, not what the schema claims: empty-field rates, distinct values/formats, codes missing from lookup tables, duplicates, orphaned child records, out-of-range dates. Do it at the start — what you find changes the mapping and surfaces cleansing decisions only the business/owner can make. **Re-profile before every rehearsal:** live data keeps changing, and a rule that handled every case in spring meets a new value by autumn.

## Mapping specification (when source ≠ target shape)

For each target field record: source field(s) incl. joins/filters · transformation rule (written so a tester can recompute it independently) · defaults & lookups for empty/unmatched · the owner who agreed the rule · change history. Keep it in version control beside the migration code so each reconciliation names the mapping version it tested.

Cleanse **at source** whenever the source is still live (the fix helps today and survives reloads); use a transformation rule for systematic patterns; avoid manual fixes in staging between runs — they don't repeat and can't be evidenced.

## The four reconciliation levels

Run all four that apply, in every rehearsal and the final run. Each catches what the one before can't.

| Level | Compare | Catches | Misses |
|---|---|---|---|
| **1 — counts** | records per entity, by segment (status/region/type) | dropped/duplicated records, wrong filters | wrong values in records that did arrive |
| **2 — control & hash totals** | sums of amounts/quantities; checksums of key fields, per segment | truncated amounts, sign errors, altered identifiers | offsetting errors; wrong non-numeric fields |
| **3 — field-level** | every field of every record (or a stratified sample) vs the expected value | transformation & mapping errors | process-level problems with individually-correct data |
| **4 — business-rule / process** | real processes run on migrated data (a report, a billing run, a login) | broken relationships; data the new system can't use | little, once 1–3 pass |

**Level 3 — full vs sample:** where it can be automated, compare *every* record (recompute expected from source, diff against loaded) — automation makes full comparison cheaper than arguing about sample sizes. Sample only for checks needing human judgement (does this record look right on screen), stratified by segment/value/age so high-value and odd records are always included.

At small scale this collapses sensibly: a mailbox copy = Level 1 (message counts per folder) + a Level 4 spot-check (open five old emails, send a test). A file move = count + total bytes (L1/L2) + open a sample (L4). Don't skip L1 — "it looked like it worked" is how silent data loss happens.

## Rejects & exceptions — every failed record gets a disposition and an owner

- Error in a live source → **fix at source** (survives reloads).
- Systematic pattern → **transformation rule** with sign-off.
- Obsolete → **exclude**, archive under retention, record it.
- Must exist but unresolved → **quarantine/suspense** status with an owner and a deadline.
- Affects financial balances → **no acceptance without finance sign-off.**

## Evidence pack (regulated / audited migrations)

Scope & inventory (incl. deliberate exclusions) · profiling report + cleansing decisions with owners · mapping-spec version used · reconciliation results by level and run (rehearsals + final, with breaks and resolutions) · rejects log with dispositions · sampling method & results · signed business acceptance per entity, plus finance for balances. Auditors look at migration controls when the data feeds financial reporting (SOX), FDA predicate-rule records (21 CFR Part 11), bank risk data (BCBS 239), or EU personal data (GDPR — keep it accurate, and don't migrate personal data you've no reason to keep).

## Portable tools (neutral — pick what fits)

- **Files / object storage:** `rclone` (70+ backends, `--dry-run`, `check`, resumable), `rsync` (local/SSH), `restic`/`borg` (dedup backup = your rollback copy), `aws s3 sync`/`gsutil rsync`/`azcopy` for same-cloud.
- **Mail:** `imapsync` (IMAP→IMAP, incremental, folder mapping), provider-native import where it exists.
- **Databases:** `pg_dump`/`pg_restore`, `mysqldump`, `pgloader` (incl. MySQL/MSSQL→Postgres), `ora2pg` (Oracle→Postgres); logical replication / CDC (Debezium) for near-zero-downtime.
- **Whole machines:** image/VM export-import, `virt-v2v`, cloud migration services, or rebuild-from-IaC (Terraform/Ansible/Bicep) + data sync.
- **Verify integrity:** checksums (`sha256sum`, `rclone check`), row counts + control totals via SQL.
