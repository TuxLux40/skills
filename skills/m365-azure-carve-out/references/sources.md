# Sources

Checked 2026-11-13.

| Source | Contributed |
|---|---|
| Coherence: *IT Carve-Out Strategy vs Full Enterprise Integration* https://coherence.us/coherence-blogs/it-carve-out-strategy-enterprise/ | carve-out vs integration decision; early dependency questions (shared infra, identity/auth, compliance, downtime tolerance); phased approach; governance |
| Coherence: Tenant migration https://coherence.us/tenant-migration/ | pre-migration / migration / post-migration phasing; manual vs third-party vs hybrid approaches. Mostly a service page. |
| Coherence: Active Directory migration https://coherence.us/active-directory-migration/ | AD migration = moving users, computers and apps between domains; Entra Domain Services as a landing option for legacy directory-aware apps. Mostly a service page. |
| ColdAI: *Carve-Out IT Separation and TSA Planning* https://coldai.org/capabilities/mergers-acquisitions/carve-out-tsa/ | the six-step sequence, entanglement checklist, four approaches, programme steps/owners, TSA scoping rules, overrun signals, licences/data/people (GDPR Art. 28, Directive 2001/23/EC) |
| Microsoft 365 migration hub https://learn.microsoft.com/microsoft-365/migration/?view=o365-worldwide | tool map |
| Plan a tenant-to-tenant migration https://learn.microsoft.com/microsoft-365/migration/microsoft-365-tenant-to-tenant-migrations | approach table, workload dependencies, coexistence |
| Migration Orchestrator overview / end-user experience https://learn.microsoft.com/microsoft-365/migration/migration-orchestrator-1-overview · …-7-end-user-exp | workloads, CompleteAfterDate, scope exclusions, Teams known issues, licensing |
| Cross-tenant mailbox migration https://learn.microsoft.com/microsoft-365/migration/cross-tenant-mailbox-migration | prerequisites, licensing, MailUser prep, holds, FAQ on two Entra Connects |
| Cross-tenant OneDrive migration + FAQ https://learn.microsoft.com/microsoft-365/migration/cross-tenant-onedrive-migration · …-faqs | cmdlets, 4,000 queue, one-shot, blocks, size limits (5 TB vs 2 TB conflict) |
| Cross-tenant SharePoint migration https://learn.microsoft.com/microsoft-365/migration/cross-tenant-sharepoint-migration | EA-only, per 100 GB, multi-geo |
| FastTrack cross-tenant migration https://learn.microsoft.com/microsoft-365/fasttrack/cross-tenant-migration | what does/doesn't migrate, 150-seat minimum, exclusions |
| Transfer an Azure subscription to a different Entra directory https://learn.microsoft.com/azure/role-based-access-control/transfer-subscription | impact matrix, discovery commands, CSP restriction, alternatives (re-deploy, Lighthouse) |
| Defender for Cloud: Map IaC templates to cloud resources https://learn.microsoft.com/azure/defender-for-cloud/iac-template-mapping | IaC → resource → repo mapping, prerequisites (CSPM, Azure DevOps, IaCFileScanner, `yor_trace`/`mapping_tag`), 12 h latency |
| Cross-tenant synchronization https://learn.microsoft.com/entra/identity/multi-tenant-organizations/cross-tenant-synchronization-overview | coexistence provisioning settings |
| Migrate mailboxes across tenants (legacy / third-party guidance) https://learn.microsoft.com/exchange/mailbox-migration/migrate-mailboxes-across-tenants | domain removal steps, MX/TTL cutover |
| Power Platform tenant-to-tenant https://learn.microsoft.com/power-platform/admin/move-environment-tenant | environment moves need destination approval |
