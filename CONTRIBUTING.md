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

## README, brand and diagrams

Keep English and Chinese README ordering, scenario sequences, reference inventories, and handoff requirements equivalent. The README has no text title: the brand image replaces it, followed immediately by the overview, before installation and explanatory sections.

The brand and overview are hand-authored SVG rendered with headless Chrome; the scenario detail diagrams are generated with [Archify](https://github.com/tt-a1i/archify). All but the brand exist in English and Chinese:

| Source | README image | Role |
|---|---|---|
| `docs/diagrams/autodev.brand.svg` | `docs/assets/autodev-brand.png` | Title: mark on the left, AutoDev wordmark on the right, transparent background |
| `docs/diagrams/autodev.overview(.zh).svg` | `docs/assets/autodev-overview(.zh).png` | Hero: artistic three-step composition, without scenario detail |
| `docs/diagrams/autodev.development(.zh).json` | `docs/assets/autodev-development(.zh).png` | Feature flow inside the workflow section |
| `docs/diagrams/autodev.optimization(.zh).json` | `docs/assets/autodev-optimization(.zh).png` | Optimization flow inside the workflow section |

### Brand and overview

The mark is an original crossbar-less "A" with a cyan loop arrow inside; it is not derived from any company logo. Palette: `#3259B4`, `#3C8CFF`, `#00C8D2`, `#78E6DD`. The wordmark reads `AutoDev`, "Auto" in royal blue and "Dev" in a blue-to-cyan gradient, after a thin vertical divider. Keep the composition minimal.

The overview shows Clarify as scattered intent converging into one focused point, Loop as an orbit around code, and Handoff as the path opening into measured evidence, connected by a single left-to-right spine. Change labels in both language files together; keep geometry identical.

```bash
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
render() { "$CHROME" --headless=new --disable-gpu --hide-scrollbars "$@" 2>/dev/null; }
render --force-device-scale-factor=2 --default-background-color=00000000 --window-size=1600,400 --screenshot=docs/assets/autodev-brand.png "file://$PWD/docs/diagrams/autodev.brand.svg"
for locale in '' '.zh'; do
  render --window-size=1920,700 --screenshot="docs/assets/autodev-overview${locale}.png" "file://$PWD/docs/diagrams/autodev.overview${locale}.svg"
done
```

The overview is rendered at 1x (1920×700); the 2x version is over 1.9 MB because of the gradients and glows.

### Detail diagrams

The process maps use Archify's `architecture` schema v1 and grid layout, not its workflow-lane template. This provides explicit canvas bounds without unused columns or full-width empty stage lanes. `components` are process steps, `connections` are directed control flow, and the named regions group stages, not deployment infrastructure. Keep `quality_profile: showcase` and identical topology and geometry within each language pair.

Detail maps use a compact two-row path: Clarify reads left to right, then Loop and Handoff follow the arrows right to left. Three numbered stage regions remain distinct. Dashed return paths show review and implementation feedback; solid paths show progression and delivery. The optimization loop is post-tested (do-while): limits → optimize → measure and retain → stop check. A negative decision returns to optimization; target reached or time exhausted leads to the chart. Do not introduce a limits-to-stop-check shortcut.

This renderer does not support workflow `semanticChecks`. Check directed connections explicitly: test preparation → baseline → proposed impact/limits → one human review; the review's "No" edge returns to test preparation and its "Yes" edge enters Loop; each detail map has that Clarify cycle and an execution cycle; only the required table/chart is terminal. Do not treat successful geometry validation as a semantic check.

Keep the PNGs opaque and dark regardless of the README viewer's color scheme. Use Archify's Editorial preset and canonical PNG export, not a screenshot containing viewer controls or manually recolored output. These are workflow illustrations, not test-result charts; do not reintroduce the removed result screenshot.

### Regenerate with Archify

Use the installed skill root containing `SKILL.md` and `bin/archify.mjs`. The checked workflow was generated with Archify `2.17.0-dev.1`, checkout `72c750b`.

```bash
ARCHIFY_SKILL=/path/to/archify/archify
OUT=$(mktemp -d)
for name in development optimization; do
  for locale in '' '.zh'; do
    source="docs/diagrams/autodev.${name}${locale}.json"
    output="$OUT/autodev-${name}${locale}.html"
    node "$ARCHIFY_SKILL/bin/archify.mjs" validate architecture "$source" --quality showcase --json &&
    node "$ARCHIFY_SKILL/bin/archify.mjs" deliver architecture "$source" "$output" --quality showcase --json &&
    node "$ARCHIFY_SKILL/bin/archify.mjs" visual-check "$output" --json || break 2
  done
done
```

Require all nine artifact checks, zero composition errors, and zero warnings. Never inspect stale HTML after a failed delivery. Browser evidence and perceptual review are separate from deterministic validation.

Open each successfully delivered HTML with `?theme=dark`, keep Editorial selected, and use Export → PNG. Save the canonical downloads to the corresponding image paths above. Inspect all four exported PNGs at a 960px README reading width for legibility, balanced margins, clear local cycles, unclipped labels, no viewer UI, and an opaque dark background. Review one detail composition before producing its translated counterpart; a nine-check pass alone is not visual acceptance. Keep validation and export receipts with the generation artifacts; source JSON and final images belong in Git.

Archify renders this repository's explanatory workflow. It is not a mandatory dependency for producing a target project's optimization-result chart.

## Verify changes

The legacy unit/evaluation suite remains retired. Do not cite its results as proof of this protocol.

Before committing:

- Walk through both scenario paths against the skill, READMEs, and diagram sources.
- Check local links, anchors, frontmatter, and code fences; verify the deleted reference names are no longer used.
- Check that baseline precedes the scope proposal and that the single human review closes the whole Clarify pass in both scenarios.
- Verify the feature table and optimization process chart are mandatory everywhere, not optional presentation choices.
- Confirm bilingual diagram topology and geometry match; detail PNGs are dark canonical exports and the brand PNG keeps a transparent background.
- Run Archify validation/browser checks for the detail diagrams and review every actual image, including the brand and overview; retain the evidence.
- Run `git diff --check` and confirm `git ls-files -- tests evals` is empty.
- Keep ignored historical run artifacts and unrelated user work untouched.
- State whether model behavior was evaluated; document and image checks do not prove agent adherence.

## Commits and license

Follow [AGENTS.md](AGENTS.md): one commit does one thing, with an imperative lowercase `<type>: <what changed>` subject. Do not rewrite shared history or push without approval.

Contributions are licensed under [MIT](LICENSE).
