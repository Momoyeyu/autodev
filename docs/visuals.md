# README visual assets

The README uses a custom SVG suite: a brand header, one overview, and three scenario diagrams in English and Chinese. The layout retains **Clarify → Loop → Handoff**, with lightweight semantics:

- **Clarify:** resolve consequential questions and sketch a short plan. The billing retry example shows only its core flow.
- **Loop:** implement and run focused checks. Update the view when a meaningful change or finding helps the user follow the work.
- **Handoff:** summarize the changes, checks, and remaining limits, with links to evidence. HTML is optional and can be produced by another skill when the user wants it.

The brand and overview state that Autodev is explicitly invoked. The diagrams do not require worktrees, Git, approval gates, frozen test suites, or a particular plan format. These are README illustrations; a plan in actual use can be a small Mermaid diagram or another suitable visual.

## Regenerate

From the repository root:

```sh
python3 docs/visuals/generate.py
```

This standard-library script writes `docs/assets/autodev-{brand,overview,development,bugfix,optimization}.svg` and their `.zh.svg` variants. It parses every generated SVG as XML before saving. Each image includes an accessible title and description, a fixed viewBox, system font fallbacks, and no network resources. Edit the generator instead of generated SVGs. English and Chinese assets share geometry.

The scenario pictures are explanatory schematics, not experimental results. Bugfix shows reproduction before the fix and regression checks afterward. Optimization shows a fixed workload and baseline samples, retained and rejected attempts, and a final rerun. Its bars do not represent measured values. The separate MoE and cann2026 case charts are measured artifacts and are not regenerated here.

## Visual review

Open the [English suite](visuals/review-en.html) and [Chinese suite](visuals/review-zh.html) through a local preview server. Both pages display the current SVGs at an 830px image width.

For this revision, all ten SVGs parsed as XML and passed browser text-bounding checks with no text outside the viewBox. Both suites were rendered in an isolated headless Chrome browser at 830px image width and visually inspected for labels, arrows, clipping, hierarchy, and bilingual parity. XML parsing and text bounds complement visual inspection; they do not establish that the depicted implementation or checks actually occurred.

## Earlier Archify comparison

The [Archify candidate](visuals/archify-comparison/overview.json), its [interactive HTML](visuals/archify-comparison/overview.html), and [canonical SVG export](visuals/archify-comparison/overview.export.svg) document an earlier, heavier workflow. They were generated from a local Archify fork at commit `b160ddea` on 2026-10-21, reporting `3.2.1-dev.1`. The [comparison page](visuals/archify-comparison/comparison.html) and files under `visuals/review/` are historical records, not validation of the current suite or current Archify releases.

The current README keeps direct SVG because it embeds clearly at reading width. That choice does not prescribe the tool used to render a user's plan or optional handoff.
