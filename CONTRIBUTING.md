# Contributing

Improve alignment between agents and humans, not just the amount of code an agent can produce. Changes should make delivery more verifiable, measurable, and visible, reduce rework, and help the human understand and take over the project.

## Keep the protocol faithful

The skill supports two scenarios through **Define → Anchor → Ratchet → Prove**:

- **Feature development:** confirm architecture/workflow impact; obtain human approval of test definitions; inspect and reconcile existing tests; verify execution; record baseline; develop until all agreed tests pass; compare baseline and final results.
- **Performance optimization:** obtain human approval of one numeric benchmark test; record baseline; confirm target, editable files, and wall-clock budget; optimize until the target is met or time expires; compare baseline and final score.

Review these distinctions explicitly:

- Human approval is about test meaning, not a fixed number of questions.
- Test construction follows approval of the definition; baseline precedes implementation.
- Outdated feature tests may be changed or removed to match approved behavior before baseline. During iteration, tests must not be weakened to manufacture success.
- Executable feature tests may fail for unimplemented behavior; a broken runner is not a useful baseline.
- A composite benchmark is one fixed weighted score, not several independent optimization targets.
- Optimization limits are confirmed after the baseline; no automatic convergence or attempt-count stop replaces the wall-clock limit.
- Final claims use comparable test versions and real evidence, including honest timeout or incomplete outcomes.

## Organize by stage

`autodev/SKILL.md` holds purpose, principles, scenario selection, and stage routing. Operational detail belongs in `references/define.md`, `anchor.md`, `ratchet.md`, and `prove.md`.

Keep a stage's instructions together. Read the current stage's shared instructions and applicable scenario; do not prefetch the entire reference directory. `references/test-design.md` is optional support for acceptance cases and composite benchmark design, not another primary workflow.

Every reference must be reachable from the skill entry point with a clear reading trigger. Links must resolve within the installed `autodev/` directory. Keep wording imperative and framework-independent; reuse the target project's tools rather than requiring a particular test runner.

Measure Markdown cost when editing, but do not optimize bytes by removing human approval, baseline comparability, or handover evidence:

```bash
for f in autodev/SKILL.md autodev/references/*.md; do
  printf '%-50s ' "$f"
  wc -l -w -c < "$f"
done
```

## Keep both READMEs synchronized

`README.md` and `README_ZH.md` describe the same protocol. Update their stage tables, scenario ordering, file inventories, and delivery expectations together.

The current workflow diagrams are inline Mermaid in the READMEs. Keep their node identities, transitions, human-review loops, and stage boundaries equivalent across languages. In particular, performance baseline must precede confirmation of loop limits.

Static assets under `docs/` belong to earlier versions. They are not the current workflow definition or evidence for this version; do not reuse their historical fixture results as new measurements.

## Verify changes

The legacy unit/evaluation suite has been retired. Do not cite its results as verification of the new protocol or link to removed runners and fixtures.

Before committing:

- Walk through both scenario sequences against the skill and both README diagrams.
- Check local Markdown links, anchors, code fences, and frontmatter.
- Verify all references have stage-appropriate triggers and remain inside the installed skill.
- Check that retained-test maintenance, the single-score rule, baseline ordering, deadlines, and takeover evidence remain explicit.
- Review the full diff for unintended changes and run `git diff --check`.
- Confirm `git ls-files -- tests evals` is empty; ignored historical run artifacts are not a current test suite.
- If no live agent evaluation was run, say so. Document validation is not proof of model adherence.

Record real behavior evidence when evaluating the skill in a target project: approved definitions, commands, before/after outputs, relevant decisions, and actual agent/model identity. Never invent a passing run to fill a report.

## Commits and license

Follow [AGENTS.md](AGENTS.md): one commit does one thing, with an imperative lowercase `<type>: <what changed>` subject. Do not rewrite shared history or push without approval.

Contributions are licensed under [MIT](LICENSE).
