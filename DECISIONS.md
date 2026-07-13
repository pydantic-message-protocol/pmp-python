# DECISIONS.md

Entry format:
```
## [STATUS] Title
- Date:
- Rationale:
- Status: OPEN | BLOCKING | DECIDED
```

## [DECIDED] License
- Date: 2026-07-11
- Rationale: Apache 2.0, matching the `rfc` repo.
- Status: DECIDED

## [DECIDED] Python package dependencies
- Date: 2026-07-11
- Rationale: `pydantic` is the only runtime dependency — everything else is stdlib.
- Status: DECIDED

## [DECIDED] Build backend
- Date: 2026-07-11
- Rationale: `hatchling`, so a plain `pip install git+...` works without requiring `uv`.
- Status: DECIDED

## [DECIDED] Repo name and org
- Date: 2026-07-11
- Rationale: `pmp-python`, under the `pydantic-message-protocol` org — consistent with the `rfc` repo's naming decision.
- Status: DECIDED

## [DECIDED] CI scope
- Date: 2026-07-11
- Rationale: CI will eventually be build+test only on push/PR; no PyPI publishing workflow for now — no code, tests, or release process exist yet.
- Status: DECIDED

## [OPEN] Minimum supported Python version
- Date: 2026-07-11
- Rationale: 3.10+ was informally suggested but not confirmed.
- Status: OPEN

## [DECIDED] Pushed to GitHub
- Date: 2026-07-11
- Rationale: Superseded the earlier local-only stance — clarified that "keep local" meant the file-copy step from the design chat, not a ban on pushing. Repo created as private (matching `rfc`) via `gh repo create pydantic-message-protocol/pmp-python --private`, all commits pushed, `main` tracking `origin/main`.
- Status: DECIDED
