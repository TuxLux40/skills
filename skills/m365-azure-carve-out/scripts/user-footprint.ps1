<#
.SYNOPSIS
  Standard-user ("posture B") footprint collector for carve-out dependency mapping.
.DESCRIPTION
  Reads ONLY the signed-in user's own data via Microsoft Graph, using delegated scopes
  a normal user can consent to themselves — no admin role, no admin consent required for
  the self-scopes. Writes edges.csv (same schema as the admin collectors) so one person's
  run drops nodes into the shared graph. Run it per volunteer and merge the edges files;
  entanglement_graph.py accepts several --edges files.

  It cannot enumerate the whole directory, other mailboxes, or Azure RBAC — that needs
  posture A (admin). Where a scope is refused, the section is skipped with a note, not an error.

  Module: Microsoft.Graph.Authentication (plus Users, Groups, Sites, Teams, Mail if present).
  If delegated Graph is blocked in the tenant, use the UI sources in
  references/discovery-without-admin.md instead.
.EXAMPLE
  ./user-footprint.ps1 -OutDir ./out/me-alice
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory)] [string] $OutDir,
  # Side the signed-in user belongs to; stamped on edges so merged graphs self-seed.
  [ValidateSet('divest','retain','unknown')] [string] $Side = 'unknown'
)
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$edges = [System.Collections.Generic.List[object]]::new()
$seeds = [System.Collections.Generic.List[object]]::new()
function Add-Edge($s, $st, $r, $d, $dt, $ev = '') {
  if ($s -and $d) { $edges.Add([pscustomobject]@{ src_id = "$s".ToLower(); src_type = $st; rel = $r; dst_id = "$d".ToLower(); dst_type = $dt; evidence = $ev; source = 'me' }) }
}
function Try-Section($name, $block) {
  try { & $block } catch { Write-Warning "$name skipped (likely a permission your account doesn't have): $($_.Exception.Message)" }
}

Connect-MgGraph -NoWelcome -Scopes User.Read, User.ReadBasic.All, Sites.Read.All, Team.ReadBasic.All, Mail.Read
$me = Get-MgContext
Write-Host "Signed in as $($me.Account)" -ForegroundColor Cyan

$self = Get-MgUser -UserId (Get-MgContext).Account -Property id,userPrincipalName,displayName,companyName,department,jobTitle -ErrorAction SilentlyContinue
if (-not $self) { $self = Invoke-MgGraphRequest -Method GET -Uri 'v1.0/me?$select=id,userPrincipalName,displayName,companyName,department,jobTitle' }
$meUpn = $self.userPrincipalName ?? $self.UserPrincipalName
$seeds.Add([pscustomobject]@{ node_id = $meUpn; side = $Side })
"You: $meUpn  company=$($self.companyName)  dept=$($self.department)" | Tee-Object -FilePath (Join-Path $OutDir 'me.txt')

Try-Section 'manager' {
  $mgr = Invoke-MgGraphRequest -Method GET -Uri 'v1.0/me/manager?$select=userPrincipalName'
  if ($mgr.userPrincipalName) { Add-Edge $meUpn 'user' 'reports_to' $mgr.userPrincipalName 'user' 'manager' }
}
Try-Section 'memberOf' {
  $groups = (Invoke-MgGraphRequest -Method GET -Uri 'v1.0/me/memberOf?$select=id,displayName,mail,groupTypes').value
  $groups | ForEach-Object { Add-Edge $meUpn 'user' 'member_of' "grp:$($_.displayName)" 'group' 'direct' }
  $groups | Select-Object displayName, mail | Export-Csv -NoTypeInformation -Encoding utf8 (Join-Path $OutDir 'my_groups.csv')
}
Try-Section 'ownedObjects' {
  (Invoke-MgGraphRequest -Method GET -Uri 'v1.0/me/ownedObjects').value | ForEach-Object {
    $t = ($_.'@odata.type' -replace '#microsoft.graph.', ''); $n = $_.displayName
    Add-Edge $meUpn 'user' 'owns' "$t`:$n" $t 'owned'
  }
}
Try-Section 'joinedTeams' {
  $teams = (Invoke-MgGraphRequest -Method GET -Uri 'v1.0/me/joinedTeams?$select=id,displayName').value
  $teams | ForEach-Object { Add-Edge $meUpn 'user' 'member_of' "team:$($_.displayName)" 'team' 'joined' }
  $teams | Select-Object displayName | Export-Csv -NoTypeInformation -Encoding utf8 (Join-Path $OutDir 'my_teams.csv')
}
Try-Section 'people' {
  (Invoke-MgGraphRequest -Method GET -Uri "v1.0/me/people?`$top=50&`$select=userPrincipalName,displayName,companyName").value |
    Where-Object userPrincipalName | ForEach-Object { Add-Edge $meUpn 'user' 'interacts_with' $_.userPrincipalName 'user' "company=$($_.companyName)" }
}
Try-Section 'sharedWithMe' {
  (Invoke-MgGraphRequest -Method GET -Uri 'v1.0/me/drive/sharedWithMe').value | ForEach-Object {
    $owner = $_.remoteItem.shared.owner.user.displayName
    if ($owner) { Add-Edge $meUpn 'user' 'depends_on' "person:$owner" 'user' "file shared: $($_.name)" }
  }
}
Try-Section 'appRoleAssignments (my apps)' {
  (Invoke-MgGraphRequest -Method GET -Uri 'v1.0/me/appRoleAssignments?$select=resourceDisplayName').value |
    Sort-Object resourceDisplayName -Unique | ForEach-Object { Add-Edge $meUpn 'user' 'signs_into' "app:$($_.resourceDisplayName)" 'enterprise_app' 'My Apps tile' }
}
Try-Section 'oauth2 grants (apps I consented)' {
  (Invoke-MgGraphRequest -Method GET -Uri 'v1.0/me/oauth2PermissionGrants').value | ForEach-Object {
    Add-Edge $meUpn 'user' 'consented' "sp:$($_.clientId)" 'service_principal' $_.scope
  }
}

$edges | Export-Csv -NoTypeInformation -Encoding utf8 -Path (Join-Path $OutDir 'edges.csv')
$seeds | Export-Csv -NoTypeInformation -Encoding utf8 -Path (Join-Path $OutDir 'seeds.csv')
Write-Host "Done: $($edges.Count) edges from your account -> $OutDir" -ForegroundColor Green
Write-Host "Merge several people's edges.csv into one graph: entanglement_graph.py --edges out/*/edges.csv --seeds out/*/seeds.csv ..." -ForegroundColor DarkGray
