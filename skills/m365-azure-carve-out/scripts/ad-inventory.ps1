<#
.SYNOPSIS
  Read-only on-prem Active Directory inventory for carve-out dependency mapping.
.DESCRIPTION
  Trusts, OUs, OU -> user/computer containment, group memberships, SPNs (account -> host),
  GPO links, DNS zones, AD sites/subnets, optional ADFS relying parties.
  Writes raw CSVs + edges.csv + aliases.csv (SID/DN -> UPN) for entanglement_graph.py.
  Needs RSAT: ActiveDirectory, GroupPolicy (+ DnsServer, ADFS optional). Domain user rights suffice for most reads.
.EXAMPLE
  ./ad-inventory.ps1 -OutDir ./out/ad -Server dc01.corp.contoso.com
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory)] [string] $OutDir,
  [string] $Server,
  [string] $DnsServer,
  [switch] $IncludeAdfs
)
$ErrorActionPreference = 'Stop'
Import-Module ActiveDirectory
Import-Module GroupPolicy
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$p = @{}; if ($Server) { $p.Server = $Server }
$edges = [System.Collections.Generic.List[object]]::new()
$aliases = [System.Collections.Generic.List[object]]::new()
function Add-Edge($s, $st, $r, $d, $dt, $ev = '') {
  if ($s -and $d) { $edges.Add([pscustomobject]@{ src_id = "$s".ToLower(); src_type = $st; rel = $r; dst_id = "$d".ToLower(); dst_type = $dt; evidence = $ev; source = 'ad' }) }
}
function Save($o, $n) { $o | Export-Csv -NoTypeInformation -Encoding utf8 -Path (Join-Path $OutDir "$n.csv") }

$dom = Get-ADDomain @p; $forest = Get-ADForest @p
Save ([pscustomobject]@{ Forest = $forest.Name; Domains = $forest.Domains -join ';'; ForestMode = $forest.ForestMode; DomainMode = $dom.DomainMode; PDC = $dom.PDCEmulator }) 'ad_topology'
$trusts = Get-ADTrust -Filter * @p
Save ($trusts | Select-Object Name,Direction,TrustType,ForestTransitive,SIDFilteringQuarantined,SelectiveAuthentication) 'ad_trusts'
foreach ($t in $trusts) { Add-Edge "domain:$($dom.DNSRoot)" 'ad_domain' 'trust' "domain:$($t.Name)" 'ad_domain' "$($t.Direction) $($t.TrustType)" }

$gpp = @{ Domain = $dom.DNSRoot }; if ($Server) { $gpp.Server = $Server }
$ous = Get-ADOrganizationalUnit -Filter * @p -Properties CanonicalName
Save ($ous | Select-Object DistinguishedName,CanonicalName) 'ad_ous'
foreach ($ou in $ous) {
  $parent = ($ou.DistinguishedName -split ',', 2)[1]
  Add-Edge "ou:$parent" 'ou' 'contains' "ou:$($ou.DistinguishedName)" 'ou'
  foreach ($gl in (Get-GPInheritance -Target $ou.DistinguishedName @gpp).GpoLinks) {
    Add-Edge "gpo:$($gl.DisplayName)" 'gpo' 'gpo_link' "ou:$($ou.DistinguishedName)" 'ou' "enabled=$($gl.Enabled) enforced=$($gl.Enforced)"
  }
}

$users = Get-ADUser -Filter * @p -Properties UserPrincipalName,ServicePrincipalName,Enabled,Company,Department,MemberOf,LastLogonDate,PasswordLastSet,TrustedForDelegation,'msDS-AllowedToDelegateTo'
Save ($users | Select-Object SamAccountName,UserPrincipalName,Enabled,Company,Department,DistinguishedName,LastLogonDate,PasswordLastSet,TrustedForDelegation,
      @{n='SPNs';e={$_.ServicePrincipalName -join ';'}},@{n='DelegateTo';e={$_.'msDS-AllowedToDelegateTo' -join ';'}}) 'ad_users'
foreach ($u in $users) {
  $k = if ($u.UserPrincipalName) { $u.UserPrincipalName } else { "ad:$($u.SamAccountName)" }
  $aliases.Add([pscustomobject]@{ alias = $u.DistinguishedName.ToLower(); canonical = $k.ToLower() })
  $aliases.Add([pscustomobject]@{ alias = $u.SID.Value.ToLower(); canonical = $k.ToLower() })
  Add-Edge "ou:$(($u.DistinguishedName -split ',', 2)[1])" 'ou' 'contains' $k 'user'
  foreach ($g in $u.MemberOf) { Add-Edge $k 'user' 'member_of' "adgrp:$g" 'ad_group' }
  foreach ($spn in $u.ServicePrincipalName) { $h = ($spn -split '/')[1] -replace ':\d+$', ''; Add-Edge $k 'service_account' 'auth_to' "host:$h" 'server' "SPN $spn" }
  foreach ($d in $u.'msDS-AllowedToDelegateTo') { Add-Edge $k 'service_account' 'auth_to' "host:$((($d -split '/')[1]) -replace ':\d+$','')" 'server' "constrained delegation $d" }
}
try {
  foreach ($s in (Get-ADServiceAccount -Filter * @p -Properties ServicePrincipalName,PrincipalsAllowedToRetrieveManagedPassword)) {
    foreach ($spn in $s.ServicePrincipalName) { Add-Edge "gmsa:$($s.Name)" 'gmsa' 'auth_to' "host:$((($spn -split '/')[1]) -replace ':\d+$','')" 'server' "SPN $spn" }
    foreach ($h in $s.PrincipalsAllowedToRetrieveManagedPassword) { Add-Edge "gmsa:$($s.Name)" 'gmsa' 'runs_on' "adobj:$h" 'computer' 'password retrieval' }
  }
} catch { Write-Warning "gMSA: $_" }

$groups = Get-ADGroup -Filter * @p -Properties MemberOf,ManagedBy,GroupScope,GroupCategory
Save ($groups | Select-Object Name,DistinguishedName,GroupScope,GroupCategory,ManagedBy) 'ad_groups'
foreach ($g in $groups) { foreach ($pg in $g.MemberOf) { Add-Edge "adgrp:$($g.DistinguishedName)" 'ad_group' 'member_of' "adgrp:$pg" 'ad_group' 'nested' } }

$computers = Get-ADComputer -Filter * @p -Properties DNSHostName,OperatingSystem,LastLogonDate,ServicePrincipalName
Save ($computers | Select-Object Name,DNSHostName,OperatingSystem,DistinguishedName,LastLogonDate) 'ad_computers'
foreach ($c in $computers) {
  $hk = "host:$(if ($c.DNSHostName) { $c.DNSHostName } else { $c.Name })"
  Add-Edge "ou:$(($c.DistinguishedName -split ',', 2)[1])" 'ou' 'contains' $hk 'server'
  $aliases.Add([pscustomobject]@{ alias = "host:$($c.Name)".ToLower(); canonical = $hk.ToLower() })
  $aliases.Add([pscustomobject]@{ alias = "adobj:$($c.DistinguishedName)".ToLower(); canonical = $hk.ToLower() })
}

Save (Get-ADReplicationSite -Filter * @p | Select-Object Name,Description) 'ad_sites'
Save (Get-ADReplicationSubnet -Filter * @p | Select-Object Name,Site,Location) 'ad_subnets'
try {
  Import-Module DnsServer
  $dp = @{}; if ($DnsServer) { $dp.ComputerName = $DnsServer } elseif ($Server) { $dp.ComputerName = $Server }
  Save (Get-DnsServerZone @dp | Select-Object ZoneName,ZoneType,IsDsIntegrated,IsReverseLookupZone,@{n='MasterServers';e={$_.MasterServers -join ';'}}) 'ad_dns_zones'
} catch { Write-Warning "DNS: $_" }
if ($IncludeAdfs) {
  try { Save (Get-AdfsRelyingPartyTrust | Select-Object Name,Enabled,@{n='Identifier';e={$_.Identifier -join ';'}},WSFedEndpoint) 'adfs_relying_parties' } catch { Write-Warning "ADFS: $_" }
}

$edges | Export-Csv -NoTypeInformation -Encoding utf8 -Path (Join-Path $OutDir 'edges.csv')
$aliases | Export-Csv -NoTypeInformation -Encoding utf8 -Path (Join-Path $OutDir 'aliases.csv')
Write-Host "Done: $($edges.Count) edges -> $OutDir" -ForegroundColor Green
