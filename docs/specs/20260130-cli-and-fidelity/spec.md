# Feature Spec: 20260130-cli-and-fidelity

Status: Active
Created: 2026-01-30 11:55
Inputs: CR-20260130-1153
Decisions: D-20260130-1154

## Summary
- Align docs with current CLI options and extraction/recreation behavior so users can reliably extract, recreate from specific JSON, and preserve template styling where possible.

## User Stories & Acceptance

### US1: Recreate from a specific JSON file (Priority: P1)
Narrative:
- As a user, I want to recreate a PPTX from an explicit JSON path, so I can move/rename JSON without being forced into a naming convention.

Acceptance scenarios:
1. Given an extracted JSON, When I run `./run.sh dummy.pptx <outdir> --recreate --info-path <path/to/info.json>`, Then a recreated PPTX is produced. (Verifies: FR-001)
2. Given a typo or directory passed to `--info-path`, When I run the command, Then I get a clear error without a Python stack trace. (Verifies: FR-001)

### US2: Name the recreated PPTX output (Priority: P1)
Narrative:
- As a user, I want to control the output file name/path, so I can version recreated decks without renaming afterward.

Acceptance scenarios:
1. Given an extracted JSON, When I run `./run.sh ... --recreate --output-pptx my_name.pptx`, Then the output file is written with that name. (Verifies: FR-002)

### US3: Preserve layout/style as much as possible (Priority: P1)
Narrative:
- As a user, I want extract+recreate to preserve slide size, geometry, and key text/table styling, so the recreated deck resembles the original.

Acceptance scenarios:
1. Given a PPTX, When I run `--extract`, Then JSON includes slide size and shape geometry/z-order fields. (Verifies: FR-003)
2. Given a PPTX containing SmartArt/diagram content, When I run `--extract`, Then JSON includes diagram text blocks for those slides. (Verifies: FR-004)
3. Given the original PPTX exists at `<pptx_path>`, When I run `--recreate`, Then it is used as a template to preserve masters/backgrounds. (Verifies: FR-005)
4. Given an extracted JSON containing `diagram` shapes, When I run `--recreate` without a template PPTX, Then the recreated PPTX contains the diagram texts as visible textboxes. (Verifies: FR-004)

## Requirements

Functional requirements:
- FR-001: Add `--info-path` to use a specific extracted JSON for `--recreate`, with clear errors for invalid/missing paths. (Sources: CR-20260130-1153; D-20260130-1154)
- FR-002: Add `--output-pptx` to control the recreated PPTX output file name/path. (Sources: CR-20260130-1153; D-20260130-1154)
- FR-003: Version the extracted JSON and include slide size, `slide_index`, geometry, and z-order, plus richer paragraph/text-frame/table sizing metadata. (Sources: CR-20260130-1153, CR-20260130-1210; D-20260130-1154, D-20260130-1211)
- FR-004: Extract SmartArt/diagram text blocks into JSON and render them as visible text when recreating without a template PPTX. (Sources: CR-20260130-1153, CR-20260130-1210; D-20260130-1154, D-20260130-1211)
- FR-005: When possible, use the original PPTX as a template on recreate to preserve masters/backgrounds and reduce “empty-looking” outputs. (Sources: CR-20260130-1153; D-20260130-1154)

## Non-goals
- Recreating SmartArt as editable SmartArt from JSON alone (python-pptx limitation). (Verifies: FR-004, FR-005)
