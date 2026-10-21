# Product evaluation plan

Status: proposed protocol, not executed results. Source checks: 2026-10-21.

The product question is whether an **optional skill** helps developers deliver complex production changes with less misunderstanding, safer verification, and easier takeover at an acceptable total cost. Preserve **Clarify → Loop → Handoff**, use the project's tools, and improve the skill from observed work. Publication is a possible downstream use of the evidence, not the product specification.

The intended setting has meaningful ambiguity, several interacting modules or repositories, compatibility or rollout constraints, and a human who needs to inspect decisions and evidence. Quick, clear fixes should normally bypass the skill. It is neither a universal bug detector nor a replacement development/test framework.

## What evidence would mean

| Evidence | Supports | Does not establish |
|---|---|---|
| Skill probes and script tests | Recorded contracts, frozen inputs, scope checks, attempt logging, and verify/report/approve behavior work in tested cases | Useful developer interaction or production correctness |
| Production-style task trials | Feasibility and failure modes on selected realistic changes | Industrial adoption or general productivity improvement |
| Independent task tests | A submitted change satisfies the tested behavior under recorded conditions | Complete requirements, safe rollout, maintainability, or human understanding |
| Actual maintainer use | Usability, acceptance, follow-up costs, and operational fit in those projects | Universal industrial maturity |

Existing optimization histories illustrate recorded runs. They are not comparative evidence of industrial validation. A passing agreed check or complete diagram is bounded evidence; reviewers must still assess whether requirements and code match. Do not claim improvements before collecting comparative results.

## Stage 1 — production-style changes and a developer pilot

Start here, before spending on a large automatic benchmark. Proposed feasibility sample: **six complex changes across three maintained codebases**, including at least one coordinated two-repository change, plus **three clear small fixes** as negative controls. These counts are a planning proposal, not a powered sample or results.

Recruit **four to six developers**, including maintainers unfamiliar with autodev, for observed use and takeover. If only project authors participate, report that limitation and call this an internal pilot. Do not count scripted agents or the skill's own test suite as users.

Choose tasks from a recorded candidate list before observing treatment outcomes. Eligibility depends on the initial request, repository context, risk, and expected coordination needs—not whether autodev succeeds. Include failures and tasks where the skill is declined. Historical tasks must hide later fixes and discussions; prospective tasks give stronger evidence of current maintainer use.

| Task family | Production concern to preserve | Independent acceptance evidence |
|---|---|---|
| Feature across API, worker, and UI | Authorization, backward compatibility, partial failure | Integration scenarios, client behavior, maintainer review |
| Defect across cache and persistence | Invalidation, concurrency, existing consumers | Reproduction plus unrelated regressions and failure paths |
| Performance change across call path | Correctness, load distribution, memory and tail latency | Repeated comparable workload, correctness suite, resource measurements |
| Coordinated producer/consumer repositories | Version skew, deployment order, rollback | Old/new compatibility matrix and integration environment |

Use existing projects and commands. Do not build a toy application to make contract checks look successful. Where a multi-repository change requires several contracts or manual coordination, record the friction and unsupported boundaries instead of implying atomic support.

For each task, observe the whole workflow:

1. **Clarify:** inspect current behavior; record baseline checks including existing failures; expose unresolved decisions, non-goals, affected components, rollout risks, and proposed acceptance evidence. Have the developer review the complete pass and log revisions and time.
2. **Loop:** implement within the approved contract; record accepted, rejected, failed, and timed-out attempts. Inspect whether evolving snapshots help the developer locate current work, uncertainty, evidence, and the next decision. An attractive snapshot is not proof that code implements its claims.
3. **Handoff:** rerun relevant checks on the retained state, inspect evidence limits, and have another developer explain the change, reproduce a result, identify a limitation, and make a small follow-up. Record corrections before acceptance and whether takeover needs the original conversation.

Pre-existing failures require explicit attribution. Preserve the baseline logs, distinguish unchanged failures from introduced regressions, and agree a meaningful check or justified waiver before Loop. Never silently weaken a guard or remove failing tasks from the sample. Record setup failure separately from a product defect.

Compare autodev with the same agent's normal workflow using the same model, repository starting point, available tools, task information, and resource envelope. Normal work includes inspection, clarification when needed, test creation, testing, debugging, and retries. A one-shot baseline would answer the wrong question.

Also include a credible **plan/spec-first workflow** with clarification, implementation planning, ordinary tests/retries, and a handoff summary. [GitHub Spec Kit](https://github.com/github/spec-kit) structures specification, planning, tasks, implementation, and convergence; [OpenSpec's documented workflow](https://github.com/Fission-AI/OpenSpec/blob/main/docs-lab/start/quickstart.md) makes a proposal/spec/design/task package reviewable before implementation. Pin whichever comparator is used, document adaptations, and do not assume specification-first work is novel to autodev.

Assign conditions across comparable tasks and counterbalance developer/task order; do not ask the same developer to solve the same task repeatedly after seeing its solution. In a tiny pilot, prioritize observed friction and transparent case comparisons over causal productivity claims.

Record primary outcomes: independent acceptance, introduced regressions, requirement corrections after Loop begins, total developer time, and takeover completion/errors. Secondary observations: scope violations, inaccurate diagrams, unsupported success claims, unnecessary questions, interruption recovery, and willingness to use the skill again for a similar task.

Report **all-in cost**: Clarify investigation, human responses/review, diagram/snapshot preparation and reading, implementation, retries, final verification, handoff, and subsequent rework. Keep agent tokens/API cost, compute, elapsed time, active developer minutes, and waiting time separate. An approved target becoming easier is a requirement change, not a free improvement.

For the small controls, evaluate the decision to bypass and measure overhead if a willing participant elects to invoke the skill. Extra overhead is expected; do not require every trivial edit to run the full process to manufacture coverage.

Stage-1 output: per-task records, developer observations, unresolved product limitations, and a prioritized revision list. Advance after the workflow is usable enough to compare reliably; stalled or costly cases are product findings. Industrial maturity requires repeated real maintainer use and follow-up, beyond production-style trials.

## Stage 2 — automatic correctness as a bounded measurement

[SWE-bench Verified](https://www.swebench.com/SWE-bench/guides/datasets/) contains 500 expert-verified solvable issues. Its [evaluation harness](https://www.swebench.com/SWE-bench/guides/evaluation/) applies submitted patches and runs repository tests in a container. This is useful for independent correctness checks, reproducibility, and regression analysis; it does not exercise a real developer's approval, visualization use, rollout judgment, or takeover.

Use a small disjoint setup pilot, then preregister the main sample size, selection seed/strata, exclusions, repetitions, budgets, metrics, and stopping rule using pilot feasibility and variability. Prefer the full eligible set where affordable. If studying complex tasks, define complexity using pre-run metadata/context and report results for the prespecified strata; never choose the favorable subset after outcomes arrive.

Run the same normal-testing/retry and plan/spec-first baselines from Stage 1. Freeze model/version, reasoning settings, agent scaffold, tools, information access, container/source revisions, and per-condition budgets. Charge autodev's Clarify and artifact work against its budget. Report both fixed-budget outcomes and measured cost rather than giving the skill extra uncounted preparation.

Keep evaluation independent: an evaluator controls gold patches, hidden tests, expected requirements/plans, and final scoring outside the solving workspace. Clarify may author ordinary task tests from the public request and repository, but **must not see gold tests, solution patches, hidden acceptance requirements, or evaluator feedback during retries**. Deny solution/history retrieval and audit available information for leakage. Existing public benchmark exposure remains a contamination limitation.

If the benchmark has no real user, label any approval oracle or scripted responder explicitly. Give all conditions the same legitimate information and response policy. Do not let an oracle convert hidden requirements into hints; synthetic approval does not validate human alignment.

Keep the skill's approved tests distinct from evaluator tests. Report at least:

- External resolved/unresolved status and introduced-regression status.
- Agreed-check status versus external status, including false confidence: internal pass/external failure.
- Completion, timeout, empty patch, invalid patch, harness/setup failure, and unavailable evaluation.
- Full cost distributions, paired task-level differences where appropriate, and uncertainty intervals; preserve all run outcomes.

Use the prespecified primary denominator of assigned eligible tasks, with unresolved/timeouts retained. Report evaluator failures separately and any sensitivity analysis under the registered exclusion policy. A rerun needs a unique identity and a documented reason; retain the first run and distinguish infrastructure repair from an additional solution attempt.

[SWE-RPG's August 2026 preprint](https://arxiv.org/abs/2608.09072) describes 163 tasks from 31 Python/Java repositories, with requirement and planning references for retrospective trajectory diagnosis. The [preview repository](https://github.com/Xin-Zhou-smu/SWE-RPG-Bench) publishes data and evaluation assets. Assess the pinned release's executability and reference quality before adoption. Use its references only after submission to diagnose missed requirements/plans; it is not evidence that autodev discovers every implicit requirement or that its users understand the result.

After the main comparison, use a small, prespecified diagnostic subset for two targeted ablations: (a) preserve approved contracts/checks but omit evolving visual snapshots, to examine visibility cost/value; (b) preserve clarification/artifacts but omit mechanical contract enforcement, to examine scope/input-drift failures. Clearly label research variants, keep ordinary tests/retries available, and avoid a large factorial study. Findings guide product choices; do not weaken production checks merely to improve benchmark scores.

## Stage 3 — optional human review study and publication

If Stage 1 suggests useful handoff/understanding effects, design a separate reviewer study. Give reviewers comparable patches with either the normal handoff or autodev's packet, conceal condition branding where feasible, counterbalance order, and avoid reusing the same patch with the same reviewer. Measure accurate understanding, missed risks, reproduction success, review time, and a follow-up edit; preference alone is insufficient.

Pilot the instruments first, then preregister recruitment, sample justification, task assignment, scoring rubric, analysis, and exclusions. Use independent raters and report agreement and disagreements. Obtain participant consent and applicable ethics review before collection; protect private code and participant data. This stage does not replace actual maintainer adoption or post-delivery defect tracking.

EASE 2027 is an optional fit if the evidence supports an empirical contribution about when this workflow helps, its costs, and its limits. The [official Research Papers call](https://conf.researchr.org/track/ease-2027/ease-2027-papers) includes AI for software engineering, human factors, process improvement, benchmarking, case studies, human experiments, and negative results. It lists abstract **15 January 2027 AoE**, paper **22 January 2027 AoE**, and notification **12 March 2027 AoE**; recheck before scheduling a submission.

Frame a paper around measured questions: which eligible changes benefit, whether correctness or rework differs from strong baselines, and whether humans understand and take over more effectively after accounting for full cost. Compare related workflows fairly; the three stage names and a CLI are not sufficient novelty. Scope conclusions to the sampled projects/models/developers. If evidence is weak or deadlines are too close, continue product work and report the limitations rather than shape the skill around a venue.

## Task sheet example — illustrative, not a completed trial

| Field | Example to fill before assignment |
|---|---|
| Identity | `pilot-04`; immutable API and worker repository revisions; owner and reviewer roles |
| User request | Add cancellable exports while existing clients continue polling completed jobs |
| Eligibility | API/worker/storage interactions; ambiguous cancellation race; mixed-version deployment |
| Constraints | No schema deletion; preserve old response fields; no deployment during trial |
| Visible acceptance | Agreed cancel/completion behavior, authorization, retry semantics, rollback notes |
| Baseline | Exact integration/unit commands and raw logs; one unrelated existing flaky test recorded |
| Scope/risk | Approved API/worker paths; frozen migrations; race and version-skew risks |
| Independent evidence | Evaluator-held race/compatibility cases prepared before agent work; no solution disclosed |
| Handoff exercise | Reviewer reproduces one case and adds a cancellation audit event from the packet |
| Assignment | Preregistered condition, agent settings, resource limits, participant order |

## Run record example — schema only, no invented measurements

```yaml
run_id: pilot-04-autodev-r1
task_sheet: <immutable sheet hash and assignment record>
condition: <autodev | normal-agent | plan-first | named ablation>
versions: <skill, comparator, agent, exact model, settings, source revisions>
environment: <OS/container digest, dependencies, hardware, network/tool access>
budgets: <all-in elapsed/token/compute limits and human-response policy>
baseline: <commands, raw outputs, known failures, environment limitations>
clarify: <contract/artifact hashes, unresolved decisions, review revisions, approval>
loop: <attempt log, commits, failures/rejections, snapshots, interruptions>
handoff: <retained commit, fresh verify record, report hash, approval or refusal>
independent_result: <sealed evaluation id, outcome, logs, regression findings>
human_outcome: <participant role, takeover scoring, review corrections, consent id>
cost: <phase times, human active/wait time, tokens, API/compute, follow-up rework>
exceptions: <timeouts, leakage/exposure concerns, exclusions, reruns and reasons>
claim_limits: <untested behavior, missing environments, follow-up still pending>
```

Store protocols, task manifests, condition prompts, version pins, analysis decisions, and permitted raw artifacts with the results. Publish task-level failures and missing data alongside aggregates, with privacy-preserving redactions documented. This document proposes evaluation work; it provides no benchmark runner, model API integration, completed experiment, or performance claim.
