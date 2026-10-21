# README visual assets

The README uses a custom SVG suite: a brand header, one product overview, and three scenario diagrams in English and Chinese. The three stages remain **Clarify → Loop → Handoff**. The overview leads with the concrete artifacts: an agreed system slice, a current partial system view and next action plus recorded checks, and as-built output plus verification evidence. Amber marks human judgment/review; teal marks measured evidence. The human reviews the whole Clarify pass once and reviews the delivery at Handoff.

## Regenerate

From the repository root:

```sh
python3 docs/visuals/generate.py
```

This standard-library script writes `docs/assets/autodev-{brand,overview,development,bugfix,optimization}.svg` and their `.zh.svg` variants. It parses every generated SVG as XML before saving. Each image includes an accessible title and description, a fixed viewBox, system font fallbacks, and no network resources. Edit the generator instead of editing generated paths manually. The case charts for MoE and cann2026 are independent measured artifacts and are untouched.

The scenario pictures are explanatory schematics. The bug-fix pass/fail pattern describes the required evidence shape; it is not a reported test run. The optimization picture has no invented scores or improvement curve.

## Direct SVG versus current Archify

The comparison uses the same product brief: Clarify agrees target/baseline/scope in one human review; Loop implements and checks while retaining evidence; Handoff packages the as-built result and verification for human review. It compares two authored compositions of that brief, not a benchmark of every renderer feature.

Archify was loaded read-only from the updated local fork at commit `b160ddea` (2026-10-21), reporting `3.2.1-dev.1`. The local upstream checkout was older (`25cf3708`, 2026-10-19). Neither checkout was modified.

- [Archify candidate](visuals/archify-comparison/overview.json) preserves the explicit work/artifact lanes, loop-back, and two human reviews.
- [Finalized interactive Archify HTML](visuals/archify-comparison/overview.html) provides exploration, theme switching, and exports.
- [Canonical light SVG export](visuals/archify-comparison/overview.export.svg) was downloaded through that HTML's export menu.
- [830px comparison page](visuals/archify-comparison/comparison.html) shows both SVGs at the same rendered width; [the inspected capture](visuals/review/comparison-830px.png) preserves that view.
- [Latest finalizer receipt](visuals/archify-comparison/review-2/overview.finalize-summary.json) and [browser/capture receipt](visuals/archify-comparison/review-2/overview.visual-check.json) bind the latest Archify artifact. Earlier receipts are retained and refer to the previous candidate, not the current artifact.

For this README, direct SVG is the better fit: its three artifact compositions keep the hierarchy clear at reading width, and keep the judgment/evidence distinction inside the image. At 830px wide its smallest text is approximately 10.4px and ordinary detail text is approximately 12px. This Archify composition exports a wider, denser graph; its smallest supporting text is approximately 5.4px at the same width. Its canonical diagram export also excludes the separate Judgment/Evidence cards shown in the interactive HTML. Those observations concern this candidate and this embedding width. The interactive Archify version is useful when the reader wants to explore the full flow.

## Verification and visual review

All ten final SVGs parsed as XML, expose title/description, and passed browser text-bounding checks with no text outside the viewBox. Both language suites were rendered in Chrome at 830px image width and visually inspected for clipping, labels, arrows, hierarchy, and bilingual parity. The [English](visuals/review/english-830px.png) and [Chinese](visuals/review/chinese-830px.png) review captures show the suite at that width. The final review includes the partial system view and next-action labels in the overview, and the checkpoint view update in both feature-development diagrams.

Archify passed showcase validation, deterministic delivery, strict artifact checking, and browser checking with zero diagnostics. Its final light/dark screenshots at 1440×900 and 2048×1320 were captured; both 1440×900 themes were visually inspected. Its exported SVG and the direct overview were also visually compared at 830px. Automated checks and this visual inspection are separate evidence.

To repeat Archify generation with an installed copy, set `ARCHIFY_SKILL` to its skill directory and run from the repository root:

```sh
node "$ARCHIFY_SKILL/bin/archify.mjs" finalize workflow \
  docs/visuals/archify-comparison/overview.json \
  docs/visuals/archify-comparison/overview.html \
  --quality showcase --out-dir docs/visuals/archify-comparison/review-next --json
```

Use a fresh evidence directory after changing the candidate. Open the resulting HTML and use **Export → SVG · Light** for the canonical comparison image.
