# Clarify: feature development

Read for a feature request, alongside the shared [Clarify](clarify.md) rules. The target of this scenario is a **blueprint**: the agreed architecture and flow diagrams the implementation must realize. One pass runs steps 1–3 in order; the human reviews the whole pass in step 4. Do not implement the feature during Clarify.

## 1. Draw the as-is picture

Inspect the relevant code and draw the current state as diagram JSON:

- the overall architecture around the change: modules, responsibilities, dependencies;
- the existing business flows the feature touches.

These as-is diagrams are the baseline. They must be drawn from the actual code, not from memory or documentation. Save them to a file outside the editable surface, for example `BLUEPRINT-ASIS.json` at the repository root.

## 2. Draft the blueprint

Draw the agreed end state in the same diagram format, at the same granularity as the as-is picture:

- the target architecture: modules, responsibilities, and boundaries after the change, including modules to be added or removed;
- the target business flows: sequence, outputs, and side effects after the change.

A diagram file is one JSON object: `nodes` carry the elements, `edges` draw the connections, `regions` group nodes visually, `depends` declares build order, and `meta.title` names the diagram:

```json
{
  "meta": {"title": "Checkout blueprint"},
  "nodes": [
    {"id": "order-api", "label": "Order API", "row": 0, "col": 1},
    {"id": "order-service", "label": "Order Service", "row": 1, "col": 0},
    {"id": "inventory-client", "label": "Inventory Client", "kind": "external", "row": 1, "col": 2},
    {"id": "checkout-flow", "label": "Checkout Flow", "row": 2, "col": 1}
  ],
  "edges": [
    {"from": "checkout-flow", "to": "order-api", "label": "calls"},
    {"from": "order-api", "to": "order-service"},
    {"from": "order-api", "to": "inventory-client", "dashed": true}
  ],
  "regions": [{"label": "SERVICE", "wraps": ["order-api", "order-service"]}],
  "depends": {"order-api": ["order-service", "inventory-client"], "checkout-flow": ["order-api"]}
}
```

Node `id`s are the element IDs — stable, `[A-Za-z0-9_-]+`, reused across as-is and blueprint where an element survives unchanged, and new for added or changed elements. At least one blueprint ID must be absent from the as-is diagram, otherwise redrawing the starting state would already pass the coverage check. `label`/`sublabel` are display text; `kind` (`service`/`store`/`external`/`decision`/`flow`) only picks a marker color. Optional `row`/`col` place a node on the layout grid; leave them out and the renderer layers nodes left-to-right by connection order. Preview any draft with `python3 <skill>/scripts/autodev_render.py FILE.json` — it writes `FILE.html` next to the source.

Declare build dependencies in `depends`, read as "the key needs the listed elements". A dependency means one element cannot be realized before another exists: a service before the API that calls it, a data model before the flow that writes it. It is build order, not every arrow in the diagram. `init` refuses unknown IDs and cycles, and prints the resulting **build order** as batches, for example `[1] order-service inventory-client → [2] order-api → [3] checkout-flow`. Elements without declared dependencies can be built in any order.

The blueprint is the target: Loop ends only when the delivered state realizes every element. Keep it at the level of architecture and flows, not pseudocode — the point is to fix *what* is built and *how the parts connect*, leaving implementation detail to Loop.

If the feature legitimately changes existing behavior, say so explicitly and mark the affected test files as editable in step 3; otherwise existing tests stay frozen and must remain green.

## 3. Propose the scope

| Boundary | Propose for the human's confirmation |
|---|---|
| Editable files | Explicit paths the agent may change to realize the blueprint |
| Existing tests | Frozen by default; list the test paths the blueprint is allowed to change, if any |
| Regression check | An existing test/lint command that must stay green, if the project has one |
| As-built path | Where Loop writes the delivered-state diagram JSON, inside the editable surface |
| Generated paths | Run-artifact paths the check command or build writes (build output, caches); declared with `--generated` so they are never mistaken for deliverables |

Write the proposal as a contract with the judge script, from the user's checkout, into a subdirectory of `.autodev/` (pass `--home` as an absolute path; every later command uses the same value). `init` writes a self-ignoring `.gitignore` there, so every contract file — the contract, the log, raw output, rendered previews — stays inside the project yet untracked. `--home` must be a strict subdirectory like `.autodev/run`, never `.autodev/` itself (its `.gitignore` would hide the constitution), and `start` refuses a contract directory inside the loop worktree:

```bash
python3 <skill>/scripts/autodev_verify.py --home "$PWD/.autodev/run" init \
  --scenario development --editable src/ docs/ \
  --blueprint BLUEPRINT.json --asis BLUEPRINT-ASIS.json \
  --asbuilt docs/asbuilt.json --check-cmd "pytest -q"
```

`init` copies the as-is and blueprint files into the contract directory, freezes their hashes, parses the element list and its dependencies into `depends` and `batches`, records which elements are new relative to the as-is diagrams (`elements_new`, refusing an empty list), renders `asis.html` and `blueprint.html` previews for the review pass, runs the regression check once as the recorded baseline, and prints the contract for the human to review in step 4. Both files must live outside the editable surface and be committed — either on the starting branch or inside the worktree's baseline commit — so the Loop worktree carries them. The baseline runs in the user's real checkout on purpose, so it measures the actual starting state; `init` records whatever the run left behind as `baseline.side_effects` and refuses outright if it touched a frozen path. Declare anything the check command writes with `--generated`: untracked files there never block an attempt and rollback sweeps them, but committing one is invalid — they are run artifacts, not deliverables.

## 4. Human review of the whole pass

Show the rendered `asis.html` and `blueprint.html` previews, the build order, and the proposed scope together. The human decides:

- **Revise:** apply the feedback and repeat from step 1. A changed blueprint needs a new contract, so rerun `init --renew`.
- **Approve:** record the approved blueprint, as-is baseline, and scope, then enter Loop.

The human confirms the blueprint is the right design, not merely that it was drawn. If the blueprint reveals disagreement about the architecture or a flow, resolve it here — not during Loop.

**Exit:** the human has approved one complete pass — the blueprint, its as-is baseline, and the permitted scope. Continue to [Loop: development](loop.md#feature-development).
