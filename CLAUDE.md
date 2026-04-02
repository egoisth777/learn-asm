# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

Meta-repository that manages multiple sub-repositories. Each child directory listed in REPOS.json is an independent git repo; this repo tracks only the orchestration scripts and the registry.

## Structure

- `REPOS.json` — flat JSON array: `[{url, path}, ...]` (tracked)
- `.scripts/` — management scripts and shared lib (tracked)
  - `init.py` — clone all repos on a fresh machine, configure hooks
  - `sync.py` — pull existing repos, clone missing, recurse into children with `.scripts/sync.py`
  - `add.py` — register and clone a new repo
  - `track.py` — scan root for on-disk repos not yet in REPOS.json, register them
  - `rm.py` — unregister and delete a repo
  - `test.py` — linter, integrity checker, and regression tests (run before committing)
  - `lib/` — shared Python modules and platform-native scripts
  - `hooks/` — git hooks (pre-commit runs `test.py`)

## Architecture

This repo follows a **shim architecture** (same pattern as `cfg/`):

- `.scripts/*.py` — thin orchestration shims (arg parsing, JSON I/O, subprocess dispatch)
- `.scripts/lib/*.py` — shared Python modules (REPOS.json I/O)
- `.scripts/lib/*.ps1` — Windows-native scripts for OS operations
- `.scripts/lib/*.sh` — Linux/Mac-native scripts for OS operations

**Python only does orchestration.** All OS-touching operations (directory deletion, git commands) MUST be in platform-native scripts (`.ps1`/`.sh`), not in Python.

## Repo Hierarchy Principle

- If a repo contains sub-repos, it MUST have `.scripts/` and `REPOS.json`
- If a repo is a leaf (contains actual content), it has neither

## Key Details

- Sub-repos live directly under root (flat layout, no platform bucketing)
- `REPOS.json` is the single source of truth for which repos are managed
- Scripts are run as `python .scripts/init.py`, `python .scripts/add.py <url> [path]`, etc.
- Every path in REPOS.json must also appear in `.gitignore`
- `sync.py` recurses into children that have their own `.scripts/sync.py`

## Testing & Linting

**Run `python .scripts/test.py` before claiming any work is complete. All phases must pass (exit 0).**

The test suite has three phases:

1. **Lint** — AST-based shim enforcement + path rule checks across `.py`/`.ps1`/`.sh`
2. **Integrity** — REPOS.json schema, .gitignore consistency, on-disk warnings
3. **Regression** — unittest cases for lib/ modules

A pre-commit hook runs `test.py` automatically. Activate with: `git config core.hooksPath .scripts/hooks`

## Rules for Writing Code in `.scripts/`

### Shim rules (enforced by linter)
- **No `shutil.rmtree`** — use native `rmtree.ps1`/`.sh`
- **No `os.symlink`, `Path.symlink_to`** — use native scripts
- **No `os.remove`, `os.unlink`, `Path.unlink`** — use native scripts
- **No `subprocess.run(..., shell=True)`** — call a script file, not inline shell
- **No `os.environ` mutation** — environment changes belong in native scripts
- **No `os.path.expanduser`** — `~` expansion belongs in native scripts

### Path rules (enforced by linter)
- All paths must be maximally relative — computed from `__file__` or `ROOT`, never hardcoded
- No drive letters (`C:\`, `E:\`) or mount points (`/home/`, `/Users/`, `/mnt/`)
- No `~`, `$HOME`, or `%USERPROFILE%` in Python code
- No string concatenation with path separators — use `pathlib.Path` or `os.path.join`
- REPOS.json `path` field must be a bare name (no slashes)

### Adding native scripts
- Place in `.scripts/lib/` with `.ps1` (Windows) and `.sh` (Linux/Mac) variants
- Python calls them via `subprocess.run` with a helper like `_rmtree_cmd()`
- No hardcoded absolute paths in native scripts either (comments are exempt)

## Key Differences from cfg/

- No platform bucketing (flat repo list, no `platform` field in REPOS.json)
- No symlinks or `act/` directory
- No `platform.py` or `links.py`
- Sub-repos live directly under root, not under platform directories
