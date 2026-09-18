# TASKS.md

## Active

## Up Next
- Try the package against a real cross-repo use case (the thing this work is actually for) — will likely surface gaps the RFC didn't anticipate.

## Backlog
- Implement spool root resolution in `spool.py`: `PMP_SPOOL_ROOT` env var override, default `~/.local/state/pmp/<channel>/` (see DECISIONS.md "Spool root resolution and channel ownership")
- PyPI publishing workflow (deferred)
- `pmp[watch]` extra using `watchdog` for inotify-based consumption instead of polling (deferred idea)
- Crash recovery tooling (RFC 0 §4.7 leaves this manual/implementation-specific — a small CLI to sweep stale `processing/` entries back to `pending/` would help)
