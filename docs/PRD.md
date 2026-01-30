# PRD

## Run Script

- Provide `run.sh` that creates/uses a local `.venv`, installs `requirements.txt`, then runs the CLI (`main.py`) forwarding user arguments. (Sources: CR-20260129-1210; D-20260129-1211)
- Update `README.md` to document using `./run.sh` for setup and running extract/recreate commands. (Sources: CR-20260129-1210)

## CLI Enhancements

- Support recreating from a specific JSON path via `--info-path` (bypassing the `<output_dir>/<pptx_basename>_info.json` convention). (Sources: CR-20260130-1153; D-20260130-1154)
- Support specifying the recreate output filename/path via `--output-pptx`. (Sources: CR-20260130-1153; D-20260130-1154)

## Extraction & Recreation Fidelity

- Extract slide size, per-slide `slide_index` (0-based), shape geometry (left/top/width/height), z-order, and richer text/table formatting into JSON (versioned). (Sources: CR-20260130-1153, CR-20260130-1210; D-20260130-1154, D-20260130-1211)
- Extract SmartArt/diagram text blocks (so slides with SmartArt aren’t “empty” in JSON). (Sources: CR-20260130-1153, CR-20260130-1210; D-20260130-1154, D-20260130-1211)
- When recreating and a template PPTX exists at `pptx_path`, use it to preserve slide masters/backgrounds and to avoid duplicating existing pictures. (Sources: CR-20260130-1153; D-20260130-1154)
- When recreating without a template PPTX, render extracted `diagram` text blocks as simple textboxes so the deck isn’t “empty-looking”. (Sources: CR-20260130-1210; D-20260130-1211)
