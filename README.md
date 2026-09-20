<p align="center">
  <strong>English</strong> · <a href="./README_ZH.md">简体中文</a>
</p>

# autodev

**Stop letting your agent grade its own homework.**

An agent can add a feature and call it done, or change some code and call it faster. autodev makes both claims checkable: agree on a benchmark first, stay inside an agreed list of files, and accept a change only when a script says it is better. Everything else gets rolled back.

![How autodev works: contract, baseline, loop, review](docs/assets/autodev-overview.png)

| Phase | What happens | What you do |
|---|---|---|
| **Contract** | Write down the goal, the criterion, the budget, and which files may change | Confirm once |
| **Baseline** | Write the tests or build the benchmark, run it once, and hash the files that must not change | Nothing |
| **Loop** | Edit the allowed files → run the benchmark → the script decides → commit or roll back → log the attempt | Wait for the budget you approved |
| **Review** | Re-run all tests on the final code, then refactor, then report what the loop gained | Nothing |

![License](https://img.shields.io/badge/license-MIT-22c55e?style=flat-square)
![Agent Skill](https://img.shields.io/badge/skill-autodev-7C3AED?style=flat-square)
![Version](https://img.shields.io/badge/version-3.0.3-0891b2?style=flat-square)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)

```bash
npx skills add Momoyeyu/autodev -g
```

Works with Claude Code, Cursor, Codex CLI, OpenCode, and anything else that reads `SKILL.md`.

## Why this exists

Today's coding models are strong and fast. One pass is enough to add a feature or rewrite a hot path, and what comes back is a paragraph describing what happened. That paragraph is the only evidence you get. You cannot read the diff as fast as the model writes it, so "done" quietly turns into something you accept rather than something you check.

autodev's answer is to stop reading the report and ask for the artifact instead:

- **A feature is shown by a case.** Not "CSV export implemented", but a test that failed before and passes now, together with the input and the exact rows it produces.
- **An optimization is shown by a number.** Not "the home page is faster", but a before-and-after on a frozen benchmark, with the target and the noise floor written next to it.

In both cases the model's prose stops being the deliverable. What you get instead is something you can run yourself, run again tomorrow, and compare across attempts.

## The problem

Ask an agent to make something faster and it will happily make a change, declare victory, and move on. Three things go wrong, and none of them are about laziness:

1. **It grades its own homework.** With no measurement taken before the edit, "faster" is an opinion. A test written after the code passes immediately and proves nothing. A benchmark number with no baseline proves just as little.
2. **It optimizes the measurement instead of the code.** Cache the benchmark input, shrink the eval set, loosen the tolerance, run it five times and report the best one. In a diff, every one of these looks like progress.
3. **It forgets.** Thirty attempts later, in a fresh context window, it retries the idea that already failed twice.

autodev prevents all three. It combines two ideas that already work:

- **Test-driven development (TDD)** as the correctness gate: write a failing test first, then just enough code to pass it. A test that never failed proves nothing, so an untested feature does not count as done.
- The **accept/reject loop** from [autoresearch](https://github.com/karpathy/autoresearch): freeze the benchmark, fix the budget, and let a script decide what survives.

## Two modes, same rules

You never have to pick one. The shape of the request decides:

| The request | How success is judged | Mode | Time budget |
|---|---|---|---|
| add / implement / fix X | a test goes from failing to passing | **development** (TDD) | **none** — it's done or it isn't |
| make X faster / smaller / cheaper | a number beats the baseline | **optimization** | **required** |
| both — "add X, and it has to be fast" | both | optimization | required |

**TDD isn't optional in either mode.** Optimization adds a benchmark on top of TDD; it doesn't replace it. Tests still pass, new code still gets tests first. A change that improves the number but breaks a test is rolled back like any other failure — which is the entire answer to "the agent made the benchmark faster by breaking the feature."

Development work gets no time budget. A feature isn't improved by being abandoned halfway. If it's too big to finish in one go, autodev splits it into several.

## Quick start

### 1. Install

```bash
npx skills add Momoyeyu/autodev -g
```

Global, non-interactive, Claude Code only:

```bash
npx -y skills add Momoyeyu/autodev --skill autodev -a claude-code -g --copy -y
```

Try it without installing:

```bash
npx skills use Momoyeyu/autodev@autodev --agent claude-code
```

### 2. Ask for the work

**A feature** — no budget; the work is either done or it isn't:

```text
implement CSV export for the filtered transaction list
```

```text
RED       test "exports filtered rows as csv"    → FAIL: exportCsv is not defined
GREEN     minimal writer, 12 lines               → PASS (suite green)
REFACTOR  extract CsvWriter                      → still PASS
```

**An optimization** — note the contract you get to approve first:

```text
make the home page load faster
```

```text
contract for approval:
  metric   p95_ms ↓   target 200ms   5 runs, median (measured noise ±2.1%)
  tests    npm test — assertion count may not drop
  frozen   bench/**  tests/**  package-lock.json  vite.config.ts
  surface  src/home/**
  budget   15 attempts / ~8 min
```

```text
attempt  commit   tests  metric  delta   verdict  note
1        a1b2c3d  pass   184.2   —       baseline initial state
2        b2c3d4e  pass   171.5   -12.7   accept   preload hero image
3        c3d4e5f  fail   —       —       fail     inline critical css broke the suite
4        d4e5f6g  pass   183.9   +12.4   reject   memoized fetch, no real gain
```

### 3. Watch what it refuses to do

The interesting output is the rejections. A run that never rejects anything is either trivial or cheating, and the rules below are what tell the two apart.

## What it asks before spending your time

autodev never requires you to know how it works. It asks two questions at most, always with concrete options and a custom answer, and only about what your request doesn't already determine:

```text
优化首页刷新速度

Q1  Which metric?
    A. p95 navigation latency      (recommended — server + network + paint)
    B. time to interactive         (paints fast, responds late)
    C. gzipped bundle size         (payload is the suspect)
    D. custom

Q2  Budget? You're buying wall clock, so the price is shown:
    A. quick try    ~5 attempts  / ~2 min
    B. standard     ~15 attempts / ~8 min     (recommended)
    C. until it converges — usually 30-60 attempts / ~30 min
    D. custom
```

Then the whole contract is shown once for confirmation. That is the only point in the loop where a human is needed.

Feature work asks nothing, because there's nothing to ask — the failing test *is* the acceptance criterion, and writing it is the first piece of work.

`--dry-run` prints the contract and stops.

## Why the loop can't be gamed

Seven rules, enforced every attempt. They're the difference between optimizing the code and optimizing the measurement:

1. **The protected files are hashed** before and after each attempt. A changed hash fails the attempt outright.
2. **The tests only get stronger.** The assertion count may rise or hold, never fall.
3. **No new dependencies, network calls, or hardware branches.**
4. **No shrinking the workload to fake a gain** — fewer eval samples, cached results, memoized inputs, warm caches the contract didn't ask for.
5. **No best-of-N.** Fixed repeat count, median statistic. Re-running until a lucky sample lands is cheating.
6. **No `.skip`, no `xfail`, no loosened tolerances** to turn a test green.
7. **At the same number, the simpler change wins.** A metric isn't a complete objective, and without a tie-break the loop just accumulates complexity.

## What's inside

Progressive disclosure, because a skill that injects 9k tokens into every request gets uninstalled. Only the core loads up front; each reference loads when its trigger fires.

| File | Loads when | Size | Contents |
|---|---|---|---|
| [`autodev/SKILL.md`](autodev/SKILL.md) | the skill is triggered | **~2.7k tok** | The three rules, the two modes, the four phases, the verdict, rolling back, the experiment log, stop conditions, anti-gaming |
| [`references/gate.md`](autodev/references/gate.md) | writing production code or touching tests | ~2.5k tok | The full TDD gate: the Iron Law, both verification steps, the rationalization table, red flags, the checklist |
| [`references/contracts.md`](autodev/references/contracts.md) | drafting a contract | ~1.5k tok | Choosing a metric, frozen files per scenario, worked contracts, how to build a benchmark |
| [`references/testing-anti-patterns.md`](autodev/references/testing-anti-patterns.md) | adding mocks or test utilities | ~2.1k tok | Five anti-patterns, each with a gate function and the fix |

A feature request loads the core plus the gate — about **5.2k tokens**. An optimization loads the core plus contracts and the gate — about **6.7k**. Nothing loads all four files at once unless the work genuinely spans everything.

## What it works on

The same two layers, recombined. No new machinery for any of these:

| Scenario | Tests | Metric | Frozen |
|---|---|---|---|
| Feature | new test fails → passes, suite green | — | existing suite |
| Bug fix | reproduction test fails → passes | — | the reproduction test |
| Refactor | behavior suite green | complexity ↓ / coverage ↑ | behavior spec |
| Performance | suite green | p95 ↓ | bench script, dataset, hardware |
| Build time | suite green | build seconds ↓ | core count, concurrency, cache state |
| Bundle size | suite green | bytes ↓ | build config, target browsers |
| Cost | suite green | $/request ↓ | traffic shape, price table |
| Model quality | no crash, no NaN | val loss ↓ | harness, validation set, **time budget** |

That last row shows why the protected list has to be worked out per scenario rather than copied. There, the fixed wall clock *is* the objective — "the best model trainable in five minutes." For a web page it would be meaningless, and what needs protecting is the machine, the dataset, and the cache state instead.

## Works with

Any agent that supports the [Agent Skills specification](https://agentskills.io). Global install paths for the common ones:

| Agent | `--agent` | Global path |
|---|---|---|
| Claude Code | `claude-code` | `~/.claude/skills/` |
| Cursor | `cursor` | `~/.cursor/skills/` |
| Codex CLI | `codex` | `~/.codex/skills/` |
| OpenCode | `opencode` | `~/.config/opencode/skills/` |
| GitHub Copilot | `github-copilot` | `~/.copilot/skills/` |
| Gemini CLI | `gemini-cli` | `~/.gemini/skills/` |
| Windsurf | `windsurf` | `~/.codeium/windsurf/skills/` |
| Amp / Replit / universal | `universal` | `~/.config/agents/skills/` |

Manual install, if you'd rather not use the CLI:

```bash
git clone --depth 1 https://github.com/Momoyeyu/autodev.git /tmp/_autodev
cp -r /tmp/_autodev/autodev ~/.claude/skills/
rm -rf /tmp/_autodev
```

## Scope

autodev covers test-first implementation, bug fixes, refactors, and measurable optimization of a quantity you can name. It deliberately ships no scripts and no dependencies: the contract is generated at Phase 0 and the verdict reuses whatever your project already runs — `npm test`, `pytest`, your own benchmark script.

Framework-specific templates are out of scope on purpose. The moment the skill knows about Jest, it stops applying to Rust.

## Evaluating the skill

The versioned evaluation corpus in [`evals/cases.json`](evals/cases.json) covers development, bug fixes, optimization contracts, noisy metrics, scope failures, and anti-gaming behavior. Run each case in a clean agent session, record its observable assertions, then score the report deterministically:

```bash
python3 evals/run.py run --case development-feature
python3 evals/run.py clean
python3 -m unittest discover -s tests -v
```

Runs copy the current skill and fixtures into the ignored `.autodev-evals/` directory, preserving transcripts and diffs for review. See [`evals/README.md`](evals/README.md) for scoring and the repeatable workflow.

- [Skill core](autodev/SKILL.md) · [Correctness gate](autodev/references/gate.md) · [Contracts](autodev/references/contracts.md) · [Anti-patterns](autodev/references/testing-anti-patterns.md) · [Changelog](CHANGELOG.md) · [Contributing](CONTRIBUTING.md)

## License

[MIT](LICENSE) — free to use, modify, and distribute.

## Contributing

Issues and PRs are welcome, especially real transcripts of the loop running — including the runs where the agent tried to game its own benchmark. Start with the [contribution guide](CONTRIBUTING.md).
