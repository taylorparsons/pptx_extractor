# Agent Guidelines

## PEAS

Agent:
- Maintain and extend this repository’s PPTX extraction/recreation utilities with small, reviewable changes.

Performance measure (P):
- CLI behavior matches the user request (extract and/or recreate) with clear errors for invalid inputs.
- For any code change: run a repo-relevant sanity check (`python3 -m compileall main.py extractors recreator utils`) and, when possible, a sample run of `python3 main.py … --extract/--recreate`.
- Keep scope tight; avoid unrelated refactors and avoid introducing large binary artifacts or secrets.

Environment (E):
- Python CLI project using `python-pptx` to read/write `.pptx` files.
- Output artifacts are JSON “_info” files (can be very large due to base64-encoded images) and recreated `.pptx` files.
- Network access may be restricted; prefer using existing sample PPTX/JSON files in-repo for validation.

Actuators (A):
- Edit/add files in this repo as needed for the requested change (prefer minimal diffs).
- Run safe local commands like `python3 -m compileall main.py extractors recreator utils` and `python3 main.py <pptx_path> <output_dir> --extract/--recreate`.
- Create output files only under explicit output directories (avoid polluting the repo root).

Sensors (S):
- Code search (`rg`), `git diff`, and runtime errors/stack traces from CLI runs.
- Outputs on sample data: generated `*_info.json` and `recreated_*.pptx` exist and open in PowerPoint without corruption.
