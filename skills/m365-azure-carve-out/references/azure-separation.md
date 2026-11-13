# Azure separation

Source: https://learn.microsoft.com/azure/role-based-access-control/transfer-subscription (checked 2026-11-13).

## Three options per landing zone

| Option | How | Use when | Cost |
|---|---|---|---|
| **A. Transfer subscription to the buyer's directory** | change the subscription's Entra directory (optionally with billing ownership) | resources are already isolated in their own subscriptions; apps depend on subscription/resource IDs | downtime, **⚠ all RBAC + custom roles permanently deleted**, identities broken |
| **B. Re-deploy and copy data** | IaC into a new subscription in the buyer's tenant, then migrate data (DB replication, AzCopy, ASR for VMs) | IaC exists; there are many tenant-bound PaaS; a clean start is wanted | build effort, but a controllable cutover and rollback |
| **C. Leave in place + Azure Lighthouse (TSA)** | the subscription stays in the seller's tenant, and the buyer's admins manage it via Lighthouse delegation | the Day One bridge while A or B is prepared | seller keeps the billing and risk. Must be a dated TSA line with exit. |

Common pattern: **resource-move first, then transfer.** Inside the *source* tenant, move the divested unit's resources from shared subscriptions into dedicated subscriptions (`Move-AzResource` / portal "Move"). Check move support per resource type, since not all types are movable. Then transfer those clean subscriptions (A) or use them as the copy source (B).

### Is option B realistic? Map IaC to resources first

Option B is only cheap if the resources really come from code. Measure IaC coverage per subscription before you choose:

- **Defender for Cloud IaC mapping** (https://learn.microsoft.com/azure/defender-for-cloud/iac-template-mapping): Cloud Security Explorer → resources → *Identity & Access* › **Provisioned by** → *DevOps* › **Code repositories** (or the built-in template *"Cloud resources provisioned by IaC templates with high severity misconfigurations"*). It shows template → resource → repository.
  - Prerequisites: Defender CSPM plan, Azure DevOps connected to Defender for Cloud, a pipeline running the Microsoft Security DevOps extension with **IaCFileScanner**, and templates tagged with unique-GUID **`yor_trace`** or **`mapping_tag`** tags (only those two are used; `yor` can auto-tag). It supports ARM, Bicep, Terraform and CloudFormation. **The SCM is Azure DevOps only.** Mapping can take up to 12 h to appear.
- **Without Defender CSPM / with GitHub**: `scripts/azure_inventory.py` already turns the same tags into `iac:<guid> --provisions--> resource` edges from Resource Graph. For untagged estates, grep the IaC repos for resource names, subscription IDs and tenant IDs, and compare that with the ARG resource list. The difference is your **click-ops residue**, which has to be rebuilt by hand or captured first (`az bicep decompile` from an export, or `aztfexport` for Terraform).
- Carve-out value beyond re-deploy: the repo → resource edges show **who owns the pipeline** (a divested resource deployed from the seller's repo and service connection is an entanglement in its own right), and which service connections / federated credentials point at the seller's tenant. Those must be re-created in the buyer's DevOps org.

**CSP subscriptions cannot change directory.** That makes option B (or a CSP-side transfer) the only path.

## Impact matrix for a directory transfer (A)

| Service / resource | Impact | Recoverable | Action |
|---|---|---|---|
| Role assignments | **deleted permanently** | yes | export first; map principals; re-create |
| Custom roles | **deleted permanently** | yes | export JSON; re-create, then the assignments |
| System-assigned managed identities | broken | yes | disable + re-enable; re-assign roles |
| User-assigned managed identities | broken | yes | delete, re-create, re-attach; re-assign roles |
| Key Vault | tenant ID mismatch | yes | update tenant ID; replace access policies (or RBAC) |
| CMK encryption depending on a transferred Key Vault | **can become unrecoverable** | ⚠ | switch to another vault or disable CMK *before* transfer |
| Azure SQL with Entra auth | **cannot transfer** while enabled | no | disable Entra auth / admin first, re-enable after |
| Azure Database for MySQL with Entra auth | cannot transfer while enabled | no | same |
| PostgreSQL Flexible with Entra auth or CMK | cannot transfer while enabled | no | disable, transfer, re-enable |
| Storage / ADLS Gen2 ACLs | ACLs lost | yes | re-create ACLs |
| Azure Files | ACLs; Entra Kerberos | mostly | re-create ACLs; disable/re-enable Entra Kerberos; Entra Domain Services targets are unsupported |
| Managed Disks with Disk Encryption Sets | identity | yes | re-enable DES identity; re-grant Key Vault |
| AKS, App Service auth, Functions, Data Factory, Synapse, etc. | usually identity- or tenant-bound | varies | check each service's docs; the Learn table isn't exhaustive |

Discovery before transfer (also in `scripts/azure_inventory.py`):

```bash
az role assignment list --all --include-inherited --output json > roleassignments.json
az role definition list --custom-role-only true --output json > customroles.json
az ad sp list --all --filter "servicePrincipalType eq 'ManagedIdentity'" > managedidentities.json
az graph query -q 'resources
  | where type != "microsoft.azureactivedirectory/b2cdirectories"
  | where identity <> "" or properties.tenantId <> "" or properties.encryptionSettingsCollection.enabled == true
  | project name, type, kind, identity, tenantId, properties.tenantId' --first 1000
az sql server ad-admin list --ids $(az graph query -q "resources | where type == 'microsoft.sql/servers' | project id" --query data[*].[id] -o tsv)
```

After transfer: a Global Admin of the target may need **"Access management for Azure resources"** elevation to see the subscription at all.

You can block subscription transfers with subscription policies. Check whether the seller has this set before you plan option A.

## Network separation: where Azure carve-outs actually hurt

- **Hub-and-spoke**: the divested spokes peer to the seller's hub (firewall, DNS, gateways). Peering across tenants is possible, but the traffic still goes through the seller's firewall. That's a TSA line: name it, price it, give it an end date.
- **Private DNS**: private endpoint zones (`privatelink.*`) linked to the hub. The buyer needs its own zones and resolver before private endpoints can move.
- **On-prem connectivity**: ExpressRoute circuits/VPN gateways owned by the seller. Lead times for new circuits are long, so order on signing, not on closing.
- **IP overlap**: the buyer's address space may collide with the divested VNets. Find out early, because re-IP is a project in itself.
- **Egress identity**: Conditional Access named locations, SaaS IP allowlists and partner firewalls that trust the seller's public IPs.

## Governance plane to re-create in the target

Management group hierarchy, Azure Policy assignments/initiatives (often inherited from the seller's MG root without anyone noticing), Defender for Cloud plans, diagnostic settings → which workspace, budgets and cost exports, reservations / savings plans (check exchange/transfer terms: these are typical **stranded costs**), Azure Backup vaults (cross-tenant restore limitations), Sentinel content.
