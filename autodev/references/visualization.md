# Visualization

Read when forming the affected system view, at a meaningful execution checkpoint, or preparing handoff. A visual should help a developer answer a question about the change; choose the smallest view that does so.

## Keep the change in context

Start with the affected slice of the real system: callers, changed components, data or external boundaries, and preserved consumers. Link to the surrounding architecture rather than drawing the entire repository. For a stateful or cross-service change, show the important business path and the failure or recovery path, not only component boxes.

Use stable names across the current state, target, and actual state. Mark what is unchanged, proposed, implemented, and still missing in labels or sublabels. Show changed edges and side effects where they matter. A diagram with a new node ID is not evidence of a new capability; a correctly implemented plan can have the same topology as the target.

Use the bundled diagram JSON and renderer for the contract's development views. Additional sequence, state, or impact views may use the project's existing tools, including SVG or Archify when available. No external drawing tool is required to use autodev. Each additional view must answer a concrete review question.

## Three moments, one continuing picture

| Moment | Question | Visible artifact |
|---|---|---|
| Clarify | What changes, what stays intact, and where could we misunderstand? | As-is and target views at comparable detail, scope, baseline, and consequential assumptions |
| Loop | What actually exists now, what is failing or unverified, and what happens next? | Updated partial architecture or flow plus a checkpoint snapshot with check evidence |
| Handoff | What was delivered and what can the evidence establish? | As-built versus target, observed results, review notes, gaps, and reproduction commands |

Prepare the whole Clarify pass before its human review. Do not turn visual updates into repeated approval gates. Update at a coherent implementation checkpoint, a meaningful failed approach, a newly discovered risk, or a change of direction; reuse the view while the underlying state is unchanged.

## Show actual partial state

For development, update the agreed as-built path from the current code at checkpoints, before the whole feature is complete. Mark unfinished paths rather than drawing the blueprint as if it already existed. Include the diagram in the checkpoint commit when it changes. The coverage gate may remain incomplete; that is expected.

For a bug fix, show the affected path and the reproduction/regression outcomes when that helps explain a consequential failure. Use the native test output for case IDs and outcomes; the judge's command-level result is not a parsed per-case test report.

For optimization, show all measured attempts and the retained best. An invalid run has no invented score. Label the target and measurement conditions; a good-looking trajectory does not establish correctness or noise immunity.

After a judged checkpoint, run:

```bash
python3 <skill>/scripts/autodev_verify.py --home <contract dir> report --progress
```

This writes `progress.html` with recorded state, recent attempts, the scenario's current view, and review notes. Open it or provide its absolute path and open command. Reuse the path as an updated snapshot; the browser needs refresh after regeneration. Progress generation does not approve delivery or overwrite the handoff packet.

## Add the judgment the logs cannot provide

Keep `<contract dir>/review.md` short and current, using normal Markdown rather than a new result schema. Cover:

- the user-visible goal and behavior that must stay intact;
- the actual change so far, with the relevant source or diagram references;
- what the observed checks establish, with command/log references;
- what is still inferred, untested, failing, or blocked, and why;
- the next action or decision needed.

The report displays these notes as **AI review**, separately from recorded execution facts. Use explicit wording: “unit checks passed; database concurrency remains unverified,” not “idempotency verified.” Do not invent measurements or state transitions to make the snapshot look complete.

## Legibility before decoration

Show the visual at the size the human will actually read it. Split an unreadable system-wide view into a context view and a focused path. Give edges, status, and important failure branches readable labels. Use color with text, retain clear grouping, and keep the target and current views comparable. A rendered file that was never shown is not useful observability.
