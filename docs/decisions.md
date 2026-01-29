# Decisions (append-only)

## D-20260129-1211
Date: 2026-01-29 12:11
Inputs: CR-20260129-1210
PRD: Run Script

Decision:
- Implement `run.sh` as a convenience wrapper that (1) creates/uses a local `.venv`, (2) installs `requirements.txt`, then (3) runs `python main.py` forwarding any CLI args.
- Prefer `python3.11 -m venv .venv` when `python3.11` exists; otherwise fall back to `python3 -m venv .venv`.

Rationale:
- The repo’s “app” is a CLI, so the safest “start” behavior is delegating to `main.py`.
- `python3` on this machine may be Homebrew-managed and blocked for global installs (PEP 668), so venv-local installs are the reliable default.

Alternatives considered:
- Hard-code `python3.11` only (rejected: not always installed).
- Install dependencies globally via `pip install` (rejected: can fail under PEP 668 / externally-managed environments).

Acceptance / test:
- `./run.sh -h` prints the CLI help.
- `./run.sh <pptx> <outdir> --extract` creates `<outdir>/<basename>_info.json`.
*** Add File: docs/TRACEABILITY.md
# Traceability (How to follow the audit trail)

Start here:
1) Find the relevant raw request in `docs/requests.md` (CR-...).
2) Read linked interpretations/tradeoffs in `docs/decisions.md` (D-...).
3) Open the feature spec at `docs/specs/20260129-run-sh/spec.md`.
   - Requirements use IDs (FR-...) and include `Sources: CR-...; D-...`.
   - Acceptance scenarios include `Verifies: FR-...`.
4) Open the feature task list at `docs/specs/20260129-run-sh/tasks.md`.
   - Tasks include `Implements: FR-...`.
5) Review execution notes in `docs/progress.txt` for commands, outcomes, and completion.
