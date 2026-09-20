# Contributing

Improve alignment between agents and humans. Changes should reduce misunderstanding and rework, improve quality, stability, and efficiency, and help the human understand and take over the project.

## Keep the protocol faithful

Use **Clarify → Loop → Handoff** as the only top-level working stages. User input triggers the workflow.

- **Development Clarify:** confirm architecture/workflow impact, then query, update/remove, add, and trial-run tests with the human until the executable set is approved; record the formal baseline afterward.
- **Optimization Clarify:** agree on one runnable numeric benchmark or fixed weighted score, record baseline, then confirm target, editable files, and wall-clock budget.
- **Loop:** develop until all agreed tests pass, or optimize until target/time limit. Preserve the measuring agreement and record actual outcomes.
- **Handoff:** one baseline/final comparison table for development; one chart of the measured optimization process for optimization.

Do not move test preparation outside the human review cycle, equate executable tests with already-passing tests, replace the optimization chart with a table, or add convergence/attempt-count exits. Changes to test meaning or permitted scope return to Clarify.

## Progressive disclosure

`autodev/SKILL.md` is the compact entry point. `references/clarify.md` contains shared alignment rules and routes to exactly one of `clarify-development.md` or `clarify-optimization.md`. `loop.md` and `handoff.md` load when those stages are reached.

Keep shared rules with the selected scenario; do not preload the whole directory. Every reference needs a clear trigger and a reachable link inside the installed skill. Preserve framework independence and reuse the target project's tools.

Measure the Markdown cost without removing approval, comparable measurement, or the required handoff artifact:

```bash
for f in autodev/SKILL.md autodev/references/*.md; do
  printf '%-52s ' "$f"
  wc -l -w -c < "$f"
done
```

## README and core diagram

Keep English and Chinese README ordering, scenario sequences, reference inventories, and handoff requirements equivalent. Place the core flow image immediately below the title, before installation and explanatory sections.

The current core diagrams are generated with [Archify](https://github.com/tt-a1i/archify):

| Source | README image |
|---|---|
| `docs/diagrams/autodev.workflow.json` | `docs/assets/autodev-overview.png` |
| `docs/diagrams/autodev.workflow.zh.json` | `docs/assets/autodev-overview.zh.png` |

Both sources use workflow schema v2, `quality_profile: showcase`, the same node/edge IDs, three phases, and two scenario lanes. The baseline/test/limit ordering is protected by `semanticChecks`; do not weaken those checks to resolve a layout failure. Loop boxes summarize repeated work and explicitly state its stop condition; ordinary sequential edges need no redundant label.

Keep the PNGs opaque and dark regardless of the README viewer's color scheme. Use Archify's Classic preset and canonical PNG export, not a screenshot containing viewer controls or manually recolored output. These are workflow illustrations, not test-result charts; do not reintroduce the removed result screenshot.

### Regenerate with Archify

Use the installed skill root containing `SKILL.md` and `bin/archify.mjs`. The checked workflow was generated with Archify `2.17.0-dev.1`, checkout `72c750b`.

```bash
ARCHIFY_SKILL=/path/to/archify/archify
OUT=$(mktemp -d)
for locale in '' '.zh'; do
  source="docs/diagrams/autodev.workflow${locale}.json"
  output="$OUT/autodev-overview${locale}.html"
  node "$ARCHIFY_SKILL/bin/archify.mjs" validate workflow "$source" --quality showcase --json &&
  node "$ARCHIFY_SKILL/bin/archify.mjs" deliver workflow "$source" "$output" --quality showcase --json &&
  node "$ARCHIFY_SKILL/bin/archify.mjs" visual-check "$output" --json || break
done
```

Require all nine artifact checks, zero composition errors, and zero warnings. Never inspect stale HTML after a failed delivery. Browser evidence and perceptual review are separate from deterministic validation.

Open each successfully delivered HTML with `?theme=dark`, keep Classic selected, and use Export → PNG. Save the canonical downloads to the corresponding image paths above. Inspect both exported PNGs for legibility, correct sequence, unclipped labels, no viewer UI, and an opaque dark background. Keep validation and export receipts with the generation artifacts; source JSON and final images belong in Git.

Archify renders this repository's explanatory workflow. It is not a mandatory dependency for producing a target project's optimization-result chart.

## Verify changes

The legacy unit/evaluation suite remains retired. Do not cite its results as proof of this protocol.

Before committing:

- Walk through both scenario paths against the skill, READMEs, and diagram sources.
- Check local links, anchors, frontmatter, and code fences; verify the deleted reference names are no longer used.
- Check that runnable-test approval precedes formal baseline and optimization limits follow baseline.
- Verify the feature table and optimization process chart are mandatory everywhere, not optional presentation choices.
- Confirm bilingual diagram topology matches and both PNGs are dark canonical exports.
- Run Archify validation/browser checks and review the actual images; retain the evidence.
- Run `git diff --check` and confirm `git ls-files -- tests evals` is empty.
- Keep ignored historical run artifacts and unrelated user work untouched.
- State whether model behavior was evaluated; document and image checks do not prove agent adherence.

## Commits and license

Follow [AGENTS.md](AGENTS.md): one commit does one thing, with an imperative lowercase `<type>: <what changed>` subject. Do not rewrite shared history or push without approval.

Contributions are licensed under [MIT](LICENSE).
