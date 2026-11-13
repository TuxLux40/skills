# Dependency survey (send to each team)

Short, voluntary questionnaire to map what the organisation actually uses, from the people who use it. Aggregating many answers gives the real application and dependency map when IT can't or won't hand one over. Keep it to five minutes; no technical knowledge needed.

> We're separating our IT from the wider group and need to know what everyone relies on, so nothing breaks on the switchover day. Please answer for **your own work** — a few words each is fine. (If you're not sure of a system's exact name, describe it.)

**Your team / department:** ______________________

1. **What do you log into on a normal day?** Apps, websites, systems. *Easiest: open https://myapps.microsoft.com and send a screenshot of all your tiles.*

2. **If one thing stopped working for an hour, what would hurt most?** (e.g. email, a specific shared drive, the ERP, a booking system)

3. **Which vendor, supplier or customer portals do you use for your job?** (external websites you log into)

4. **Shared drives / shared mailboxes / Teams you depend on?** (names or paths — e.g. `\\fileserver\finance`, "Orders" shared mailbox, "Project X" team)

5. **Who outside our part of the company do you rely on** for approvals, data, or systems? (a person, a team, or "head-office IT")

6. **Anything that emails you automatically?** (invoices, tickets, scanners/printers, alerts) — which system sends it?

7. **Hardware/tools tied to a system?** (meeting-room screens, label printers, badge readers, lab/plant equipment)

---

## How to use the answers (for the analyst)

- **Count app mentions across respondents** → rough criticality. An app named by many is a Day One "must keep working".
- **An app/drive/system named by both the divested and the retained side → `shared`** node (an entanglement). Flag it.
- Turn each answer into a graph edge: `person --signs_into--> app`, `person --depends_on--> \\server\share`, `team --depends_on--> head-office-IT`.
- Q2 feeds the **Day One minimum** list directly. Q5 feeds the **TSA** (cross-company services). Q3 feeds the **external SSO / contract** list (re-federate or re-contract on the new tenant).
- Keep it aggregated. This is a "what do you use" survey, not monitoring of individuals — don't turn it into per-person activity tracking.
