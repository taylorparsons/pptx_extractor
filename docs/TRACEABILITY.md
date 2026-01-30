# Traceability (How to follow the audit trail)

Start here:
1) Find the relevant raw request in `docs/requests.md` (CR-...).
2) Read linked interpretations/tradeoffs in `docs/decisions.md` (D-...).
3) Open the relevant feature spec:
   - Run script + README: `docs/specs/20260129-run-sh/spec.md`
   - CLI + extraction/recreation fidelity: `docs/specs/20260130-cli-and-fidelity/spec.md`
   - Requirements use IDs (FR-...) and include `Sources: CR-...; D-...`.
   - Acceptance scenarios include `Verifies: FR-...`.
4) Open the matching feature task list:
   - `docs/specs/20260129-run-sh/tasks.md`
   - `docs/specs/20260130-cli-and-fidelity/tasks.md`
   - Tasks include `Implements: FR-...`.
5) Review execution notes in `docs/progress.txt` for commands, outcomes, and completion.
