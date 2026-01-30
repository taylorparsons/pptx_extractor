# Feature Spec: 20260130-web-ui

Status: Done
Created: 2026-01-30 12:58
Inputs: CR-20260130-1257
Decisions: D-20260130-1258

## Summary
Add a lightweight local web UI so non-technical users can run extract/recreate, validate edited JSON, and optionally filter what gets recreated (slides/shape types) without touching the CLI.

## User Stories & Acceptance

### US1: Run extract/recreate from a browser (Priority: P1)
Narrative:
- As a user, I want a simple local UI to run extract/recreate, so I don’t have to remember CLI flags.

Acceptance scenarios:
1. Given a valid PPTX path and output directory, When I click “Extract”, Then the UI produces a `*_info.json` and shows the output path. (Verifies: FR-001)
2. Given a valid JSON and output directory, When I click “Recreate”, Then the UI produces a `recreated_*.pptx` and shows the output path. (Verifies: FR-002)

### US2: Inline JSON validation (Priority: P1)
Narrative:
- As a user, I want immediate feedback when JSON is invalid, so I know what to fix before recreating.

Acceptance scenarios:
1. Given a JSON file path, When I validate it in the UI, Then I see a list of schema errors with JSON paths (e.g., `$.slides[3].shapes[2].type`). (Verifies: FR-003)

### US3: Select what gets recreated (Priority: P1)
Narrative:
- As a user, I want to select subsets (slides, shape types) to recreate, so I can update only what I intend to change.

Acceptance scenarios:
1. Given an extracted JSON, When I select slide indices and shape types and save a filtered JSON, Then recreating from that filtered JSON produces a PPTX containing only the selected content. (Verifies: FR-004)

## Requirements

Functional requirements:
- FR-001: Provide a local web UI that can run extraction using the same Python modules as the CLI. (Sources: CR-20260130-1257; D-20260130-1258)
- FR-002: Provide a local web UI that can run recreation from a chosen JSON and show the output PPTX path. (Sources: CR-20260130-1257; D-20260130-1258)
- FR-003: Provide inline JSON validation using the repo’s JSON validator with actionable error messages. (Sources: CR-20260130-1257; D-20260130-1258)
- FR-004: Provide filtering controls to select slides and shape types to include before recreation (implemented by producing a filtered JSON). (Sources: CR-20260130-1257; D-20260130-1258)

Non-functional requirements:
- NFR-001: Keep the UI dependency optional (do not require Streamlit for CLI-only usage). (Sources: CR-20260130-1257; D-20260130-1258)
