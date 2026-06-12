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

### Source-drift checking (automated, costs API tokens)
A scheduled GitHub Action can run Claude with repo access to re-fetch key sources and diff them against the skill's claims, opening a PR with proposed updates:
- Official action: `anthropics/claude-code-action` (needs `ANTHROPIC_API_KEY` secret)
- Sensible cadence: monthly, scoped to one reference file per run to bound cost
- Keep human review on the PR — auto-merge of LLM-rewritten reference content is how errors compound silently

Not enabled by default: it costs money and the usage feedback loop above catches the important drift for free. Enable when the skill has users beyond its maintainer.

### What NOT to automate
- Tribal entries — provenance requires a human (or an agent in a real debugging session), not a crawler
- Wholesale re-distillation — a model rewriting the whole skill from sources each month destroys curation
