# CLAUDE.md

## What this is
Python reference implementation of **PMP (Protocol for Message Passing)**, RFC 0 / PMP/Spool 0.0. Companion to `github.com/pydantic-message-protocol/rfc`, where the spec lives (`rfcs/0000-pmp-spool.md`). This repo only implements the RFC — it does not define or amend the protocol.

## Constraints
- Once pushed, installable via `pip install git+https://github.com/pydantic-message-protocol/pmp-python.git`.
- `pyproject.toml` uses the `hatchling` build backend (plain PEP 517, no `uv` required to install).
- The only runtime dependency is `pydantic`. Everything else (atomic rename, fsync, advisory locking via `fcntl`, timestamps, filenames) is Python stdlib.
- Dev tooling uses the global uv-managed venv — see `~/.claude/CLAUDE.md` for that rule. Never create a per-project virtual environment here.
- Commit convention: Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, ...).

## Control files
- `TASKS.md` — active to-do, up next, backlog.
- `DECISIONS.md` — decisions with rationale and status (open / blocking / decided).
- `IDEAS.md` — scratch. Everything lands here first, gets promoted to `TASKS.md` or `DECISIONS.md`.

## Cross-project rules
Not here. Cross-project preferences (Python/uv environment, the control-file bootstrap methodology, commit-isolation for control files) live in `~/.claude/CLAUDE.md` (user-level, auto-loaded for every project).
