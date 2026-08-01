# Maintenance — When and How to Update

This skill describes a rolling-release ecosystem. Parts of it WILL go stale. This file defines update triggers and the feedback loop.

## Update triggers (when to touch what)

| Trigger | What to update | How you notice |
|---------|---------------|----------------|
| A documented fix **fails** during a real debugging session | The failing entry — fix it or demote to 🟣 tribal with a "broken since" note | The agent using the skill hits it; see feedback loop below |
| A fix **not in the skill** solves a session | Add it at the appropriate tier with provenance | Same |
| New Proton / GE-Proton major release | `wine-proton.md` launch options, HDR table in `display.md` | Watch github.com/GloriousEggroll/proton-ge-custom releases |
| New Mesa major release | `gpu.md` RADV notes, raytracing/HDR minimum versions | Mesa release notes |
| Kernel releases with gaming-relevant changes (ntsync, amdgpu) | `performance.md`, `gpu.md` | kernel release summaries (Phoronix etc.) |
| NVIDIA driver branch release | `gpu-nvidia.md` (explicit-sync, GSP, version-specific quirks) | NVIDIA Linux forum / release notes |
| Wayland color management adoption milestones | `display.md` — gamescope may stop being the only HDR path | compositor release notes |
| Tribal entry gets official fix | Graduate entry to ✅/⚠️ in the proper file, delete from `tribal.md` | Periodic review of tribal.md dates |
| Tribal entry >2 years old | Verify component still exists; delete if stale | Same |

## Feedback loop (the cheap, high-signal path)

The best update signal is **usage**: when an agent applies this skill and the outcome contradicts it. If you run this skill locally, add to your agent's project instructions:

> After a gaming debugging session where steam-debugger was used: if a documented fix failed or an undocumented fix succeeded, update the skill repo accordingly (tier-appropriate, with provenance) and commit.

This turns every debugging session into a potential skill improvement — no scheduled review needed for the content that matters most.

## Automation

### Link rot (automated, free)
`.github/workflows/linkcheck.yml` runs [lychee](https://github.com/lycheeverse/lychee) monthly over all markdown and opens an issue on dead links. Dead link = upstream moved = content may have changed too. Treat linkcheck issues as review prompts, not just URL fixes.

### Source-drift checking (automated via Copilot coding agent) — ENABLED
`.github/workflows/drift-check.yml` runs monthly (15th): picks one reference file by month rotation, opens a scoped task issue, and assigns it to the GitHub Copilot coding agent, which re-checks sources and opens a minimal-diff PR. Manual run: workflow_dispatch with `target=<file>`.

Guardrails:
- One file per issue bounds scope; issue body forbids wholesale rewrites and touching other files
- PR-only, never merges — human review stays mandatory
- Requires Copilot coding agent enabled for the repo; if the auto-assign step fails (the assignment API has churned before), the issue stays open — assign to Copilot manually in the UI

### What NOT to automate
- Tribal entries — provenance requires a human (or an agent in a real debugging session), not a crawler
- Wholesale re-distillation — a model rewriting the whole skill from sources each month destroys curation
