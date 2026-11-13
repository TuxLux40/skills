# Inventory & dependency discovery

You can't sequence what you can't see. Two things to capture: **what exists** (the inventory) and **what needs what** (the dependencies). Dependencies are the part people skip and the part that breaks cutovers — the app that silently calls an old database, the script hard-coded to a server name, the firewall rule nobody documented.

## Two kinds of evidence

- **Declared** (configuration, asset lists, licences, invoices): complete for what's recorded, blind to what's actually used.
- **Observed** (logs, network traffic, "turn it off and see who screams"): shows real use, but only within the window you watch — a 30-day log misses the quarterly job, the year-end run, the annual audit.

Use both. Declared finds the items; observed tells you which dependencies are *live* and how critical. Anything only declared and not seen recently is a "confirm with the owner", not a safe delete.

## Finding dependencies you can't see from config

| Technique | Finds |
|---|---|
| **Ask the owners / users** | the real "what breaks if this stops" — often better than any tool at small scale (see the carve-out skill's colleague survey idea) |
| **Network flows / connection logs** | which server talks to which (netflow, VPC/VNet flow logs, `ss`/`netstat`, firewall logs) |
| **Auth logs** | who/what logs into a system (a service account authenticating = a dependency) |
| **DNS query logs / hosts files** | apps resolving a name you're about to retire |
| **Scheduled jobs** | `cron`, Task Scheduler, CI pipelines, ETL schedulers — the integrations that run at night |
| **Config & code grep** | hard-coded hostnames, IPs, connection strings, API URLs, licence servers in configs and repos |
| **Monitoring / APM** | service maps many tools already draw |
| **Billing / invoices** | shadow SaaS and forgotten subscriptions nobody listed |
| **Certificates & secrets** | what trusts the CA/secret you're moving |

The "**turn it off and see who screams**" test (a controlled, announced maintenance window) is crude but finds dependencies nothing documented. Use it where logs are thin and the blast radius is acceptable.

## What to inventory per domain

- **Accounts/identity:** users, groups, service accounts, API keys, SSO integrations, MFA methods.
- **Data stores:** databases, file shares, object storage, mailboxes — size, record counts, who writes to them.
- **Applications:** what each needs (its DB, auth, other services it calls) and what calls it.
- **Network:** DNS zones & records, IP ranges, VPN/circuits, firewall rules, load balancers, certificates.
- **Endpoints:** devices, how they're managed, what they map/mount.
- **Integrations:** scheduled jobs, webhooks, data feeds, partner/EDI interfaces.
- **Contracts/licences:** what's tied to the source, renewal dates, affiliate/transfer terms, reserved capacity.

Record each as a row in `templates/inventory.example.csv` and each dependency as a row in `templates/deps.example.csv`; the wave planner turns them into an ordering and flags cycles and typos (dangling deps).

## Scale note

- **Individual:** the inventory is a list you can hold in your head made explicit — accounts, where your files are, what's tied to your email address (password resets!). The dependency that bites: everything that uses your old email as its recovery address.
- **KMU:** a spreadsheet and an afternoon of asking each team "what do you use". Good enough.
- **Enterprise:** a discovery tool / CMDB + agentless dependency mapping; expect the inventory itself to be a workstream, and expect it to be wrong until observed traffic corrects it.
