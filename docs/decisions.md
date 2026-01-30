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

## D-20260130-1154
Date: 2026-01-30 11:54
Inputs: CR-20260130-1153
PRD: Run Script; CLI Enhancements; Extraction & Recreation Fidelity

Decision:
- Treat the current codebase behavior as the source of truth and update RALPH docs to match it.
- Keep `20260129-run-sh` focused on the `run.sh` wrapper + README documentation, but update it to include the current `run.sh` behavior (output directory fallback and new flags passthrough).
- Document post-run.sh changes (CLI flags and extraction/recreation fidelity improvements) as a new feature spec `20260130-cli-and-fidelity`.

Rationale:
- The repo has evolved beyond the original `run.sh` scope, and splitting the spec keeps traceability readable while still reflecting current behavior.

Alternatives considered:
- Expand `20260129-run-sh` spec to cover all subsequent changes (rejected: would mix unrelated concerns and obscure the audit trail).

Acceptance / test:
- `docs/PRD.md` includes requirements for the new documented behaviors with `Sources: CR-20260130-1153; D-20260130-1154`.
- `docs/specs/20260129-run-sh/spec.md` reflects current `run.sh` behavior.
- New spec `docs/specs/20260130-cli-and-fidelity/spec.md` matches the implemented CLI flags and extraction/recreation behavior.

## D-20260130-1211
Date: 2026-01-30 12:11
Inputs: CR-20260130-1210
PRD: Extraction & Recreation Fidelity; Run Script; CLI Enhancements

Decision:
- Add `slide_index` (0-based) to each slide entry in extracted JSON so users can verify slide coverage and tooling can map slides deterministically.
- When recreating from JSON without a template PPTX, render extracted `diagram` text blocks as simple textboxes so the recreated deck is not “empty-looking”.
- Keep skipping `diagram` recreation when a template PPTX is used, to avoid duplicating SmartArt (the template already contains it).
- Repair the RALPH decision log by removing an accidentally pasted patch/template snippet that was not a real decision entry.

Rationale:
- `slide_index` makes it obvious whether slides are missing and makes debugging deterministic.
- python-pptx cannot recreate editable SmartArt; textbox placeholders are the most reliable fallback when no template exists.
- In template mode, preserving the original SmartArt is preferable to duplicating it.

Alternatives considered:
- Attempt to reconstruct SmartArt from JSON (rejected: out of scope and not reliably supported by python-pptx).

Acceptance / test:
- `./run.sh <pptx> <outdir> --extract` produces JSON with `slides[].slide_index` values `0..N-1`.
- `./run.sh dummy.pptx <outdir> --recreate --info-path <json>` produces a PPTX containing extracted diagram text in slide text.
- `./run.sh <pptx> <outdir> --recreate --info-path <json>` preserves SmartArt content via the template PPTX without duplicating it.

## D-20260130-1258
Date: 2026-01-30 12:58
Inputs: CR-20260130-1257
PRD: Web UI

Decision:
- Implement the web UI as a lightweight local Streamlit app (no hosted service).
- Keep the existing CLI as the source of truth and have the UI call the same Python modules (Extractor/Recreator) rather than shelling out.
- Provide “selection” controls by letting users load an extracted JSON, filter slides and shape types, validate it inline, then recreate from the filtered JSON.
- Keep Streamlit as an optional dependency via `requirements-ui.txt` so CLI installs remain fast.

Rationale:
- Streamlit provides a simple, cross-platform local UI with file pickers and fast iteration.
- Filtering/validation at the JSON layer avoids invasive changes to extraction logic and keeps diffs reviewable.

Alternatives considered:
- Build a Flask/React app (rejected: larger surface area and more dependencies).
- Add dozens of CLI flags for per-field selection (rejected: not user-friendly for this use case).

Acceptance / test:
- `./run.sh ui` launches the local UI.
- UI can run extract and recreate, and can validate a JSON file and show specific schema errors.
- UI can filter a JSON (slides/types) and recreate a PPTX from the filtered JSON.
