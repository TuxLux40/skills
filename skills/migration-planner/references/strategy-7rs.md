# Strategy per item: the 7 Rs

Decide what happens to each item *before* planning waves. The 7 Rs come from AWS Prescriptive Guidance, building on Gartner's original Rs; the labels are industry-standard and apply to any target, not just AWS. Pick exactly one per item.

| R | What it means | Effort | Use when | Watch out |
|---|---|---|---|---|
| **Retire** | switch it off — nobody needs it | trivial | usage near zero, duplicated by another system, obsolete | confirm "nobody" with observed usage, not assumption; archive under retention first |
| **Retain** | leave it where it is, for now | none (now) | not worth moving yet; a dependency not ready; EOL soon anyway | give it a **review date** — "retain" with no review becomes "forgotten" |
| **Rehost** | lift-and-shift, no changes | low | speed matters, app is portable, you'll optimise later | you carry the old design's inefficiencies and costs across |
| **Relocate** | move at hypervisor/container level, no OS/app change | low | VMware→VMware-on-cloud, container repacking | target must support the same virtualization/runtime |
| **Repurchase** | drop-and-shop: replace with a different product/SaaS | medium | the old thing is replaceable off-the-shelf (email, CRM, ticketing) | data export/import fidelity; retraining; feature gaps |
| **Replatform** | lift-and-reshape: small changes to fit the target | medium | a managed DB, a new runtime, modest optimisation pays off | scope creep — keep the reshaping small |
| **Refactor / re-architect** | rebuild significant parts | high | the current design blocks what the business needs | **most complex and riskiest — rarely do it *during* a move;** migrate first, refactor after |

## Decision shortcut

1. **Can it just be switched off?** → Retire. (Cheapest migration is the one you don't do.)
2. **Does it have to move now?** If not, and it's not blocking → Retain with a date.
3. **Is there a better off-the-shelf replacement?** → Repurchase.
4. **Does it move as-is?** → Rehost (or Relocate if it's whole-VM/container).
5. **Small changes make the target much better/cheaper?** → Replatform.
6. **Only a rebuild solves the real problem?** → Refactor — and consider doing it *after* a rehost, not as the migration.

Default to the lowest-effort R that meets the goal. "Refactor everything while we move" is how migrations miss deadlines.

## The same framework at each scale

**Individual** — leaving a provider:
- Retire: the three newsletters and the trial account you forgot. Close them.
- Repurchase: Evernote → a different notes app; one password manager → another (export/import).
- Rehost: copy your files as-is to the new drive/cloud.
- Retain: the old email account kept as an archive/forwarding address for a year.

**KMU** — switching core tools:
- Repurchase: on-prem Exchange → a hosted mail provider; desktop accounting → cloud accounting.
- Rehost: file server → cloud file storage, same folder structure.
- Replatform: self-managed MySQL → a managed database.
- Retire: the intranet nobody opens.

**Enterprise** — portfolio migration:
- Run a portfolio assessment and tag every application with an R. Typical split skews to Rehost/Replatform for speed, a long Retire tail (often 10–20% of apps), deliberate Retain for things pending their own project, and Refactor reserved for a few strategic systems.
- The R drives the wave: Retire items need only a decommission wave; Rehost/Relocate move early; Refactor items are their own sub-projects.

The **infrastructure strategy follows the application strategy** — decide the app's R first, and the servers/network/storage under it inherit it.
