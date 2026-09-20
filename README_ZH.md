<p align="center">
  <a href="./README.md">English</a> · <strong>简体中文</strong>
</p>

# autodev

**autodev 是一个要求编程 Agent 用结果证明工作的 Skill：开发功能，要让一个失败的测试变绿；做优化，要在冻结的 benchmark 上真正超过 baseline。**

![License](https://img.shields.io/badge/license-MIT-22c55e?style=flat-square)
![Agent Skill](https://img.shields.io/badge/skill-autodev-7C3AED?style=flat-square)
![Version](https://img.shields.io/badge/version-3.0.3-0891b2?style=flat-square)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)

```bash
npx skills add Momoyeyu/autodev -g
```

支持 Claude Code、Cursor、Codex CLI、OpenCode，以及任何能够读取 `SKILL.md` 的 Agent。

## 为什么要做 autodev

编程 Agent 写代码的速度，已经超过了人逐行 review 的速度。现在真正困难的，不再是让代码被写出来，而是判断这次改动究竟值不值得留下。

如果没有一套测量规则，Agent 最重要的几句话都无法核实：

| Agent 说 | 缺少的证据 |
|---|---|
| “功能已经做完了。” | 一个实现前失败、实现后通过的测试 |
| “页面已经变快了。” | baseline、稳定的 benchmark，以及实测的噪声范围 |
| “这是最好的方案。” | 被拒绝的尝试记录，以及统一的比较规则 |

autodev 改变的是交付物。Agent 的解释仍然有参考价值，但它不再是证据；证据必须是你明天还能重新运行的东西：

- 开发功能，交付一个 **RED → GREEN** 的测试用例；
- 做性能优化，交付一组 **before → after** 的测量结果；
- 失败的方案会被**记录，并恢复到上一个已接受状态**，而不是悄悄堆进最终代码；
- 测试、benchmark、数据集等测量依据会被冻结，Agent 不能靠修改尺子来提高分数。

最终得到的是一个只向前移动的棘轮：只有脚本能够证明更好的代码，才会进入已接受状态。

## 看看它实际怎么工作

仓库为下面的场景提供了不依赖第三方库的可重复 fixture。图中的结果都来自这些 fixture 的实际运行，不是为了说明概念而虚构的数字。

![可重复的功能开发与性能优化结果](docs/assets/autodev-evidence.png)

### 1. 开发一个新功能

```text
为 Invoice 增加 total_with_tax(rate) 方法。
```

autodev 不会先写实现。它先写一个只描述目标行为的测试，亲自运行并确认失败原因正确；之后才补上最小实现，再运行目标测试和完整测试套件。

| 检查点 | fixture 实测结果 |
|---|---|
| RED | `test_total_with_tax_applies_rate ... FAIL` |
| GREEN | Invoice 的两个测试全部通过 |
| 交付证据 | 新测试明确展示了输入、税率和精确结果 |

这就是**开发模式**。它不设置尝试预算：功能要么已经实现并受到测试保护，要么就还没有完成。

### 2. 优化一个可测量的目标

```text
把 API 的 p95 延迟降到 200 ms 以下；固定运行 7 次并取中位数。
```

动代码之前，autodev 会先写出 contract：

```yaml
goal:      "API p95 延迟低于 200 ms"
criterion: "测试通过；benchmark 跑 7 次；比较中位数"
frozen:    ["tests/**", "bench/**"]
surface:   ["src/api.py"]
budget:    "最多 12 次尝试或 20 分钟"
reset:     "从已接受的 commit 恢复 src/api.py"
```

仓库中的 fixture 可以重复得到下面的结果：

| | p95 | 测试 | 判定 |
|---|---:|---|---|
| Baseline | 224.305 ms | 通过 | — |
| 第 1 次尝试 | 163.196 ms | 通过 | **接受** |
| 总收益 | **−27.2%** | 仍然全绿 | 达到目标 |

数字变快还不够。如果测试失败，或者这次尝试修改了 benchmark、数据集及其他 frozen 输入，autodev 也会拒绝这次尝试并恢复到上一个已接受状态，即使新的跑分看起来更好。

### 3. “更好”没有定义时，先停下来

```text
把这块代码重构得更优雅一些。
```

这句话没有可执行的验收标准，所以 autodev 不会自行猜测，也不会直接改代码。它会请你选择一个能够运行的目标，例如：保持行为不变并降低复杂度、提高覆盖率、缩小产物体积，或者采用更符合当前仓库的指标。

同一条规则也会拦住虚假的优化。比如提高批量导入吞吐量时，autodev 会冻结测试、benchmark、数据集、runner 配置和 lockfile。删掉一半数据或者放宽断言，即使吞吐量上涨，也只会得到一次失败的尝试。

## 工作流程

![autodev 工作流程：Define、Anchor、Ratchet、Prove](docs/assets/autodev-overview.zh.png)

| 阶段 | 作用 | 完成标志 |
|---|---|---|
| **Define · 定义** | 把需求变成可证伪目标、可执行 gate、边界、预算和回滚方式 | contract 已明确并确认 |
| **Anchor · 锚定** | 冻结量尺，建立可信的起点 | 已验证 RED，或已记录 baseline 与噪声 |
| **Ratchet · 棘轮** | 测量每次尝试，然后接受，或者恢复到上一个已接受状态 | 每次尝试都有机械判定和日志 |
| **Prove · 证明** | 从干净条件验证最终状态，并整理证据 | 测试、测量结果、成本和失败记录都已交付 |

真正起作用的是两种已经被反复验证的方法：

1. **TDD 是正确性 gate。** 新行为从失败测试开始。性能数字再漂亮，也不能拿正确性做交换。
2. **Ratchet 是进展 gate。** benchmark 被固定，预算提前约定，每次尝试都必须由脚本决定是接受还是恢复。这套机制受到 [autoresearch](https://github.com/karpathy/autoresearch) 接受 / 拒绝 loop 的启发。

### 根据需求自动选择模式

| 需求 | 成功条件 | 模式 | 预算 |
|---|---|---|---|
| 增加 / 实现 / 修复 X | 相关测试从 RED 变成 GREEN | **开发** | 无 |
| 让 X 更快 / 更小 / 更便宜 | 测试保持全绿，指标超过 baseline 和噪声 | **优化** | 必须有 |
| 增加 X，同时不能超过某个上限 | 正确性和指标同时达标 | **优化** | 必须有 |
| 让 X “更好”或“更干净” | 没有可执行标准 | **停止并询问** | — |

你不需要手动选择模式。autodev 会根据需求本身判断，只询问真正缺失的信息。优化任务最多问两个问题——指标与目标不明确时问一次，预算问一次——然后只需要你确认一遍完整 contract。

## 快速开始

### 安装

```bash
npx skills add Momoyeyu/autodev -g
```

只安装到 Claude Code、全局、免交互：

```bash
npx -y skills add Momoyeyu/autodev --skill autodev -a claude-code -g --copy -y
```

不安装，只试用一次：

```bash
npx skills use Momoyeyu/autodev@autodev --agent claude-code
```

### 像平常一样描述任务

不需要学习特殊的 prompt 模板：

```text
实现筛选后交易列表的 CSV 导出。
```

```text
把 CLI 启动时间至少缩短 5%，最多尝试 10 次或运行 15 分钟。
```

开发任务会直接从失败测试开始；优化任务会先展示 contract，得到确认后才会使用你批准的预算。

## 运行评测样例

上面的场景都以可重复样例的形式保存在 [`evals/`](evals/README.md)：

```bash
python3 evals/run.py list
python3 evals/run.py run --case development-feature
python3 evals/run.py run
```

每个 case 都会创建独立的 Git 仓库，并把当前版本的 skill 安装到 `.devin/skills/autodev`。Agent 的回复、完整 transcript、diff、命令输出和修改后的 workspace 都会保存在已忽略的 `.autodev-evals/` 目录，方便逐项 review。

Review 完成后，一条受保护的命令即可删除全部运行产物：

```bash
python3 evals/run.py clean
```

不调用模型，也可以验证 fixture、runner、清理保护、语料结构和评分器：

```bash
python3 -m unittest discover -s tests -v
```

## Skill 里有什么

| 文件 | 何时加载 | 作用 |
|---|---|---|
| [`autodev/SKILL.md`](autodev/SKILL.md) | 每次 autodev 运行 | 两种模式、四阶段、两个 gate、必要判定与保护规则、按需文档路由 |
| [`references/gate.md`](autodev/references/gate.md) | 修改生产代码或测试之前 | 正确性 gate：RED → GREEN → REFACTOR、借口辨析和完成清单 |
| [`references/contracts.md`](autodev/references/contracts.md) | Define 中定义优化任务，或需要设计 contract 时 | 六个 contract 字段、指标选择、frozen 变量和 benchmark 构建方法 |
| [`references/progress-gate.md`](autodev/references/progress-gate.md) | 优化任务进入 Anchor 之前 | 进展 gate：测量、Ratchet 判定、局部恢复、日志、停止条件和 Prove 证据 |
| [`references/testing-anti-patterns.md`](autodev/references/testing-anti-patterns.md) | 仅在新增或修改 mock、helper、测试专用 API 时 | 确保测试验证真实行为，而不是验证替身本身 |
| [`references/testing-examples.md`](autodev/references/testing-examples.md) | 仅在需要具体 TDD 示例时 | 重试与 bug 修复的示范流程，只读相关章节 |

先加载入口，不要预加载整个目录。普通开发任务补充读取正确性 gate；优化任务再读取 contract 和进展 gate。Mock 指南与示例始终按需读取。入口直接链接每个子文档，无须沿多层引用链寻找规则。

Skill 本身不绑定语言和测试框架。它不要求项目使用 Jest、pytest 或额外 runtime，而是复用目标仓库已经信任的命令。

## 参与贡献

行为变更应该同时在 `evals/cases.json` 中增加回归 case。请保持核心 Skill 紧凑，把按条件加载的细节放入 `references/`，并同步维护中英文 README。完整约定见 [`CONTRIBUTING.md`](CONTRIBUTING.md)。

## 许可

[MIT](LICENSE)
