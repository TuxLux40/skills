---
name: stow
description: Expert guidance for GNU Stow — the symlink farm manager used to manage dotfiles and software installations. Use this skill whenever the user asks about stowing packages, managing dotfiles with stow, stow conflicts, tree folding/unfolding, --adopt, ignore lists, .stowrc resource files, chkstow, or any stow command options. Also trigger for questions about "why isn't my stow working", "stow conflict", "stow symlink not created", or any debugging of stow-managed configurations. This skill is essential for all stow-related tasks even if the user just says "stow fish" or "re-stow my dotfiles".
---

# GNU Stow (v2.4.1)

GNU Stow is a symlink farm manager. It takes packages living in a **stow directory** and creates symlinks in a **target directory** so files appear installed there. The classic dotfiles use case: packages live in `~/Projects/dotfiles/`, each mirrors the home-relative path (e.g. `fish/.config/fish/config.fish`), and stow links them into `~`.

## Core concepts

| Term | Meaning |
|------|---------|
| **stow directory** | The repo root (e.g. `~/Projects/dotfiles`) |
| **target directory** | Where symlinks land (default: parent of stow dir; for dotfiles: `~`) |
| **package** | A top-level subdirectory of the stow dir (e.g. `fish/`, `nvim/`) |
| **installation image** | The layout inside a package, mirroring the target structure |

Stow only ever creates symlinks that point **into** the stow directory. It never deletes content it doesn't own.

## Common operations

```bash
# Always run from the stow directory (repo root)
cd ~/Projects/dotfiles

# Stow a package
stow -t ~ fish

# Dry run — see what would happen without changing anything
stow -n -v -t ~ fish

# Restow (unstow + stow) — useful after renaming/moving files
stow -R -t ~ fish

# Unstow (remove symlinks)
stow -D -t ~ fish

# Adopt existing files into the repo (moves them into the package, then links back)
stow --adopt -t ~ fish && git restore fish/

# Stow multiple packages at once
stow -t ~ fish nvim ghostty

# Mix operations in one pass (faster — deduplicates fold/unfold)
stow -D old-pkg -S new-pkg -t ~
```

## Important flags

| Flag | Effect |
|------|--------|
| `-t dir` | Set target directory |
| `-d dir` | Set stow directory (default: current dir) |
| `-n` / `--simulate` | Dry run; combine with `-v` |
| `-v` / `--verbose` | Show what's happening (repeat for more: `-vvv`) |
| `-D` | Delete/unstow package(s) |
| `-R` | Restow: unstow then stow |
| `-S` | Explicitly stow (useful when mixing `-D` and `-S`) |
| `--adopt` | Move pre-existing target files into the package, then link |
| `--no-folding` | Always create real dirs; never create a single dir symlink |
| `--dotfiles` | Treat `dot-` prefix in package as `.` (for repos avoiding hidden dirs) |
| `--ignore=REGEXP` | Skip files matching Perl regex (anchored at end of filename) |
| `--defer=REGEXP` | Skip files already stowed by another package |
| `--override=REGEXP` | Force-stow even if another package already owns the link |

## Tree folding and unfolding

Stow minimizes symlinks via **tree folding**: if a package is the only thing populating a directory, stow creates one symlink for the whole directory rather than individual symlinks for each file.

```
# First package stowed into empty target:
~/.config → ~/Projects/dotfiles/fish/.config   (folded — one symlink)

# Second package also needs .config/:
# Stow "splits open" the fold: removes the dir symlink, creates a real dir,
# then links individual contents from both packages.
~/.config/fish → ~/Projects/dotfiles/fish/.config/fish
~/.config/nvim → ~/Projects/dotfiles/nvim/.config/nvim
```

When unstowing, if a real directory ends up containing symlinks to only one package, stow **refolds** it back to a single dir symlink. Use `--no-folding` to suppress this behavior.

## Conflicts

Stow uses a **two-phase algorithm**: it scans for all conflicts first, reports them, then either makes no changes (if conflicts found) or applies everything. You'll never get a partially-stowed state from a conflict.

A conflict occurs when stow needs to create a symlink but the path already exists and is not owned by stow (not a symlink pointing into the stow directory).

**Resolving conflicts:**
- If the file is one you want to bring into the repo: `--adopt` (moves file into the package, then links)
- After `--adopt`, run `git restore <package>/` so the repo version wins (not the local file)
- If you just want the stow version to win: manually remove the conflicting file first

## Ignore lists

Stow checks for ignore patterns in this order (first found wins):

1. **`.stow-local-ignore`** in the package directory (Perl regexes, one per line)
2. **`~/.stow-global-ignore`**
3. **Built-in defaults** (ignores `.git`, `.gitignore`, `CVS`, editor backups, etc.)

The built-in list already ignores `.gitignore`, `.gitmodules`, `~` backup files, `#autosave#` files, and VCS directories — so you usually don't need an ignore list for dotfiles repos.

```
# Example .stow-local-ignore (Perl regexes)
\.DS_Store
README.*
\.env$
```

Regexes without `/` match against the basename. Regexes with `/` match against the full path relative to the package root (prefixed with `/`).

## Resource files (.stowrc)

Default options can be set in `.stowrc` (current dir) or `~/.stowrc` (home). Useful for dotfiles repos:

```ini
# ~/Projects/dotfiles/.stowrc
--target=$HOME
--verbose
```

With this file, `stow fish` from the repo root automatically targets `~` without `-t ~`. Command-line options always override resource file options.

Note: `-D`, `-S`, `-R`, and package names are ignored in resource files.

## Target maintenance (chkstow)

```bash
# Find broken symlinks in target tree
chkstow -t ~ --badlinks

# Find non-symlink files in target (things stow didn't create)
chkstow -t ~ --aliens

# Show which package owns each symlink
chkstow -t ~ --list
```

## Adding a new dotfiles package

1. Create the package directory mirroring the home-relative path:
   ```
   mkdir -p nvim/.config/nvim
   # Top-level entry must be hidden (.config, .bashrc, etc.)
   # install.sh skips packages where the top-level entry isn't hidden
   ```
2. Place config files inside, maintaining the exact target structure
3. Stow it: `stow -t ~ nvim`

**Key constraint for this repo**: every package's top-level entry under the package dir must be a hidden name (`.config`, `.bashrc`, etc.). `install.sh` skips packages with non-hidden top-level entries since they're not `$HOME` packages.

## The --adopt workflow (repo wins)

When you have existing config files at `~` that you want to bring under stow management:

```bash
stow --adopt -t ~ fish     # moves ~/.config/fish → repo, creates symlink
git restore fish/           # discard local version; restore tracked version
stow -R -t ~ fish          # restow to be sure everything is clean
```

Without `git restore`, the local (possibly modified) files become the repo content — which you may or may not want.

## Debugging tips

- **Always dry-run first**: `stow -n -v -t ~ <package>` — shows exactly what would happen
- **Verbosity levels**: `-v` through `-vvvvv` (5 levels); `-vv` is usually enough for debugging
- **Check for conflicts**: if stow exits without doing anything, look for "CONFLICT" in output
- **Orphaned links**: use `chkstow -t ~ --badlinks` to find broken symlinks after removing packages
- **Tree fold confusion**: if a dir symlink blocks a new package, stow splits it automatically — run with `-v` to see this happening
