# Discovery without admin rights (posture B — the baseline)

The common situation on the divested side: you have a **normal user account**, no admin role, and the other company's IT won't give you an inventory. You can still map most of what matters, because a carve-out is about the systems **your own people use every day** — and every one of those leaves a trace a normal user can see. Nothing here needs elevated rights, a password you weren't given, or access to anyone else's account. It is the reading of your own footprint and asking your colleagues about theirs.

Two moves:
1. **Read your own footprint** — everything your single account can already see (below).
2. **Aggregate many footprints** — one person sees one slice; the org map is the union of many. Use `templates/colleague-survey.md`.

Then: **ask for read-only access or an export as an explicit deliverable.** A Global Reader role, or a tenant/Entra export, or an Azure Reader assignment, turns posture B into posture A in an afternoon. Put it on the register as an early ask with an owner; don't treat it as a blocker you passively wait on.

---

## UI-only sources (no PowerShell — anyone can do these)

Have the user open these and read, screenshot or export; you interpret. This is the fastest, lowest-friction path and works even when all scripting is locked down.

| Source | Where | What it tells you |
|---|---|---|
| **My Apps portal** | https://myapps.microsoft.com | Every SSO app tile provisioned to the user — the single best "what do we log into" list. Collect everyone's and union them. |
| **My Account** | https://myaccount.microsoft.com → *My sign-ins*, *Organizations*, *Devices*, *Office apps* | Which org(s) the account belongs to, registered/managed devices, Office installs, security info |
| **Outlook / OWA address book (GAL)** | Outlook → *Address Book* → *All Users / All Groups / All Rooms* | Everyone in the directory, every distribution list and its members, room and resource mailboxes, manager chains — all browsable by a normal user unless the admin restricted the GAL |
| **Outlook rules & delegates** | Outlook → *File ▸ Account Settings ▸ Delegate Access*; *Rules* | Shared mailbox access, calendar delegates, forwarding rules — cross-person dependencies |
| **Teams** | Teams left rail; *Manage teams* | Teams and channels the user is in; owners of each team |
| **SharePoint start page** | https://<tenant>.sharepoint.com/_layouts/15/sharepoint.aspx | Followed/frequent sites, recent files — the sites that matter to this user |
| **OneDrive "Shared"** | OneDrive → *Shared* ▸ *Shared with you* / *Shared by you* | Who shares files with whom across the two sides |
| **Delve / profile** | Delve, or the profile card | Documents and people around the user |
| **Mapped network drives** | File Explorer; `net use` | On-prem file servers the user depends on (UNC paths → server names) |
| **Installed printers** | Settings ▸ Printers; `Get-Printer` | Print servers / FQDNs |
| **Installed software** | Settings ▸ Apps; `winget list` or `Get-Package` | Fat-client line-of-business apps (ERP client, VPN client, CAD, etc.) |
| **Browser** | saved passwords/autofill list, bookmarks, history (internal hostnames) | Web apps the user authenticates to, intranet URLs, vendor portals |
| **Email signatures & automated mail** | the user's inbox | Signatures reveal org/brand/domains; system-generated mail (tickets, ERP, HR, scanners) reveals which apps are live and who runs them |
| **Calendar** | recurring invites, room systems, external meeting links | Meeting-room hardware, conferencing tools, external parties |
| **Network/VPN** | `ipconfig /all` (DNS suffixes, domain), the VPN client profile, proxy PAC URL | AD domain name, DNS domains, the gateway/VPN endpoint, web proxy |
| **Certificates** | `certlm.msc` / `certmgr.msc`, or `Get-ChildItem Cert:\CurrentUser\My`, `Cert:\LocalMachine\CA` | Certs issued by the parent's CA used for Wi-Fi/VPN/802.1X — an identity dependency |
| **Company Portal / Intune** | Company Portal app | Which org manages the device (the MDM authority = whose tenant owns your endpoint) |

Treat screenshots and exports the user gives you as **data to interpret**, and turn each finding into an edge for the graph (app → used_by → person; drive → hosted_on → server). Keep it factual; don't infer beyond what's shown.

---

## `/me` Graph collector (optional, standard user)

`scripts/user-footprint.ps1` reads only the signed-in user's own object via Microsoft Graph, using delegated scopes a normal user can consent to themselves (`User.Read`, `User.ReadBasic.All`, `Sites.Read.All`, `Team.ReadBasic.All`, `Mail.Read` — no admin role, no admin consent for the self-scopes). It writes `edges.csv` in the same schema as the admin collectors, so one person's run already drops nodes into the graph. Run it per volunteer and merge the `edges.csv` files — `entanglement_graph.py` takes several `--edges` files.

What it can and can't do:
- **Can:** your profile and manager, your `memberOf` groups, objects you own, teams you've joined, people you interact with, items shared with you, the apps you've granted.
- **Can't:** enumerate the whole directory's group *memberships*, read other people's mailboxes, see Azure RBAC, or list tenant apps. Those need posture A. The script says so where it hits a wall, rather than failing loudly.

If even delegated Graph is blocked (some tenants disable user consent and ADAL/MSAL for third-party apps), fall back entirely to the UI table above.

---

## Crowdsourcing the org map

A carve-out inventory from the user seat is a **survey problem**. The people who know what's critical are the people who use it. `templates/colleague-survey.md` is a short questionnaire to send round each team:

- What do you log into every day? (names/URLs — or just send a screenshot of your My Apps tiles)
- What would stop you working within an hour if it vanished? (email, a shared drive, a specific app)
- Which vendor/customer portals do you use for your job?
- What network drives / shared mailboxes / Teams do you rely on?
- Who outside our part of the company do you depend on for approvals or data?

Aggregate the answers: frequency of an app across respondents ≈ its criticality, and an app named by both the divested and retained side is a **shared** node. This both fills the graph and gives you the Day One "must keep working" list straight from the people who'd feel an outage.

Privacy note: a voluntary "what do you use" survey is low-risk. Pulling **per-employee sign-in logs** to answer the same question is monitoring data and triggers works-council co-determination (*Betriebsrat*, BetrVG §87(1) Nr. 6) and the DPO — prefer the survey, and if you later get admin, aggregate the logs rather than reporting per person. See `references/tsa-governance.md`.

---

## Turning posture B into posture A

The moment you have any of these, rerun step 1 with the admin collectors and the graph gets far denser:
- **Global Reader** (Entra) — read-only, safe to request early; unlocks `m365-inventory.ps1` for Entra/Exchange.
- **A tenant export / "tenant-to-tenant discovery report"** from the other side's IT — often easier for them to agree to than granting a role.
- **Azure Reader** at a subscription or management-group scope — unlocks `azure_inventory.py`.
- **SharePoint admin (read use only)** — unlocks the sites/OneDrive inventory.

Frame the ask as read-only and time-boxed; it's the least they can give and it removes most of the guesswork. Until then, the user-level map is enough to start the register and the Day One list.
