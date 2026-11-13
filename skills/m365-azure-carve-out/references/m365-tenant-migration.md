# Microsoft 365 tenant-to-tenant migration (native tools)

Status as checked 2026-11-13 against Microsoft Learn. **Re-verify limits and licensing before committing**, because they change, and the docs contradict each other in places (noted below).

Hub: https://learn.microsoft.com/microsoft-365/migration/?view=o365-worldwide

## Choosing the toolset

| Approach | Best for | Tool |
|---|---|---|
| Multi-workload orchestrated | mailboxes + OneDrive + Teams chats + meetings, per user, in coordinated batches | **Migration Orchestrator** |
| Individual workload | one workload, or granular control of each timeline | Cross-tenant mailbox / OneDrive / SharePoint tools |
| Third-party / partner | shared data the native tools skip (Teams channels, Planner, Power Platform, public folders), delta passes, coexistence tooling | Quest On Demand Migration, ShareGate, AvePoint Fly, BitTitan, etc. |

Migration architecture models: **single event** (small/medium orgs), **phased** (large orgs, requires coexistence), **tenant move/split** (a subset moves, others stay: typical for a divestiture).

## Licensing

- **Cross-Tenant User Data Migration**: per user, one-time fee, assigned on **source or target** user. Covers mailbox + OneDrive (and orchestrated Teams chats/meetings). Add-on for M365 Business Basic/Standard/Premium, M365 F1/F3/E3/E5, O365 F3/E1/E3/E5, Exchange Online, SharePoint, OneDrive, EDU. Available via EA, CSP, Web Direct. Without it the moves fail (`CrossTenantMigrationWithoutLicensePermanentException`). Microsoft makes no exceptions.
- **Cross-Tenant Shared Data Migration** (SharePoint sites): per **100 GB moved**, EA customers only, via the Microsoft account team. Size it with `Get-SPOSite -Limit All | Select Url, StorageUsageCurrent`. There's 20% grace for growth.
- **FastTrack cross-tenant service**: invitation only, minimum 150 licenses, needs the User Data Migration SKU. Covers EXO, SharePoint and OneDrive data only. Not Teams, M365 Groups, Planner, Stream, Power Platform, devices. Not available for US Gov/EDU.
- Migrations have **no SLA**. Throughput depends on volume and service load.

## Identity mapping comes first

The tools move **content, not identities.** You create and configure the target users. Identity mapping (`cross-tenant-identity-mapping`) must succeed before moves, and the Orchestrator needs each user to be a **mailbox in source** and a **MailUser in target** even if mail isn't moving.

Licensing order in the target matters:
1. Create the target MailUser with `ExchangeGuid`, `ArchiveGuid` (if there's an archive), the source `LegacyExchangeDN` as an `x500:` proxy, and all proxy addresses.
2. **Only then** assign the Exchange Online license. Licensing first provisions a fresh mailbox and breaks the move. Safest: license after the move, within the 30-day grace period.
3. Block OneDrive creation for target users (restrict site creation) until their move. An existing target OneDrive makes the move fail. It can't be merged or overwritten.
4. Teams license gives the SIP domain. If it's missing, fix it with `Set-CsUser`.

If a target object once had a mailbox: `Set-User <id> -PermanentlyClearPreviousMailboxInfo`. **⚠ irreversible.** Any soft-deleted mailbox is gone.

## Cross-tenant mailbox migration

https://learn.microsoft.com/microsoft-365/migration/cross-tenant-mailbox-migration

- **Configure target first.** Target creates the migration app in Entra (`Mailbox.Migration` permission, secret), migration endpoint, and an **organization relationship** to the source tenant ID. The source consents to the app, and its org relationship is scoped by a **mail-enabled security group** of movable mailboxes. Use multiple groups above 10,000 users. Nested groups work but aren't recommended. Admins of each side can do their part without the other's credentials.
- Start with `New-MigrationBatch` and a CSV.
- **Blocks:** mailboxes on any hold (litigation, retention, eDiscovery) are blocked. Talk to Microsoft before trying to move them.
- **Moves only user-visible content** (mail, calendar, contacts, tasks, notes). Journaling and public folders don't move. Permissions, delegates and inbox rules may need re-creating. Plan to re-apply delegations from your inventory.
- After the move: the source mailbox becomes a MailUser with `targetAddress` → target. This gives coexistence and mail routing. The source mailbox is **gone**: no eDiscovery in source afterwards. If legal needs a copy, copy it to another mailbox *before* the move.
- Two Entra Connect instances (one per tenant) on the same AD are supported. Use OU-scoped sync for in-scope users instead of the pre-provisioning script, and check that `msExchMailboxGUID` and `proxyAddresses` on-prem are correct, or you get duplicate mailboxes.
- Distribution lists and mail contacts aren't part of the move. Pre-create them in the target.

## Cross-tenant OneDrive migration

https://learn.microsoft.com/microsoft-365/migration/cross-tenant-onedrive-migration

- `Set-SPOCrossTenantRelationship` on both sides → `Get-SPOCrossTenantCompatibilityStatus` (must be Compatible/Warning) → identity mapping file → `Start-SPOCrossTenantUserContentMove` → `Get-SPOCrossTenantUserContentMoveState`.
- **Up to 4,000** OneDrive/SharePoint moves scheduled at a time. This queue is **shared** with SharePoint site moves, and with Multi-Geo it applies per source geo.
- **⚠ One-shot move. There's no incremental/delta pass.** A redirect is left in source, so old links keep working. The OneDrive is read-only for minutes during the move.
- **Blocks:** source tenant with **Customer Key / BYOK** (fails), source OneDrive set read-only, existing target OneDrive, OneDrive on legal hold, path > **400 characters** (target URL + source path, so keep target UPN/URLs short), apostrophe in the UPN/URL, government clouds (GCC/GCC High/DoD).
- Size limit: **docs disagree.** The main page says 5 TB / 1M items, the FAQ says 2 TB / 1M items. Items include versions, folders and list rows. Verify with Microsoft and treat 2 TB as the safe planning value.
- `MnAPartnersFarmsAreIncompatible`: wait at least 48 h after setting up trust, then recheck.

## Cross-tenant SharePoint migration

https://learn.microsoft.com/microsoft-365/migration/cross-tenant-sharepoint-migration

- Same trust/identity-map mechanism. EA + Shared Data Migration license.
- Pre-create users, groups, and the **M365 groups for group-connected sites** in the target.
- **⚠ One-shot move**, with a redirect left in source. Same 400-char path limit and 4,000 queue.
- FastTrack scope moves documents, structure, user/group permissions, sharing links, versions and basic metadata. It does **not** move SharePoint workflows, apps, Power Apps/automation, sites > 5 TB / 1M items, or corrupted items.
- Multi-Geo: establish trust per geo instance and upload the identity map to every target instance. A site moved to the wrong geo can't be fixed with this tool. Use the Multi-Geo move commands.

## Migration Orchestrator

https://learn.microsoft.com/microsoft-365/migration/migration-orchestrator-1-overview

- Four workloads per batch: **Exchange mailboxes, OneDrive, Teams chats, Teams meetings.** Run them together in one batch. It sequences the dependencies itself. Selecting meetings without chats + mailboxes fails.
- `CompleteAfterDate`: before it, only the Exchange sync runs in the background. After it, the mailbox cuts over, then OneDrive/chats/meetings.
- **Not in scope: shared data, meaning Teams teams & channels and SharePoint sites.** These stay in source and need the SharePoint tool or a third party.
- Teams chats: content is copied, and the source stays accessible but isn't synced afterwards. Duplicate/temporary threads appear during phased moves. Not migrated: self-chats, chats started by external users or departed/unlicensed users, reactions, apps/polls, messages > 4 MB, deleted messages.
- Teams meetings: only the default calendar, max 250 attendees. Not migrated: recordings/transcripts/recaps, channel meetings, webinars/town halls/live events, cancelled meetings, modified occurrences of series, room-organized meetings, Confidential/Highly Confidential. All RSVPs reset.
- **Don't remove the source mail forwarding or delete source objects before all batches finish.** Once they're deleted, the same users can't be migrated to a different target again.
- Running `Remove-CTIMData` during running batches corrupts the identity map for already-migrated users. Add users without it.

## Coexistence during a phased split

- Mail routing via the source MailUser `targetAddress` (automatic after the move) plus shared-namespace routing if the domain is still in source.
- Free/busy: organization relationships both ways.
- Teams: external access / federation between the tenants, B2B direct connect for shared channels.
- Optional: **cross-tenant synchronization / multitenant organization (MTO)** to provision each side as B2B members in the other for the TSA period. See `identity-ad-entra.md`.

## Domain move: the hard cutover

A verified domain can exist in **one tenant only**.
1. Remove it from **every** object in source: UPNs, primary/proxy SMTP addresses, groups, DLs, rooms/resources, SIP addresses, SharePoint public-site references. Reset to `*.onmicrosoft.com`.
2. Remove the domain from the source tenant. Release can take **up to 72 h** in practice (plan for it, and test with a low-value domain first if you have one).
3. Add and verify the domain in the target (TXT). Microsoft-hosted DNS domains complicate verification, so move DNS to an external provider beforehand.
4. Re-stamp UPNs/addresses in the target, then fix MX, SPF, DKIM, DMARC and Autodiscover.
5. Lower the MX TTL days ahead. Consider a mail queueing/backup MX service to avoid NDRs during the window.

Alternative that avoids the window: the divested unit keeps its own domain and the parent never owned it. Or use a **new** domain plus a re-brand, and keep the old domain on the source with forwarding under TSA.

## Also check (not covered by the native tools)

Power Platform environments (separate T2T process in the Power Platform admin center, needs destination approval), Planner, Stream (on SharePoint), Forms, Bookings, Loop workspaces, Viva, Copilot agents and their knowledge sources, Purview (retention policies, labels, DLP: re-create in the target, and encrypted content needs re-protection), Intune policies and devices (re-enroll), phone system / Teams Phone numbers (port), third-party SaaS SSO (re-federate to the target tenant).
