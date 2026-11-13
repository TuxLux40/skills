# Discovery & dependency mapping

How to find **relations and dependencies** in an M365 / Entra / AD / Azure estate, and how to turn them into a graph you can cut.

There are two kinds of evidence, and you need both:

- **Declared** (configuration): memberships, ownerships, permissions, RBAC, peerings, connectors. This is complete for what's configured, but blind to what is actually used.
- **Observed** (runtime): sign-ins, Kerberos tickets, network flows, mail flow. It shows real use, but only within the retention window (often 30 days), so it misses quarterly and annual jobs such as year-end close, audits and DR tests.

Rule of thumb: declared evidence finds the edges. Observed evidence tells you which edges are **live** and how critical they are. Anything that is only declared and older than the log window is a *"confirm with the owner"* item, not a safe delete.

---

## Graph schema (what `edges.csv` contains)

```
src_id,src_type,rel,dst_id,dst_type,evidence,source
```

| rel | meaning | propagates owner label? |
|---|---|---|
| `member_of` | user/group → group (incl. nesting) | yes (child → parent counts as usage) |
| `owns` | user → group/site/app/team/mailbox/subscription | yes |
| `contains` | MG → subscription → RG → resource; OU → object | yes (parent → child) |
| `delegate_of` | user → mailbox (FullAccess/SendAs/SendOnBehalf) | no, but it's an entanglement if it crosses sides |
| `assigned_to` | user/group → enterprise app (app role assignment) | no |
| `consented` | SP → API (OAuth2 grant / app role) | no |
| `role_on` | principal → scope (Entra role or Azure RBAC) | no |
| `signs_into` | user/SP → app (observed) | no (weight = count) |
| `linked_to` | site ↔ M365 group ↔ team | yes |
| `peers_with` / `private_link_to` / `dns_link` / `routes_via` | network | no |
| `uses_domain` | object → accepted/verified domain | no |
| `auth_to` | account → server/SPN (Kerberos, observed) | no |
| `gpo_link` | GPO → OU | no |
| `provisions` | IaC template/repo → Azure resource (`yor_trace`/`mapping_tag` tags, Defender for Cloud IaC mapping) | no (but a template provisioning both sides' resources = a shared pipeline) |
| `uses_identity` / `attached_to` | resource → user-assigned MI; private endpoint → VNet | no |
| `trust` | domain ↔ domain/forest | no |

Ownership-type relations (`member_of`, `owns`, `contains`, `linked_to`) propagate the divest/retain label. Usage-type relations don't, because a user from the retained side using an app doesn't make the app "retained". Usage edges are what turns a node into **shared**.

---

## Layer 1: Entra ID

Microsoft Graph PowerShell (`Connect-MgGraph -Scopes Directory.Read.All,Application.Read.All,Policy.Read.All,AuditLog.Read.All,RoleManagement.Read.Directory`).

| Question | Source |
|---|---|
| Who belongs to the divested unit? | `Get-MgUser -All -Property id,userPrincipalName,companyName,department,onPremisesSyncEnabled,onPremisesDistinguishedName,employeeOrgData,accountEnabled,userType`, then seed by `companyName`/`department`/OU |
| Group nesting & mixed groups | `Get-MgGroup -All` + `Get-MgGroupMember -GroupId -All` (transitive: `Get-MgGroupTransitiveMember`). A group whose members are on both sides is a **shared** node. Dynamic groups: read `membershipRule`, because the rule may reference attributes that will change. |
| Which apps each side uses | `Get-MgServicePrincipalAppRoleAssignedTo -ServicePrincipalId <sp>` (assignments) + sign-in logs (actual use) |
| App ownership & credentials | `Get-MgApplication -All` (owners via `Get-MgApplicationOwner`, `passwordCredentials`/`keyCredentials` expiry), `signInAudience` (multi-tenant apps are easier to keep working across the split) |
| Delegated / app permissions | `Get-MgOauth2PermissionGrant -All` (delegated consents incl. per-user), `Get-MgServicePrincipalAppRoleAssignment` (application permissions). App-only Graph permissions on `Mail.Read`/`Sites.Read.All` are **tenant-wide** and read both sides' data. Flag them. |
| Admin roles | `Get-MgRoleManagementDirectoryRoleAssignment -All` (+ PIM eligibility `Get-MgRoleManagementDirectoryRoleEligibilitySchedule`). Administrative units scope admins: `Get-MgDirectoryAdministrativeUnit`. |
| Conditional Access dependencies | `Get-MgIdentityConditionalAccessPolicy`: include/exclude groups, named locations (the parent's egress IPs!), and auth strengths. Day One CA in the new tenant must not rely on the parent's network. |
| Domains | `Get-MgDomain` (verified, federated, default). Every UPN/proxy address on a domain is a `uses_domain` edge. |
| External / B2B | `Get-MgPolicyCrossTenantAccessPolicyPartner`, guest users (`userType eq 'Guest'`). Existing B2B relationships with the buyer are often already there. |
| Devices | `Get-MgDevice -All` (`trustType`: AzureAd / ServerAd = hybrid / Workplace), Intune: `Get-MgDeviceManagementManagedDevice`. Entra-joined devices **cannot** move tenants; they must be reset/re-enrolled (Autopilot re-registration in the target). |

## Layer 2: Exchange Online

`Connect-ExchangeOnline` (View-Only Organization Management is enough).

| Question | Source |
|---|---|
| Mailboxes, types, holds | `Get-EXOMailbox -ResultSize Unlimited -Properties LitigationHoldEnabled,InPlaceHolds,ArchiveStatus,ForwardingSmtpAddress,GrantSendOnBehalfTo,RecipientTypeDetails,ExchangeGuid,ArchiveGuid,LegacyExchangeDN`. **Holds block cross-tenant moves**, so list them early. |
| Delegations (classic shared-mailbox entanglement) | `Get-EXOMailboxPermission` (FullAccess), `Get-EXORecipientPermission` (SendAs), `GrantSendOnBehalfTo`, calendar folder permissions (`Get-EXOMailboxFolderPermission <mbx>:\Calendar`) |
| Distribution lists | `Get-DistributionGroup -ResultSize Unlimited` + `Get-DistributionGroupMember`. DLs are **not** moved by the mailbox tool; pre-create them in the target. |
| Mail flow | `Get-AcceptedDomain`, `Get-InboundConnector`, `Get-OutboundConnector` (scanners, ERP relays, MFPs, SaaS senders), `Get-TransportRule` (disclaimers, routing by domain), `Get-RemoteDomain`, `Get-OrganizationRelationship` |
| Who sends via SMTP relay / apps | Message trace (`Get-MessageTraceV2` where available) aggregated by sender IP / connector. MFPs and line-of-business apps that relay through the parent's connector are classic Day One breakers. |
| Public folders | `Get-PublicFolder -Recurse`. Not covered by cross-tenant mailbox migration. |

## Layer 3: SharePoint, OneDrive, Teams

`Connect-SPOService -Url https://<tenant>-admin.sharepoint.com`, `Connect-MicrosoftTeams`.

| Question | Source |
|---|---|
| All sites incl. OneDrive | `Get-SPOSite -Limit All -IncludePersonalSite $true`: `Url, Owner, StorageUsageCurrent, GroupId, HubSiteId, SharingCapability, LockState, SensitivityLabel` |
| Site ↔ group ↔ team | `GroupId` on site; `Get-Team` (GroupId); `Get-TeamUser -GroupId`; `Get-TeamChannel -GroupId -MembershipType Shared/Private` (private/shared channels have **their own** sites) |
| Who has access to what | site owners/members via the M365 group; unique permissions and sharing links need PnP (`Get-PnPListItem` + `Get-PnPFileSharingLink`) or a reporting tool. Use the sharing reports in SharePoint Advanced Management where licensed. |
| Hub/associated sites | `HubSiteId`: hub structures often mix both sides |
| OneDrive size/items vs limits | `StorageUsageCurrent` (MB); item count via usage reports (`Get-MgReportOneDriveUsageAccountDetail`) |
| Power Platform built on M365 data | `Microsoft.PowerApps.Administration.PowerShell`: `Get-AdminFlow`, `Get-AdminPowerApp`, `Get-AdminPowerAppEnvironment`. Flows owned by divested users that read retained lists, and vice versa. Environments move via the Power Platform tenant-to-tenant process, not M365 tools. |
| Encryption & labels | Purview sensitivity labels with encryption: content is protected with the **source tenant's** keys/RMS. After moving, target users can't open it unless it's re-protected or the source keeps granting access. Inventory labelled-and-encrypted content and Customer Key/DKE use. |

## Layer 4: On-prem Active Directory

`scripts/ad-inventory.ps1` (RSAT AD + GroupPolicy + DnsServer modules).

| Question | Source |
|---|---|
| Forest/domain topology, trusts | `Get-ADForest`, `Get-ADDomain`, `Get-ADTrust -Filter *` |
| Where the divested objects live | OU tree `Get-ADOrganizationalUnit -Filter *`. A clean OU split is the cheapest seed; mixed OUs are a finding. |
| Service accounts → servers | `Get-ADUser -Filter 'ServicePrincipalName -like "*"' -Properties ServicePrincipalName` and the same for gMSAs (`Get-ADServiceAccount`). The SPN host part is the dependency edge. |
| GPOs | `Get-GPO -All`, links via `Get-GPInheritance -Target <OU>`. GPOs linked above the divested OU still apply to it. |
| DNS | `Get-DnsServerZone`, conditional forwarders. Apps hard-coded to parent FQDNs. |
| Sites/subnets | `Get-ADReplicationSite`, `Get-ADReplicationSubnet`. These map physical locations to the network. |
| Federation / SSO | ADFS: `Get-AdfsRelyingPartyTrust`. Each RP is an app that must be re-pointed. |
| Sync scope to cloud | Entra Connect: `Get-ADSyncConnector`, OU/attribute filters in the Synchronization Service. Cloud Sync: configuration in the Entra portal. |
| PKI | AD CS templates/CAs (`certutil -CATemplates`), certs issued by the parent CA used for Wi-Fi/VPN/802.1X/LDAPS. |

## Layer 5: Azure

`scripts/azure_inventory.py` (`az graph query`, needs Reader on the management group scope).

| Question | Resource Graph source |
|---|---|
| Hierarchy | `resourcecontainers` (managementGroups, subscriptions, resourceGroups), tags (`costCenter`, `businessUnit`) as seeds |
| Tenant-bound resources | `resources | where identity <> "" or isnotempty(properties.tenantId)`: these break on directory transfer |
| RBAC | `authorizationresources | where type =~ "microsoft.authorization/roleassignments"`: `principalId`, `scope`, `principalType` |
| Network topology | VNets + `properties.virtualNetworkPeerings`, `microsoft.network/privateendpoints` (→ `privateLinkServiceId`), `microsoft.network/privatednszones/virtualnetworklinks`, `microsoft.network/connections` (VPN/ExpressRoute), route tables (next hop = shared firewall/NVA), `microsoft.network/virtualhubs` |
| Shared platform services | Log Analytics workspaces (diagnostic settings of both sides' resources point at them), Key Vaults (secrets used by both), container registries, Defender for Cloud, Azure Policy assignments at MG scope |
| Billing | EA enrollment / MCA billing profile per subscription. Moving a subscription's billing is separate from moving its directory. |

| IaC provenance | tags `yor_trace` / `mapping_tag` → `provisions` edges. With Defender CSPM + Azure DevOps: Cloud Security Explorer "Provisioned by" → "Code repositories" maps resource → template → repo (see `azure-separation.md` §IaC) |

What Resource Graph does **not** show: app settings that reference Key Vault secrets or connection strings, firewall rules by IP, code-level calls. For those, use observed evidence or IaC repos (`grep` Bicep/Terraform for subscription IDs, resource IDs, tenant IDs, FQDNs).

---

## Runtime / observed evidence

| Source | Gives you | Notes |
|---|---|---|
| **Entra sign-in logs** (`SigninLogs`, `AADNonInteractiveUserSignInLogs`, `AADServicePrincipalSignInLogs`, `AADManagedIdentitySignInLogs`) | user → app, SP → resource, location/IP | 30 days in the portal. Export to Log Analytics for longer windows. Requires P1. **Works council involvement for per-person analysis.** |
| Microsoft 365 unified audit log | who accessed which site/file/mailbox | `Search-UnifiedAuditLog` / Purview Audit; cross-side file access = live entanglement |
| DC security events 4768/4769 (Kerberos TGT/service tickets), 4624 | account → SPN/host | forward to SIEM; aggregate by service |
| LDAP / NTLM | apps binding to DCs | event 2889 (unsigned LDAP binds), NTLM auditing policies; reveals legacy apps bound to the parent's DCs |
| VNet flow logs + Traffic Analytics | subnet ↔ subnet, on-prem ↔ Azure flows | NSG flow logs are being replaced by VNet flow logs |
| Azure Migrate dependency analysis (agentless) | server ↔ server TCP connections for on-prem/VMware/Hyper-V | good for the "what talks to the ERP DB" question |
| Message trace | which connectors/IPs relay mail | catches MFPs and app relays |
| DNS query logs | who resolves parent FQDNs | Windows DNS analytic logs, Azure DNS / Private Resolver logs |

### Sample KQL (Log Analytics)

```kusto
// Apps used by each side: join with your seed list (watchlist or externaldata)
let divest = externaldata(upn:string)[@"https://<storage>/divest_upns.csv"] with (format="csv");
SigninLogs
| where TimeGenerated > ago(90d) and ResultType == 0
| extend side = iff(UserPrincipalName in~ (divest), "divest", "retain")
| summarize users=dcount(UserPrincipalName), signins=count() by AppDisplayName, AppId, side
| evaluate pivot(side, sum(users))
| where divest > 0 and retain > 0          // shared apps
| order by divest desc
```

```kusto
// Service principals / managed identities touching resources (who calls what)
AADServicePrincipalSignInLogs
| union AADManagedIdentitySignInLogs
| where TimeGenerated > ago(30d)
| summarize calls=count() by ServicePrincipalName, ResourceDisplayName
```

---

## Reading the graph: heuristics

- **Hub nodes** (high degree, both sides): `All Users` groups, the intranet hub site, the ERP app, the hub VNet/firewall, the central Log Analytics workspace, the "IT Admins" group with Global Admin. Each one needs an explicit decision.
- **Nested group chains**: a divested user who is in group A, nested in B, which holds an app role in C, inherits a dependency that looks invisible. Always use transitive membership.
- **Orphans / unknowns**: objects without an owner or a seed, such as service accounts, shared mailboxes and app registrations owned by people who have left. Push them to the owners list. Never guess.
- **Tenant-wide app permissions**: any SP with application-level `*.ReadWrite.All` is a data-leak path across the boundary during TSA. It is either shared or needs scoping (Exchange RBAC for Applications, `Sites.Selected`).
- **Identity attributes that drive things**: dynamic group rules, CA include rules, licensing groups and HR-driven provisioning all react when you change `companyName`/`department`. Change seeds *after* you've snapshot the graph.
- **Time**: a 30-day log won't show year-end close, the annual audit or the DR test. Ask app owners specifically about periodic jobs.
