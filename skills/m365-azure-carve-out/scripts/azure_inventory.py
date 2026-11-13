#!/usr/bin/env python3
"""Azure topology + dependency collector via Azure Resource Graph (read-only).

Requires: Azure CLI logged in (`az login`), `az extension add --name resource-graph`,
Reader on the scopes you want (management group root for a full picture).

Writes <out>/edges.csv (normalized schema for entanglement_graph.py), raw JSON per
query, and <out>/tenant_bound.csv (resources that break on a directory transfer).

  python3 azure_inventory.py --out out/azure [--management-group <mgId>] [--subscriptions id1 id2]
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

E = "| project src_id, src_type, rel, dst_id, dst_type, evidence"

QUERIES = {
    # --- hierarchy (propagating "contains") ---
    "mg_to_sub": """resourcecontainers
| where type =~ 'microsoft.resources/subscriptions'
| extend parent = tostring(properties.managementGroupAncestorsChain[0].name)
| where isnotempty(parent)
| extend src_id = strcat('/providers/microsoft.management/managementgroups/', parent), src_type = 'management_group',
         rel = 'contains', dst_id = id, dst_type = 'subscription', evidence = name """ + E,
    "sub_to_rg": """resourcecontainers
| where type =~ 'microsoft.resources/subscriptions/resourcegroups'
| extend src_id = strcat('/subscriptions/', subscriptionId), src_type = 'subscription',
         rel = 'contains', dst_id = id, dst_type = 'resourcegroup', evidence = tostring(tags) """ + E,
    "rg_to_resource": """resources
| extend src_id = strcat('/subscriptions/', subscriptionId, '/resourcegroups/', resourceGroup), src_type = 'resourcegroup',
         rel = 'contains', dst_id = id, dst_type = type, evidence = location """ + E,
    # --- network ---
    "vnet_peering": """resources
| where type =~ 'microsoft.network/virtualnetworks'
| mv-expand p = properties.virtualNetworkPeerings
| where isnotnull(p)
| extend src_id = id, src_type = 'vnet', rel = 'peers_with', dst_id = tostring(p.properties.remoteVirtualNetwork.id),
         dst_type = 'vnet', evidence = strcat(tostring(p.properties.peeringState), ' useRemoteGateways=', tostring(p.properties.useRemoteGateways)) """ + E,
    "private_endpoint_auto": """resources
| where type =~ 'microsoft.network/privateendpoints'
| mv-expand c = properties.privateLinkServiceConnections
| where isnotnull(c)
| extend src_id = id, src_type = 'private_endpoint', rel = 'private_link_to', dst_id = tostring(c.properties.privateLinkServiceId),
         dst_type = 'paas', evidence = strcat('auto ', tostring(c.properties.groupIds)) """ + E,
    "private_endpoint_manual": """resources
| where type =~ 'microsoft.network/privateendpoints'
| mv-expand c = properties.manualPrivateLinkServiceConnections
| where isnotnull(c)
| extend src_id = id, src_type = 'private_endpoint', rel = 'private_link_to', dst_id = tostring(c.properties.privateLinkServiceId),
         dst_type = 'paas', evidence = strcat('manual ', tostring(c.properties.groupIds)) """ + E,
    "private_endpoint_vnet": """resources
| where type =~ 'microsoft.network/privateendpoints'
| extend subnet = tostring(properties.subnet.id)
| extend src_id = id, src_type = 'private_endpoint', rel = 'attached_to',
         dst_id = tostring(split(subnet, '/subnets/')[0]), dst_type = 'vnet', evidence = subnet """ + E,
    "private_dns_link": """resources
| where type =~ 'microsoft.network/privatednszones/virtualnetworklinks'
| extend src_id = tostring(properties.virtualNetwork.id), src_type = 'vnet', rel = 'dns_link',
         dst_id = tostring(split(id, '/virtualnetworklinks/')[0]), dst_type = 'private_dns_zone',
         evidence = strcat('autoReg=', tostring(properties.registrationEnabled)) """ + E,
    "gateway_connections": """resources
| where type =~ 'microsoft.network/connections'
| extend src_id = tostring(properties.virtualNetworkGateway1.id), src_type = 'vnet_gateway', rel = 'routes_via',
         dst_id = coalesce(tostring(properties.peer.id), tostring(properties.localNetworkGateway2.id), tostring(properties.virtualNetworkGateway2.id)),
         dst_type = 'connection_peer', evidence = tostring(properties.connectionType) """ + E,
    "subnet_route_table": """resources
| where type =~ 'microsoft.network/virtualnetworks'
| mv-expand s = properties.subnets
| where isnotempty(s.properties.routeTable.id)
| extend src_id = id, src_type = 'vnet', rel = 'routes_via', dst_id = tostring(s.properties.routeTable.id),
         dst_type = 'route_table', evidence = tostring(s.name) """ + E,
    "route_next_hop": """resources
| where type =~ 'microsoft.network/routetables'
| mv-expand r = properties.routes
| where tostring(r.properties.nextHopType) =~ 'VirtualAppliance'
| extend src_id = id, src_type = 'route_table', rel = 'routes_via', dst_id = strcat('ip:', tostring(r.properties.nextHopIpAddress)),
         dst_type = 'nva_ip', evidence = tostring(r.properties.addressPrefix) """ + E,
    # --- IaC provenance (Defender for Cloud IaC mapping tags; yor_trace / mapping_tag GUIDs) ---
    "iac_tag": """resources
| extend t = coalesce(tostring(tags.yor_trace), tostring(tags.mapping_tag))
| where isnotempty(t)
| extend src_id = strcat('iac:', t), src_type = 'iac_template', rel = 'provisions',
         dst_id = id, dst_type = type, evidence = iff(isnotempty(tostring(tags.yor_trace)), 'yor_trace', 'mapping_tag') """ + E,
    # --- identity / access ---
    "rbac": """authorizationresources
| where type =~ 'microsoft.authorization/roleassignments'
| extend src_id = tostring(properties.principalId), src_type = tolower(tostring(properties.principalType)), rel = 'role_on',
         dst_id = tostring(properties.scope), dst_type = 'scope', evidence = tostring(properties.roleDefinitionId) """ + E,
}

TENANT_BOUND = """resources
| where type != 'microsoft.azureactivedirectory/b2cdirectories'
| where identity <> '' or isnotempty(properties.tenantId) or properties.encryptionSettingsCollection.enabled == true
| project id, name, type, subscriptionId, identityType = tostring(identity.type), tenantId = tostring(properties.tenantId)"""

USER_ASSIGNED = """resources
| where isnotnull(identity.userAssignedIdentities)
| project id, type, uai = identity.userAssignedIdentities"""

FIELDS = ["src_id", "src_type", "rel", "dst_id", "dst_type", "evidence", "source"]


def run(query: str, scope: list[str]) -> list[dict]:
    rows, token = [], None
    while True:
        cmd = ["az", "graph", "query", "-q", query, "--first", "1000", "-o", "json", *scope]
        if token:
            cmd += ["--skip-token", token]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(res.stderr.strip()[:500])
        out = json.loads(res.stdout)
        rows += out.get("data", [])
        token = out.get("skip_token") or out.get("skipToken")
        if not token:
            return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--management-group")
    ap.add_argument("--subscriptions", nargs="*")
    a = ap.parse_args()
    if not shutil.which("az"):
        sys.exit("Azure CLI 'az' not found")
    scope = (["--management-groups", a.management_group] if a.management_group
             else (["--subscriptions", *a.subscriptions] if a.subscriptions else []))
    a.out.mkdir(parents=True, exist_ok=True)
    raw = a.out / "raw"
    raw.mkdir(exist_ok=True)

    edges, failed = [], []
    for name, q in QUERIES.items():
        try:
            rows = run(q, scope)
        except RuntimeError as e:
            failed.append(f"{name}: {e}")
            continue
        (raw / f"{name}.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
        for r in rows:
            if r.get("src_id") and r.get("dst_id"):
                edges.append({**{k: r.get(k, "") for k in FIELDS[:-1]}, "source": f"arg:{name}"})
        print(f"{name}: {len(rows)}")

    try:  # user-assigned managed identities attached to resources
        for r in run(USER_ASSIGNED, scope):
            for uai in (r.get("uai") or {}):
                edges.append({"src_id": r["id"], "src_type": r["type"], "rel": "uses_identity",
                              "dst_id": uai, "dst_type": "managed_identity", "evidence": "userAssigned",
                              "source": "arg:user_assigned"})
    except RuntimeError as e:
        failed.append(f"user_assigned: {e}")

    with (a.out / "edges.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(edges)

    try:
        tb = run(TENANT_BOUND, scope)
        with (a.out / "tenant_bound.csv").open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["id", "name", "type", "subscriptionId", "identityType", "tenantId"])
            w.writeheader()
            w.writerows({k: r.get(k, "") for k in w.fieldnames} for r in tb)
        print(f"tenant_bound: {len(tb)}")
    except RuntimeError as e:
        failed.append(f"tenant_bound: {e}")

    print(f"wrote {a.out}/edges.csv ({len(edges)} edges)")
    if failed:
        print("FAILED queries (check permissions / extension):\n  " + "\n  ".join(failed), file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
