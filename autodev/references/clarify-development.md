# Clarify: feature development

Read for a feature request, alongside the shared [Clarify](clarify.md) rules. The target of this scenario is a **blueprint**: the agreed architecture and flow diagrams the implementation must realize. One pass runs steps 1–3 in order; the human reviews the whole pass in step 4. Do not implement the feature during Clarify.

## 1. Draw the as-is picture

Inspect the relevant code and draw the current state in Mermaid:

- the overall architecture around the change: modules, responsibilities, dependencies;
- the existing business flows the feature touches.

These as-is diagrams are the baseline. They must be drawn from the actual code, not from memory or documentation. Save them to a file outside the editable surface, for example `BLUEPRINT-ASIS.md` at the repository root.

## 2. Draft the blueprint

Draw the agreed end state in Mermaid, same granularity as the as-is picture:

- the target architecture: modules, responsibilities, and boundaries after the change, including modules to be added or removed;
- the target business flows: sequence, outputs, and side effects after the change.

Give every element a stable ID — node names in Mermaid are IDs already; reuse the same IDs across as-is and blueprint where an element survives unchanged. Collect all blueprint element IDs on one comment line so the judge can check coverage mechanically:

```mermaid
%% autodev-elements: order-api order-service inventory-client checkout-flow
```

The blueprint is the target: Loop ends only when the delivered state realizes every element. Keep it at the level of architecture and flows, not pseudocode — the point is to fix *what* is built and *how the parts connect*, leaving implementation detail to Loop.

If the feature legitimately changes existing behavior, say so explicitly and mark the affected test files as editable in step 3; otherwise existing tests stay frozen and must remain green.

## 3. Propose the scope

| Boundary | Propose for the human's confirmation |
|---|---|
| Editable files | Explicit paths the agent may change to realize the blueprint |
| Existing tests | Frozen by default; list the test paths the blueprint is allowed to change, if any |
| Regression check | An existing test/lint command that must stay green, if the project has one |
| As-built path | Where Loop writes the delivered-state diagrams, inside the editable surface |

Write the proposal as a contract with the judge script, from the user's checkout, into a directory outside the repository (pass `--home` as an absolute path; every later command uses the same value):

```bash
python3 <skill>/scripts/autodev_verify.py --home ../<repo>.autodev init \
  --scenario development --editable src/ docs/ \
  --blueprint BLUEPRINT.md --asis BLUEPRINT-ASIS.md \
  --asbuilt docs/asbuilt.md --check-cmd "pytest -q"
```

`init` copies the as-is and blueprint files into the contract directory, freezes their hashes, parses the element list, runs the regression check once as the recorded baseline, and prints the contract for the human to review in step 4. Both files must live outside the editable surface and be committed — either on the starting branch or inside the worktree's baseline commit — so the Loop worktree carries them.

## 4. Human review of the whole pass

Show the as-is diagrams, the blueprint, and the proposed scope together. The human decides:

- **Revise:** apply the feedback and repeat from step 1. A changed blueprint needs a new contract, so rerun `init --renew`.
- **Approve:** record the approved blueprint, as-is baseline, and scope, then enter Loop.

The human confirms the blueprint is the right design, not merely that it was drawn. If the blueprint reveals disagreement about the architecture or a flow, resolve it here — not during Loop.

**Exit:** the human has approved one complete pass — the blueprint, its as-is baseline, and the permitted scope. Continue to [Loop: development](loop.md#feature-development).
