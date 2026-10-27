# Production workflow implementation plan

> Historical record for the earlier contract-based version. The current lightweight workflow is defined in `autodev/SKILL.md`; the tools and required gates described here have since been removed.

> **For agentic workers:** Use superpowers:executing-plans for the core changes; independent visual and evaluation work uses focused agents. Preserve the existing uncommitted quick fixes. The initial implementation scope did not request commits or pushes; the user subsequently approved GitHub delivery.

**Goal:** Make autodev useful for consequential changes in production codebases, with explicit opt-in, visible execution, and honest verification.

**Architecture:** Keep Clarify → Loop → Handoff, detailed scenario clarification, and the standard-library judge. AI assesses meaning and adequacy; the tools record execution facts. Add a lightweight progress snapshot to the existing report path, not a runtime service or universal test-result protocol.

**Tech Stack:** Markdown skill, Python standard library, self-contained HTML/SVG, bilingual README assets.

**Spec:** The user's request in this conversation, including product usefulness before optional EASE 2027 evaluation.

## Global constraints

- Simple local changes normally bypass autodev; task risk and uncertainty matter more than repository size.
- Preserve complete clarification and reuse user decisions; one review of the whole pass, not approval per substep.
- Show actual partial state at meaningful checkpoints, with evidence limits and next actions.
- Diagrams are AI-authored models; IDs and graph differences cannot prove implementation correctness.
- Reuse native tests and benchmark commands; semantic failures remain AI judgment.
- Existing quick-fix changes remain intact; no benchmark-specific code in the installed skill.
- Real case measurements remain unchanged. Demonstration artifacts must be labeled synthetic.

## Review focus

- A quick typo should not trigger a full contract/worktree workflow.
- Partial development without as-built completion must remain visible and explicitly incomplete.
- Rendering progress must not overwrite or invalidate the handoff packet or its approval.
- A valid as-built may have the same topology as the blueprint; superficial redrawing must not be required.
- Green narrow checks must not become claims of integration or production readiness.

## Task 1: Skill and verification guidance

- [x] Record current-skill behavior probes before edits.
- [x] Rewrite the compact entry around selection, shared change understanding, execution visibility, and reviewable evidence.
- [x] Preserve scenario Clarify details; add focused visualization and verification references.
- [x] Retest the scenarios against the revised skill and distinguish probes from real validation.

## Task 2: Visible execution and truthful diagram checks

Files: autodev/scripts/autodev_verify.py, tests/test_verify.py, supporting references.

- [x] Add failing tests for report --progress, preserved handoff approval/artifacts, unchanged blueprint IDs, and matched as-built topology.
- [x] Add progress snapshots from recorded state; capture review notes as AI judgment separately from tool evidence.
- [x] Remove mechanical novelty/copy gates; keep element/dependency checks and explicit semantic review.
- [x] Run targeted tests, then the full suite and inspect generated HTML.

## Task 3: README, visuals, and product evaluation

Files: README.md, README_ZH.md, docs/assets/, docs/visuals.md, docs/evaluation.md, CONTRIBUTING.md.

- [x] Redesign bilingual brand, overview, and workflow visuals; compare current Archify and direct SVG on actual output.
- [x] Rewrite READMEs around the production use case and user-visible artifacts, with real cases intact.
- [x] Document real-task evaluation first, benchmark corroboration second, optional EASE research third.
- [x] Verify SVGs, render at README width, check links/bilingual parity and regenerate previews.
- [x] Complete fresh review and address important findings before delivery.

## Verification ledger

- Baseline and revised skill probes completed; qualitative instruction-following evidence only.
- Progress and diagram checks observed RED before implementation; targeted suites passed.
- Updated Archify compared with direct SVG at README width; SVG selected and both languages inspected.
- Independent review finding on manual verification reproduced and fixed with regression coverage.
- Final full suite: 155 tests passed in 75.680 seconds; whitespace, local links, generator reproducibility, SVG XML, desktop and true 430px viewport checks passed. See docs/validation/2026-10-21-product-iteration.md.
- Implementation was reviewed before delivery. The user subsequently approved committing and pushing this iteration to GitHub.
