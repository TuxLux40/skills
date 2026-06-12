# Tribal Knowledge — Anecdotal Fixes (🟣 Last Resort)

Fixes from community discussion that worked for real users but have **no official documentation**. Consult only after the ✅ and ⚠️ fixes for the symptom have failed. Always disclose to the user that a fix from this file is anecdotal and cite its provenance line.

## Entry format

Every entry must carry provenance — an unsourced tribal fix is a rumor, not knowledge:

```markdown
### <symptom, phrased as user would say it>
- **Fix:** <exact commands/config>
- **Reversal:** <how to undo it>
- **Source:** <Discord server + channel / forum thread URL>, <date>
- **Confirmations:** <how many independent users reported it working>
- **Suspected mechanism:** <best guess why it works, or "unknown">
```

Entries with unknown mechanism are still valid — that is the nature of tribal knowledge — but say so explicitly.

## Maintenance rules

- When an official fix later lands (kernel patch, package update, wiki documentation), **move the knowledge to the appropriate reference file** at ✅/⚠️ tier and delete the entry here, noting the version that fixed it.
- Prefer entries that are reversible. Irreversible anecdotal fixes need a strong confirmation count and an explicit warning.
- Date matters: an entry older than ~2 years on a rolling-release distro is suspect — verify the underlying component still exists before suggesting it.

## Entries

*(none yet — populated from Discord channel exports and forum thread distillation)*
