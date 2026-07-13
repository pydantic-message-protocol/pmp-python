# TASKS.md

## Active

## Up Next
- Add `.github/workflows/ci.yml`: build + run tests (`uv run --no-project --with-editable . --with pytest pytest`) on push/PR. No publish step for now.
- Try the package against a real cross-repo use case (the thing tomorrow's session is actually for) — will likely surface gaps the RFC didn't anticipate.

## Backlog
- PyPI publishing workflow (deferred)
- `pmp[watch]` extra using `watchdog` for inotify-based consumption instead of polling (deferred idea)
- Crash recovery tooling (RFC 0 §4.7 leaves this manual/implementation-specific — a small CLI to sweep stale `processing/` entries back to `pending/` would help)
