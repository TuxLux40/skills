<#
.SYNOPSIS
  Read-only M365 / Entra ID inventory for carve-out dependency mapping.
.DESCRIPTION
  Collects Entra (users, groups, nesting, apps, assignments, consents, roles, CA, domains),
  Exchange Online (mailboxes, holds, delegations, DLs, connectors, transport rules),
  SharePoint/OneDrive (sites, owners, group links) and Teams (teams, members).
  Writes raw CSVs + normalized edges.csv + aliases.csv for entanglement_graph.py.

  Modules: Microsoft.Graph (Authentication, Users, Groups, Applications, Identity.DirectoryManagement,
  Identity.SignIns, Identity.Governance), ExchangeOnlineManagement, Microsoft.Online.SharePoint.PowerShell,
  MicrosoftTeams. Each section is skipped with a warning if its module or permission is missing.

  Least privilege: Global Reader + View-Only Organization Management (EXO) + SharePoint admin (read use only).
.EXAMPLE
  ./m365-inventory.ps1 -OutDir ./out/m365 -SpoAdminUrl https://contoso-admin.sharepoint.com
.EXAMPLE
  ./m365-inventory.ps1 -OutDir ./out/m365 -Skip Exchange,Teams -IncludeMailboxPermissions:$false
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory)] [string] $OutDir,
  [string] $SpoAdminUrl,
  [ValidateSet('Entra','Exchange','SharePoint','Teams')] [string[]] $Skip = @(),
  # Per-mailbox FullAccess/SendAs queries are slow on large tenants (one call per mailbox).
  [switch] $IncludeMailboxPermissions = $true
)
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$edges   = [System.Collections.Generic.List[object]]::new()
$aliases = [System.Collections.Generic.List[object]]::new()

function Add-Edge($SrcId, $SrcType, $Rel, $DstId, $DstType, $Evidence = '', $Source = '') {
  if ([string]::IsNullOrWhiteSpace($SrcId) -or [string]::IsNullOrWhiteSpace($DstId)) { return }
  $edges.Add([pscustomobject]@{ src_id = "$SrcId".ToLower(); src_type = $SrcType; rel = $Rel
    dst_id = "$DstId".ToLower(); dst_type = $DstType; evidence = $Evidence; source = $Source })
}
function Add-Alias($Alias, $Canonical) {
  if ($Alias -and $Canonical) { $aliases.Add([pscustomobject]@{ alias = "$Alias".ToLower(); canonical = "$Canonical".ToLower() }) }
}
function Save($Obj, $Name) { $Obj | Export-Csv -NoTypeInformation -Encoding utf8 -Path (Join-Path $OutDir "$Name.csv") }
# Readable, unique key for non-user objects.
function Key($Prefix, $Name, $Id) { "{0}:{1} ({2})" -f $Prefix, $Name, ("$Id".Substring(0, [Math]::Min(8, "$Id".Length))) }

$keyById = @{}   # Entra objectId -> node key

# ---------------------------------------------------------------- Entra ID
if ('Entra' -notin $Skip) {
  Write-Host '== Entra ID' -ForegroundColor Cyan
  Connect-MgGraph -NoWelcome -Scopes Directory.Read.All, Application.Read.All, Policy.Read.All, RoleManagement.Read.Directory, GroupMember.Read.All

  $users = Get-MgUser -All -Property id,userPrincipalName,displayName,mail,companyName,department,jobTitle,userType,accountEnabled,onPremisesSyncEnabled,onPremisesDistinguishedName,proxyAddresses,createdDateTime
  Save ($users | Select-Object id,userPrincipalName,displayName,mail,companyName,department,jobTitle,userType,accountEnabled,onPremisesSyncEnabled,onPremisesDistinguishedName,@{n='proxyAddresses';e={$_.ProxyAddresses -join ';'}}) 'entra_users'
  foreach ($u in $users) {
    $keyById[$u.Id] = $u.UserPrincipalName
    Add-Alias $u.Id $u.UserPrincipalName
    if ($u.Mail -and $u.Mail -ne $u.UserPrincipalName) { Add-Alias $u.Mail $u.UserPrincipalName }
    $dom = ($u.UserPrincipalName -split '@')[-1]
    Add-Edge $u.UserPrincipalName 'user' 'uses_domain' "domain:$dom" 'domain' 'UPN' 'entra'
  }

  $groups = Get-MgGroup -All -Property id,displayName,mail,groupTypes,securityEnabled,mailEnabled,membershipRule,onPremisesSyncEnabled,isAssignableToRole
  Save ($groups | Select-Object id,displayName,mail,securityEnabled,mailEnabled,membershipRule,onPremisesSyncEnabled,isAssignableToRole,@{n='groupTypes';e={$_.GroupTypes -join ';'}}) 'entra_groups'
  foreach ($g in $groups) { $k = Key 'grp' $g.DisplayName $g.Id; $keyById[$g.Id] = $k; Add-Alias $g.Id $k; if ($g.Mail) { Add-Alias $g.Mail $k } }

  Write-Host '   group memberships (direct; nesting is captured as group->group edges)'
  foreach ($g in $groups) {
    foreach ($m in (Get-MgGroupMember -GroupId $g.Id -All)) {
      $t = ($m.AdditionalProperties.'@odata.type' -replace '#microsoft.graph.', '')
      $src = $keyById[$m.Id]; if (-not $src) { $src = "${t}:$($m.Id)" }
      Add-Edge $src $t 'member_of' $keyById[$g.Id] 'group' ($(if ($g.MembershipRule) { 'dynamic' } else { 'direct' })) 'entra'
    }
    foreach ($o in (Get-MgGroupOwner -GroupId $g.Id -All)) {
      $src = $keyById[$o.Id]; if ($src) { Add-Edge $src 'user' 'owns' $keyById[$g.Id] 'group' 'owner' 'entra' }
    }
  }

  Write-Host '   service principals, assignments, consents'
  $sps = Get-MgServicePrincipal -All -Property id,appId,displayName,servicePrincipalType,appOwnerOrganizationId,accountEnabled,appRoleAssignmentRequired
  Save ($sps | Select-Object id,appId,displayName,servicePrincipalType,appOwnerOrganizationId,accountEnabled,appRoleAssignmentRequired) 'entra_service_principals'
  foreach ($sp in $sps) { $k = Key 'sp' $sp.DisplayName $sp.AppId; $keyById[$sp.Id] = $k; Add-Alias $sp.Id $k; Add-Alias $sp.AppId $k }
  foreach ($sp in ($sps | Where-Object ServicePrincipalType -eq 'Application')) {
    foreach ($a in (Get-MgServicePrincipalAppRoleAssignedTo -ServicePrincipalId $sp.Id -All)) {
      $src = $keyById[$a.PrincipalId]; if (-not $src) { $src = "$($a.PrincipalType):$($a.PrincipalId)" }
      Add-Edge $src $a.PrincipalType.ToLower() 'assigned_to' $keyById[$sp.Id] 'enterprise_app' "appRole $($a.AppRoleId)" 'entra'
    }
    # application permissions this SP holds on other APIs (tenant-wide data access!)
    foreach ($a in (Get-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $sp.Id -All)) {
      Add-Edge $keyById[$sp.Id] 'service_principal' 'consented' $keyById[$a.ResourceId] 'api' "application appRole $($a.AppRoleId)" 'entra'
    }
  }
  foreach ($gr in (Get-MgOauth2PermissionGrant -All)) {
    $who = if ($gr.ConsentType -eq 'AllPrincipals') { 'tenant-wide' } else { $keyById[$gr.PrincipalId] }
    Add-Edge $keyById[$gr.ClientId] 'service_principal' 'consented' $keyById[$gr.ResourceId] 'api' "delegated [$who] $($gr.Scope)" 'entra'
  }

  $apps = Get-MgApplication -All -Property id,appId,displayName,signInAudience,passwordCredentials,keyCredentials,web,spa
  Save ($apps | Select-Object id,appId,displayName,signInAudience,
        @{n='secretExpiry';e={($_.PasswordCredentials.EndDateTime | Sort-Object | Select-Object -Last 1)}},
        @{n='certExpiry';e={($_.KeyCredentials.EndDateTime | Sort-Object | Select-Object -Last 1)}},
        @{n='redirectUris';e={(@($_.Web.RedirectUris) + @($_.Spa.RedirectUris)) -join ';'}}) 'entra_applications'
  foreach ($app in $apps) {
    foreach ($o in (Get-MgApplicationOwner -ApplicationId $app.Id -All)) {
      Add-Edge $keyById[$o.Id] 'user' 'owns' (Key 'sp' $app.DisplayName $app.AppId) 'enterprise_app' 'app registration owner' 'entra'
    }
  }

  Write-Host '   directory roles, CA policies, domains, cross-tenant partners'
  $roleDefs = @{}; Get-MgRoleManagementDirectoryRoleDefinition -All | ForEach-Object { $roleDefs[$_.Id] = $_.DisplayName }
  $ra = Get-MgRoleManagementDirectoryRoleAssignment -All
  Save ($ra | Select-Object principalId,roleDefinitionId,@{n='role';e={$roleDefs[$_.RoleDefinitionId]}},directoryScopeId) 'entra_role_assignments'
  foreach ($r in $ra) { Add-Edge $keyById[$r.PrincipalId] 'principal' 'role_on' "entra-role:$($roleDefs[$r.RoleDefinitionId])" 'entra_role' "scope $($r.DirectoryScopeId)" 'entra' }

  $ca = Get-MgIdentityConditionalAccessPolicy -All
  Save ($ca | Select-Object id,displayName,state,
        @{n='includeGroups';e={$_.Conditions.Users.IncludeGroups -join ';'}}, @{n='excludeGroups';e={$_.Conditions.Users.ExcludeGroups -join ';'}},
        @{n='includeApps';e={$_.Conditions.Applications.IncludeApplications -join ';'}}, @{n='includeLocations';e={$_.Conditions.Locations.IncludeLocations -join ';'}},
        @{n='excludeLocations';e={$_.Conditions.Locations.ExcludeLocations -join ';'}}) 'entra_conditional_access'
  foreach ($p in $ca) {
    foreach ($gid in @($p.Conditions.Users.IncludeGroups) + @($p.Conditions.Users.ExcludeGroups)) {
      if ($gid) { Add-Edge $keyById[$gid] 'group' 'scoped_by' "ca:$($p.DisplayName)" 'ca_policy' $p.State 'entra' }
    }
  }
  Save (Get-MgDomain -All | Select-Object id,isVerified,isDefault,authenticationType,@{n='services';e={$_.SupportedServices -join ';'}}) 'entra_domains'
  try { Save (Get-MgPolicyCrossTenantAccessPolicyPartner -All | Select-Object tenantId,isServiceProvider) 'entra_crosstenant_partners' } catch { Write-Warning "cross-tenant partners: $_" }
  try { Save (Get-MgDevice -All -Property id,displayName,trustType,operatingSystem,approximateLastSignInDateTime | Select-Object id,displayName,trustType,operatingSystem,approximateLastSignInDateTime) 'entra_devices' } catch { Write-Warning "devices: $_" }
}

# ---------------------------------------------------------------- Exchange Online
if ('Exchange' -notin $Skip) {
  Write-Host '== Exchange Online' -ForegroundColor Cyan
  Connect-ExchangeOnline -ShowBanner:$false
  $mbx = Get-EXOMailbox -ResultSize Unlimited -Properties LitigationHoldEnabled,InPlaceHolds,RetentionHoldEnabled,ArchiveStatus,ForwardingSmtpAddress,ForwardingAddress,GrantSendOnBehalfTo,ExchangeGuid,ArchiveGuid,LegacyExchangeDN,WhenCreated
  Save ($mbx | Select-Object DisplayName,UserPrincipalName,PrimarySmtpAddress,RecipientTypeDetails,LitigationHoldEnabled,RetentionHoldEnabled,
        @{n='InPlaceHolds';e={$_.InPlaceHolds -join ';'}},ArchiveStatus,ForwardingSmtpAddress,ExchangeGuid,ArchiveGuid,LegacyExchangeDN,
        @{n='EmailAddresses';e={$_.EmailAddresses -join ';'}}) 'exo_mailboxes'
  foreach ($m in $mbx) {
    $mk = "$($m.PrimarySmtpAddress)"
    if ($m.RecipientTypeDetails -eq 'UserMailbox') { Add-Edge $m.UserPrincipalName 'user' 'owns' $mk 'mailbox' 'primary' 'exo' }
    else { Add-Alias $m.UserPrincipalName $mk }
    Add-Edge $mk 'mailbox' 'uses_domain' ("domain:" + ($mk -split '@')[-1]) 'domain' 'PrimarySmtp' 'exo'
    foreach ($d in $m.GrantSendOnBehalfTo) { Add-Edge $d 'recipient' 'delegate_of' $mk 'mailbox' 'SendOnBehalf' 'exo' }
    if ($m.ForwardingSmtpAddress) { Add-Edge $mk 'mailbox' 'forwards_to' ($m.ForwardingSmtpAddress -replace '^smtp:', '') 'address' 'ForwardingSmtpAddress' 'exo' }
  }
  if ($IncludeMailboxPermissions) {
    Write-Host "   mailbox permissions for $($mbx.Count) mailboxes (slow)"
    foreach ($m in $mbx) {
      Get-EXOMailboxPermission -Identity $m.ExchangeGuid.ToString() -ErrorAction SilentlyContinue |
        Where-Object { -not $_.IsInherited -and $_.User -notmatch '^(NT AUTHORITY|S-1-5-)' } |
        ForEach-Object { Add-Edge $_.User 'user' 'delegate_of' $m.PrimarySmtpAddress 'mailbox' ($_.AccessRights -join '+') 'exo' }
      Get-EXORecipientPermission -Identity $m.ExchangeGuid.ToString() -ErrorAction SilentlyContinue |
        Where-Object { $_.Trustee -notmatch '^(NT AUTHORITY|S-1-5-)' } |
        ForEach-Object { Add-Edge $_.Trustee 'user' 'delegate_of' $m.PrimarySmtpAddress 'mailbox' 'SendAs' 'exo' }
    }
  }
  $dls = Get-DistributionGroup -ResultSize Unlimited
  Save ($dls | Select-Object DisplayName,PrimarySmtpAddress,GroupType,ManagedBy,RecipientTypeDetails) 'exo_distribution_groups'
  foreach ($dl in $dls) {
    foreach ($mm in (Get-DistributionGroupMember -Identity $dl.Identity -ResultSize Unlimited)) {
      $src = if ($mm.PrimarySmtpAddress) { "$($mm.PrimarySmtpAddress)" } else { $mm.Name }
      Add-Edge $src $mm.RecipientType 'member_of' $dl.PrimarySmtpAddress 'distribution_group' 'DL' 'exo'
    }
  }
  Save (Get-AcceptedDomain | Select-Object DomainName,DomainType,Default) 'exo_accepted_domains'
  Save (Get-InboundConnector | Select-Object Name,Enabled,ConnectorType,@{n='SenderIPAddresses';e={$_.SenderIPAddresses -join ';'}},@{n='SenderDomains';e={$_.SenderDomains -join ';'}},TlsSenderCertificateName) 'exo_inbound_connectors'
  Save (Get-OutboundConnector | Select-Object Name,Enabled,ConnectorType,@{n='SmartHosts';e={$_.SmartHosts -join ';'}},@{n='RecipientDomains';e={$_.RecipientDomains -join ';'}}) 'exo_outbound_connectors'
  Save (Get-TransportRule | Select-Object Name,State,Priority,Description) 'exo_transport_rules'
  Save (Get-OrganizationRelationship | Select-Object Name,Enabled,@{n='DomainNames';e={$_.DomainNames -join ';'}},MailboxMoveEnabled,FreeBusyAccessEnabled) 'exo_org_relationships'
}

# ---------------------------------------------------------------- SharePoint / OneDrive
if ('SharePoint' -notin $Skip) {
  if (-not $SpoAdminUrl) { Write-Warning 'SharePoint skipped: pass -SpoAdminUrl https://<tenant>-admin.sharepoint.com' }
  else {
    Write-Host '== SharePoint / OneDrive' -ForegroundColor Cyan
    Connect-SPOService -Url $SpoAdminUrl
    $sites = Get-SPOSite -Limit All -IncludePersonalSite $true
    Save ($sites | Select-Object Url,Title,Template,Owner,StorageUsageCurrent,GroupId,HubSiteId,SharingCapability,LockState,SensitivityLabel,LastContentModifiedDate) 'spo_sites'
    foreach ($s in $sites) {
      $t = if ($s.Url -match '-my\.sharepoint\.com/personal/') { 'onedrive' } else { 'site' }
      if ($s.Owner) { Add-Edge $s.Owner 'user' 'owns' $s.Url $t 'site owner' 'spo' }
      if ($s.GroupId -and $s.GroupId -ne [guid]::Empty -and $keyById[$s.GroupId.ToString()]) {
        Add-Edge $keyById[$s.GroupId.ToString()] 'group' 'linked_to' $s.Url $t 'group-connected' 'spo'
      }
      if ($s.HubSiteId -and $s.HubSiteId -ne [guid]::Empty) { Add-Edge $s.Url $t 'member_of' "hub:$($s.HubSiteId)" 'hub' 'hub association' 'spo' }
      # StorageUsageCurrent is in MB; warn above ~1.8 TB (FAQ planning limit 2 TB / 1M items)
      if ($t -eq 'onedrive' -and $s.StorageUsageCurrent -gt 1800000) { Write-Warning "OneDrive near 2 TB planning limit: $($s.Url)" }
    }
  }
}

# ---------------------------------------------------------------- Teams
if ('Teams' -notin $Skip) {
  Write-Host '== Teams' -ForegroundColor Cyan
  Connect-MicrosoftTeams | Out-Null
  $teams = Get-Team
  Save ($teams | Select-Object GroupId,DisplayName,Visibility,Archived,MailNickName) 'teams'
  foreach ($tm in $teams) {
    $gk = $keyById[$tm.GroupId]; if (-not $gk) { $gk = "grp:$($tm.DisplayName) ($($tm.GroupId.Substring(0,8)))" }
    Add-Edge $gk 'group' 'linked_to' "team:$($tm.DisplayName)" 'team' 'team' 'teams'
    foreach ($ch in (Get-TeamChannel -GroupId $tm.GroupId | Where-Object MembershipType -in 'Private','Shared')) {
      Add-Edge "team:$($tm.DisplayName)" 'team' 'contains' "channel:$($tm.DisplayName)/$($ch.DisplayName)" 'channel' "$($ch.MembershipType) (own site)" 'teams'
    }
  }
}

$edges   | Export-Csv -NoTypeInformation -Encoding utf8 -Path (Join-Path $OutDir 'edges.csv')
$aliases | Sort-Object alias -Unique | Export-Csv -NoTypeInformation -Encoding utf8 -Path (Join-Path $OutDir 'aliases.csv')
Write-Host "Done: $($edges.Count) edges, $($aliases.Count) aliases -> $OutDir" -ForegroundColor Green
