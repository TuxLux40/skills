# Oliver — Aktenwurzel und Schreibweg

Homelab overlay for Signal scans. Generic method stays in `SKILL.md`.

## Roots

| View | Path | Access from ai-hub |
|------|------|--------------------|
| Canonical tree | `/home/oliver/documents` on os93-nas | SSH as `oliver` |
| Read mount | `/mnt/pve/documents` | CIFS **RO** (`//192.168.178.2/personal_folder/documents`) |

Do not write through the CIFS mount. Do not invent top-level categories; the tree already has `Anbieter`, `Anwaelte`, `Arbeit_Bildung`, `Behoerden`, `Finanzen`, `Gesundheit`, `Haustiere`, `Import`, `Sport`, `Versicherungen`, `Wohnungen`.

## SSH

```bash
ssh -i ~/.ssh/nas_sync_key -o IdentitiesOnly=yes oliver@192.168.178.2
```

LAN preferred (`192.168.178.2`). Key: `ai-hub-nas-sync`. Git identity is **not** set on the NAS user — pass `-c user.name='Hermes Agent' -c user.email='agents@deroliver.me'` on each commit.

## Git pitfalls

- Branch: `main`. No remote configured.
- Working tree is often dirty under `Arbeit_Bildung/Bewerbungen/`. Stage **only** the files this pass added.
- `git status` / `git commit` over CIFS is slow and read-only anyway — run git on the NAS over SSH.

## Naming vs existing folders

Match siblings. Example already in tree (do not copy IDs into new files unless they belong):

- Generic: `2026-08-30--Mahnung_Absender.pdf`
- Case files that already use exhibit prefixes: keep `Anlage_…--YYYY-MM-DD--…`

## Out of scope

- smart-okf ingest / dream (deferred unless asked)
- New folder layouts
- Committing unrelated dirty files
