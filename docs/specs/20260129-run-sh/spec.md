# Feature Spec: 20260129-run-sh

Status: Active
Created: 2026-01-29 12:11
Inputs: CR-20260129-1210
Decisions: D-20260129-1211

## Summary
- Add a `run.sh` wrapper that sets up a local virtual environment, installs dependencies, and runs the CLI entrypoint; document it in the README for reliable first-run setup.

## User Stories & Acceptance

### US1: Run the tool without manual venv steps (Priority: P1)
Narrative:
- As a user, I want a single script to set up dependencies and run the CLI, so that I don’t have to remember venv/pip steps.

Acceptance scenarios:
1. Given a fresh checkout, When I run `./run.sh -h`, Then I see the CLI usage help. (Verifies: FR-001)
2. Given a PPTX path, When I run `./run.sh <pptx> <outdir> --extract`, Then `<outdir>/<basename>_info.json` is created. (Verifies: FR-001)
3. Given the repo README, When I look for setup/run instructions, Then `./run.sh` usage is documented with examples. (Verifies: FR-002)
4. Given an unwritable output directory (e.g. a volume root), When I run `./run.sh <pptx> <outdir> --extract`, Then it falls back to a writable directory and prints which directory is used. (Verifies: FR-003)

## Requirements

Functional requirements:
- FR-001: Add `run.sh` that creates/uses `.venv`, installs dependencies from `requirements.txt`, and runs `python main.py` forwarding args. (Sources: CR-20260129-1210; D-20260129-1211)
- FR-002: Update `README.md` to include `./run.sh` instructions and examples. (Sources: CR-20260129-1210)
- FR-003: When `output_dir` is not writable, `run.sh` should fall back to a writable output directory and avoid confusing Python stack traces. (Sources: CR-20260130-1153; D-20260130-1154)

## Edge cases
- Missing `python3.11`: script falls back to `python3`. (Verifies: FR-001)
- Missing `.venv`: script creates it automatically. (Verifies: FR-001)
