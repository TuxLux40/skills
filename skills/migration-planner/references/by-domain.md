# Per-domain playbooks

Concrete, vendor-neutral patterns for the migrations people actually run. Each names the gotcha that bites and the ⚠ one-way step. Verify any specific provider limit against current docs — they change.

## Email / mailboxes
- **Path:** provision target mailboxes → migrate with `imapsync` (IMAP→IMAP, incremental, maps folders) or provider-native import → set up mail routing/forwarding during coexistence → cut MX over → stop forwarding once quiet.
- **Reconcile:** message counts per folder (L1), spot-check old mail + send/receive test (L4).
- **Gotchas:** mailbox-size/item limits; shared mailboxes, calendars, delegates and rules usually **don't** copy — re-create them; aliases and distribution lists; signatures. Litigation/legal holds may block export.
- **⚠ one-way:** removing the domain from the old provider / releasing it; deleting source mailboxes. Keep the old mailbox as archive/forwarding for a grace period.

## Files / storage
- **Path:** `rclone`/`rsync` with `--dry-run` → initial bulk copy (source read-only or snapshot) → incremental delta syncs → final sync in the window → `rclone check`/checksums.
- **Reconcile:** file count + total bytes (L1/L2), checksum sample or full (L3), open a sample (L4).
- **Gotchas:** permissions/ACLs and sharing links rarely survive — plan to re-apply; path-length limits; special characters; versions and metadata (created/modified/by); huge files; preserve timestamps (`--times`).
- **⚠ one-way:** deleting the source share; overwriting target if a merge is needed (most tools won't merge — target must be empty).

## Website + DNS
- **Path:** stand up the site on the new host → test via hosts-file override or a staging URL → lower DNS TTL days ahead → cut records over in the window → verify from multiple resolvers → keep old host live until traffic moves.
- **Gotchas:** TLS certificates (re-issue/transfer; watch HSTS), email records (SPF/DKIM/DMARC/MX — don't lose them when you move the zone), redirects and SEO (preserve URLs, 301s), CDN config, database connection for a CMS.
- **⚠ one-way:** transferring the domain registrar (slow, can lock for days); decommissioning the old host.

## Databases
- **Path:** schema first → bulk load (`pg_dump`/`pgloader`/`ora2pg`/native) → for low downtime, logical replication / CDC to keep target in sync → cut writes over in a short window → reconcile.
- **Pattern for schema change:** **expand-contract** — add new alongside old, write both, backfill, switch reads, stop writing old, drop old. Never a destructive change before the code that uses it is gone.
- **Reconcile:** row counts per table by segment (L1), control totals on amounts + checksums on keys (L2), full/sample field compare (L3), run a real query/report (L4).
- **Gotchas:** dialect differences (types, sequences, collation, functions), foreign-key integrity, character encoding, large objects.
- **⚠ one-way:** dropping source tables; the write cutover.

## Servers / cloud / VMs
- **Path:** choose the R (rehost/relocate/replatform) → rebuild from IaC (Terraform/Ansible) *or* image/VM export-import (`virt-v2v`, cloud migration service) → sync data → repoint DNS/load-balancer → smoke test → decommission.
- **Gotchas:** IP/hostname changes rippling into configs and firewall rules; licences tied to hardware IDs; secrets/certs; outbound dependencies (NTP, package mirrors, licence servers); monitoring/backup re-pointing.
- **⚠ one-way:** terminating the old instances; releasing reserved capacity (a stranded cost if done too early *or* too late).

## SaaS → SaaS
- **Path:** export from source (API or built-in export) → map fields to the target's model → import (API/CSV) → re-create integrations, automations, webhooks, SSO → re-invite users.
- **Gotchas:** export fidelity (attachments, history, custom fields often lost), rate limits on the API, record-ID remapping breaking links, per-seat licensing overlap during coexistence, data-residency.
- **⚠ one-way:** cancelling the old subscription (keep read access through the grace period); anything that can't be re-exported.

## Accounts, passwords, secrets, 2FA
- **Path (individual/team):** export from the old password manager → import to the new → re-enrol 2FA/passkeys on the critical accounts → **repoint account-recovery email/phone** to the new ones → verify login on each important account → then close the old.
- **Gotchas:** 2FA seeds usually **don't** transfer — you re-enrol per account; passkeys are device/platform-bound; SSH/GPG keys and API tokens need rotating, not copying, if the old store is leaving your control; recovery codes.
- **⚠ one-way:** closing the old email/account that other services use for recovery — do this **last**, after confirming nothing still depends on it.

## Phone numbers / domains (porting)
- **Gotchas:** porting is provider-to-provider with its own lead time and a window you don't fully control; the number/domain can be unreachable briefly; **don't cancel the old service before the port completes** (cancelling releases it and can kill the port).
- **⚠ one-way:** the port itself; cancelling the losing service.
