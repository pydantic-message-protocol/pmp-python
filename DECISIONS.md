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

## [DECIDED] Minimum supported Python version
- Date: 2026-07-12
- Rationale: 3.10+, resolved by implementation rather than left informal — the codebase uses PEP 604 union syntax (`X | Y`) and builtin generics throughout, which pydantic must evaluate at runtime; that requires 3.10. Already reflected in `pyproject.toml`'s `requires-python`.
- Status: DECIDED

## [DECIDED] Core module implementation
- Date: 2026-07-12
- Rationale: `envelope.py`, `naming.py`, `spool.py`, `producer.py`, `consumer.py`, `exceptions.py` implemented per RFC 0 (previously stubs). Sequence allocation via `fcntl.flock` on `.sequence`, atomic+durable publish (fsync file, atomic rename, fsync directory), consumer claims by numeric sequence order (not lexical), filename/envelope sequence agreement enforced on claim (`SequenceMismatchError`), crash recovery deliberately manual (no lease/timeout, per RFC 0 §4.7). 31 tests added, all passing, run via an ephemeral `uv run --no-project --with-editable . --with pytest` invocation — no local `.venv` created, keeping the global-venv rule intact.
- Status: DECIDED

## [DECIDED] Pushed to GitHub
- Date: 2026-07-11
- Rationale: Superseded the earlier local-only stance — clarified that "keep local" meant the file-copy step from the design chat, not a ban on pushing. Repo created as private (matching `rfc`) via `gh repo create pydantic-message-protocol/pmp-python --private`, all commits pushed, `main` tracking `origin/main`.
- Status: DECIDED

## [DECIDED] CI workflow added and verified locally
- Date: 2026-07-13
- Rationale: `.github/workflows/ci.yml` added — build (via `uv build`, exercising the hatchling backend) + test (`uv run --no-project --with-editable . --with pytest pytest`) on push/PR to `main`, matrix over Python 3.10 (the declared minimum) and 3.13. Verified by installing `act` (nektos/act, via Homebrew) and running the actual workflow YAML in Docker locally rather than just replicating the steps in shell — both matrix jobs passed (build succeeded, 31/31 tests passed on each Python version). Required `--container-daemon-socket -` since the host uses Colima (non-default Docker socket path) and this workflow has no docker-in-docker steps to justify bind-mounting it. Per explicit instruction, **not yet pushed** — developing locally for now.
- Status: DECIDED

## [DECIDED] CI workflow pushed and verified on GitHub
- Date: 2026-09-18
- Rationale: The three commits adding CI (`ci: add build+test GitHub Actions workflow` and the two related docs commits) had been sitting local-only since 2026-07-13 — `origin/main` had no workflow file and no run history. Pushed to `main`; the resulting Actions run (35341594850) passed on both matrix legs (3.10, 3.13) in ~9s each. CI is now live on GitHub, not just locally verified.
- Status: DECIDED

## [DECIDED] Spool root resolution and channel ownership
- Date: 2026-09-18
- Rationale: RFC 0 defines the `spool/` subdirectory layout (`tmp/`, `pending/`, `processing/`, `completed/`, `failed/`) but deliberately leaves the spool root's filesystem location, and how a producer/consumer pair pick which spool to use, out of scope — same as `message_type` and payload schemas, which RFC 0 §3 already requires producer and consumer to agree on independently. A per-repo path (e.g. a gitignored `.pmp_spool/` inside one repo's checkout) was rejected: it ties the shared spool to wherever that one checkout happens to be cloned, which doesn't hold up for the cross-repo producer/consumer use case this package is meant for (see the `example-project-messages` idea in the `rfc` repo's `IDEAS.md` and the `"producer": "repository-a"` framing in RFC 0's own envelope example). Decided instead: the spool root resolves from a `PMP_SPOOL_ROOT` env var when set, else defaults to `~/.local/state/pmp/<channel>/` — decoupled from any repo's working directory so producer and consumer processes can find each other regardless of where their repos live. `channel` is not derived from envelope fields: not from `message_type` (would fragment one logical flow, e.g. `build.*`, across several spools) and not from `producer` (would break RFC 0 §4.3's support for multiple producers sharing one queue). Instead `channel` is an opaque name the **receiver** creates and owns — since the default root already lives under the receiver's own `$HOME`, the name only needs to be unique within that one receiver's namespace, not globally — and the receiver communicates it to each producer out-of-band, the same handshake RFC 0 already requires for `message_type`/schema agreement. This is an implementation-level default of `pmp-python`, not a protocol requirement — RFC 0 is unchanged.
- Status: DECIDED
