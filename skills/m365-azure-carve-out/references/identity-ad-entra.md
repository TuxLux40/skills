# Identity: AD DS, Entra ID, coexistence

Identity is wave 1. Every other workload's identity mapping depends on it.

## Decide the identity end state

| Divested unit lands in… | On-prem AD | Cloud identity |
|---|---|---|
| Buyer's existing tenant + buyer AD | migrate objects into the buyer's forest (or go cloud-only) | buyer's Entra Connect syncs them in; cross-tenant moves for content |
| New standalone tenant, keeps on-prem | **new forest** (clean) or **clone + clean** of the parent domain | new Entra Connect to the new tenant |
| New standalone tenant, cloud-only | none: retire the on-prem dependency during the separation | cloud-only users, Entra-joined devices, Intune |

Cloning a parent domain controller to "take the domain with you" brings the parent's SIDs, krbtgt, admin accounts, trusts and every GPO. Security teams on both sides usually reject that. If you do it, it is clone-and-go: plan a full credential reset, krbtgt double reset, purge of seller objects, and a trust teardown.

## AD DS migration mechanics

- **Inter-forest migration** with SID history keeps access to the parent's resources during the TSA. It needs a forest trust with SID filtering relaxed, which is a security exposure the seller must accept on paper and remove at exit.
- Tools: ADMT is legacy and largely unmaintained. Commercial tools (Quest Migration Manager for AD / On Demand, Semperis, BinaryTree/Quest) handle SID history, re-ACLing of file servers and device re-domain-join.
- Order: trusts → service accounts and their SPNs → groups (with SID history) → users → resource re-ACL → workstations (re-domain-join or Autopilot reset) → servers → retire trust.
- Find hidden coupling: SPNs (account → host), hard-coded DC names/IPs in apps and appliances, LDAP binds (event 2889), Kerberos delegation settings, GPO-deployed certificates/Wi-Fi/proxy settings, logon scripts on parent `NETLOGON` shares, DFS namespaces.

## Entra Connect / Cloud Sync during the split

- **One AD forest can sync to two tenants** with two Entra Connect servers, each scoped by OU. An object must be in scope of **only one** tenant's sync for a given identity. Separate the OUs *before* you re-scope.
- Moving a user's OU from the parent sync scope to the buyer scope **soft-deletes the cloud user in the parent tenant** at the next sync cycle. Do it only in the planned wave, after the content has moved. Watch the accidental-deletion threshold (it's a safety net, not a plan).
- For cross-tenant mailbox moves, on-prem `msExchMailboxGUID`, `proxyAddresses` and `msExchRemoteRecipientType` must be correct before the user syncs into the target. Otherwise you get duplicate mailboxes.
- UPN change: change it on-prem after the user's migration completes (unless the domain moves in the same cutover).

## Coexistence for the TSA period

| Need | Mechanism |
|---|---|
| Divested users still open seller apps/sites | B2B guest or B2B **member** in the seller tenant: **cross-tenant synchronization** (auto-provision/deprovision, attribute sync). The inbound "Allow user synchronization into this tenant" is set in the target. |
| Both sides collaborate in Teams | external access (federation), B2B direct connect for shared channels, or an MTO (multitenant organization) for the "one company" experience |
| MFA/device trust not prompted twice | cross-tenant access settings: inbound trust of MFA, compliant device, hybrid-joined claims |
| Admins of the buyer manage seller-hosted Azure | Azure Lighthouse (see `azure-separation.md`) |
| Mail free/busy | organization relationship |

All of these are **TSA artifacts**. List each one in the register with an exit date, and remove them at exit, because a forgotten cross-tenant sync keeps provisioning.

## Day One identity checklist

- [ ] Every divested user can sign in somewhere they own, or has a dated TSA for seller sign-in
- [ ] Break-glass accounts in the new tenant (cloud-only, excluded from CA, FIDO2)
- [ ] CA policies in the new tenant don't reference seller named locations/groups
- [ ] MFA methods re-registered (methods don't migrate cross-tenant), with an onboarding comms plan (TAP / Temporary Access Pass)
- [ ] Privileged roles: no seller admin holds a role in the new tenant beyond the TSA delegation, and vice versa
- [ ] App registrations that the buyer must own: recreated (new app IDs → every SaaS/OIDC config changes) or made multi-tenant
- [ ] Secrets/certificates of service principals rotated (the seller knew them)
- [ ] HR → identity provisioning (Workday/SAP SF/etc.) pointed at the new tenant/AD
