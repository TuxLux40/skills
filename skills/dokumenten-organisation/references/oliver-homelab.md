# Oliver — Aktenwurzel und Schreibweg

Homelab overlay for Signal scans. Generic method stays in `SKILL.md`.

## Roots

| View | Path | Access from ai-hub |
|------|------|--------------------|
| Canonical tree | `/home/oliver/documents` on os93-nas | SSH as `oliver` |
| Read mount | `/mnt/pve/documents` | CIFS **RO** (`//192.168.178.2/personal_folder/documents`) |

Do not write through the CIFS mount. Do not invent top-level categories; the tree already has `Anbieter`, `Anwaelte`, `Arbeit_Bildung`, `Behoerden`, `Finanzen`, `Gesundheit`, `Haustiere`, `Import`, `Sport`, `Versicherungen`, `Wohnungen`.

## SSH write path (Oliver 2026-09-27)

```bash
ssh -i ~/.ssh/nas_sync_key -o IdentitiesOnly=yes oliver@os93-nas
```

- Host: **`oliver@os93-nas`** (Tailscale MagicDNS). Prefer that over bare `192.168.178.2`.
- Key: `~/.ssh/nas_sync_key` (`ai-hub-nas-sync`), always `IdentitiesOnly=yes`.
- **Upload:** stream bytes over SSH stdin — `ssh … "cat > '/home/oliver/documents/…'" < localfile`. Verify size after.
- **Do not** use: CIFS `/mnt/pve/documents` (RO), SFTP mounts, or `scp` (NAS SFTP subsystem fails: `dest open … No such file` / `stat remote: Unknown status`).
- Fallback only if SSH file write fails: `tailscale file cp` — not the default.
- Moves/renames: `ssh … mv` on the NAS, never mount-side moves.
- Git identity is **not** set on the NAS user — pass `-c user.name='Hermes Agent' -c user.email='agents@deroliver.me'` on each commit.

## Git pitfalls

- Branch: `main`. No remote configured.
- Working tree is often dirty under `Arbeit_Bildung/Bewerbungen/`. Stage **only** the files this pass added.
- Run git **on the NAS over SSH** — never via CIFS.

## Naming vs existing folders

Match siblings. Example already in tree (do not copy IDs into new files unless they belong):

- Generic: `2026-08-30--Mahnung_Absender.pdf`
- Case files that already use exhibit prefixes: keep `Anlage_…--YYYY-MM-DD--…`

## Out of scope

- smart-okf ingest / dream (deferred unless asked)
- New folder layouts
- Committing unrelated dirty files
