<p align="center">
  <a href="./README.md">English</a> · <strong>简体中文</strong>
</p>

<p align="center">
  <img src="docs/assets/autodev-brand.zh.svg" alt="autodev — 从设计到交接持续保持共同理解" width="720">
</p>

**autodev 是一个按需使用的 Agent Skill，面向需要充分澄清、直观执行过程和可检查证据的复杂生产变更。**

一次计费重试改造可能跨越 API、队列、数据库和下游账本。对一句需求表示同意还不够：人需要看清准备改什么、实际做到了哪里、哪些检查支撑结论，以及还有哪些不确定性。autodev 通过 **Clarify → Loop → Handoff** 持续保持这种共同理解，使用目标项目自己的代码、测试和 benchmark。

```bash
npx skills add Momoyeyu/autodev -g
```

适用于能够加载 `SKILL.md` 的 Agent。它提供工作流和本地证据工具，复用项目已有的开发工具。

## 什么时候使用

当理解偏差、隐藏依赖或验证不足可能让重要变更付出较高代价时，使用 autodev：例如跨服务行为、兼容性敏感的迁移、支付流程、难以定位的回归，或有明确预算和验收目标的性能优化。

简单的局部快速修复通常走常规开发流程。仓库大本身不是使用理由；幂等边界上的一处小改动也可能值得使用。依据变更后果和共同理解的需要选择，而不是给每次编辑都套一层仪式。

| 适合 autodev | 通常使用常规开发流程 |
|---|---|
| 重试策略跨越计费服务、队列 worker 和账本写入 | 明显的拼写错误或直接的局部重命名 |
| 导出变更需要保持跨模块兼容性 | 行为清楚、已有检查充分的小改动 |
| kernel 优化需要可比较测量和受限预算 | 尚无有效测量目标的猜测性优化 |

## 使用体验

![Clarify、Loop、Handoff，贯穿可见状态与可检查证据](docs/assets/autodev-overview.zh.svg)

价值在于持续理解变更，而不是开头画一张图、结尾宣称成功。

| 阶段 | Agent 准备或执行什么 | 人可以检查什么 |
|---|---|---|
| **Clarify · 对齐** | 查实际代码；准备目标产物；建立 baseline；提出范围和验证依据 | 实现前一次审阅完整准备结果 |
| **Loop · 迭代** | 在共识内实现，裁决有意义的检查点，更新实际局部状态 | 改了什么、检查记录、未完成路径、失败和下一步 |
| **Handoff · 交接** | 验证保留的源码状态，准备必需产物、证据与限制 | 交付了什么、验证过什么、仍有哪些不确定性、如何继续 |

Clarify 是实际准备，不只是问问题。Agent 从代码画图、准备或维护测试、试运行命令、记录未改动源码的 baseline，并提出边界。**一次用户审阅覆盖整轮准备结果**：目标产物、baseline、范围和验证依据。用户决定修订还是批准进入 Loop。已有决定直接复用；意图、target 含义或允许范围变化时，回到 Clarify。

Loop 在独立 git worktree 和专用分支进行。尝试以 commit 记录，调用项目约定命令裁决。开发中的失败检查点保持可见；无效改动会回滚，被拒绝的优化尝试回到保留的最佳状态。在有意义的已裁决检查点，`report --progress` 生成 `progress.html`，展示已记录检查、可用的当前图和剩余工作。它是再次运行命令才刷新的快照，不是流式看板，也不要求每次工具调用都出报告。

Agent 可以在 `<contract dir>/review.md` 说明用户目标、实际进展、已检查事实、证据缺口和下一步。页面将其明确标注为 **AI review**，与命令执行记录分开。局部实现应保持局部状态的真实样子；下游回归失败和不可用的集成检查也应进入画面。

### 功能开发

![功能开发：对齐设计、检查局部实现、对照交付状态](docs/assets/autodev-development.zh.svg)

从实际代码准备 as-is 架构图与流程图，再提出 blueprint、构建依赖、可编辑范围和回归检查，由用户一次审阅整轮结果。Loop 中展示当前已实现和未完成的职责与路径。Handoff 时依据保留的代码绘制 as-built 图，与 blueprint 对照。

图中的节点记录的是实现声明，不是证明。拓扑不变也可以准确描述行为变化；换 ID 或画出不同的图不能证明正确性。Agent 需要对照代码和支撑证据检查语义。

### 问题修复

![问题修复：复现、对齐回归覆盖、检查失败、交付测试证据](docs/assets/autodev-bugfix.zh.svg)

准备在未改动源码上失败的复现，检查现有测试，保留相关覆盖，有依据地修订过时预期，并补充缺失回归。运行约定测试得到 baseline，提出影响范围，一并交给用户审阅。环境损坏是阻塞，不是 bug 已复现。

Loop 修复直到约定测试全部通过，保留测试版本与原始输出。说明测试覆盖了什么、没有覆盖什么：测试通过是受检行为的证据，不是通用 bug 分类，也不能证明所有生产故障都不可能发生。

### 性能优化

![性能优化：固定 benchmark、可比较尝试、保留结果与过程图](docs/assets/autodev-optimization.zh.svg)

准备一个可执行分数或固定加权和，建立 baseline，提出目标、可编辑文件、测量条件和时间预算，供一次审阅。保持尺子不变。Loop 先尝试改进、测量、保留最佳有效状态，再判断目标或截止时间。除了提升，也记录被拒绝的思路、失败尝试和复测结果。

Handoff 包含 baseline → 尝试 → 保留结果的过程图。超时可以结束工作，但不代表达标。两次 baseline 测量检查的是已观察到的波动，不能给出排除噪声的统计保证。缺失的测量保持缺失。

## 实测案例

这两段历史展示优化工作流的具体使用，不能证明 autodev 对所有任务都有提升，也不能建立普遍的工业有效性。两张图均使用实测记录和 skill 的 `autodev_render.py` 渲染器。

**MoE Transformer —— 英译法翻译模型（PyTorch，单卡 RTX 4090D）。** 目标：BLEU ≥ 28.87（dense 参照值），baseline 24.97，只允许修改 `src/train.py`，每次运行固定墙钟预算。benchmark 在未改动的源码上复跑，同一份代码两次成绩相差 0.62，改进余量因此定为 0.8。31 次尝试、30 个思路标签、4 次被保留——`top1-n4`、`batch-up`、`dropout-down`、`cosine-sched`——达到 31.25；verify 复测 30.91。其余思路（torch.compile、EMA、fused AdamW、容量与层数变体等）测量全部低于余量，逐一回滚。

![MoE 优化的分数轨迹：31 次尝试、4 次保留、超过目标](docs/assets/autodev-case-moe.svg)

**cann2026 —— rotary position embedding kernel（AscendC，CANN 9.0）。** 对同一个 kernel 文件跑了六轮，图中是一条连续轨迹：初始 baseline 为第 0 点，16 次尝试接着编号。所有分数都从 15 个用例的原始耗时出发，按第 3–6 轮使用的同一组固定参考耗时重新计算，共用一条 y 轴，从 19.7026 到最终保留的 0.7168。保留当时的接受／拒绝判定，baseline 复测不计为新尝试。虚线标注最后一轮的目标 0.680，不代表六轮共用这个目标。四轮达到各自目标，第 2、6 轮未达标。第 6 轮里 3 个思路测量低于保留阈值，1 次尝试编译失败被判无效并回滚，保留的连续 token 分块优化拿到 0.7168（target ≤0.680）；最后 verify 撞上评测服务宕机，报告里记录的是宕机，不是一个编出来的分数。

![cann2026 六轮连续优化轨迹：baseline 后接 16 次累计尝试，共用固定参考尺度](docs/assets/autodev-case-cann2026.svg)


## 快速开始

安装 skill 后，请 Agent 对值得采用该流程的变更使用它：

```text
用 autodev 做计费重试和幂等性改造。检查 API、队列 worker、持久化
和下游账本流程。准备现状与目标流程、baseline 检查、可编辑范围和
验证计划，在实现前进行一次完整 Clarify 审阅。保持已有支付兼容性，
明确展示缺失的集成验证证据。
```

Agent 加载 [SKILL.md](autodev/SKILL.md) 和相关参考，准备完整 Clarify 结果，再展示产物供审阅。它使用真实项目命令与环境。数据库集成环境不可用时，应记录缺口并限制结论；单元测试全绿不能证明数据库支撑的幂等行为。

接管运行中的 loop 时，契约目录和专用分支持有已记录状态。新 session 运行 `status`，检查最新证据和审阅说明，处理尚未裁决的工作，再按下一步继续。可选的[项目宪法](autodev/references/constitution.md)可以让冻结路径、guard 检查和优化预算跨轮生效。

## 可以信任什么

| 职责 | 依据与边界 |
|---|---|
| **机械事实** | 裁决脚本记录源码身份、允许范围、冻结文件检查、已配置命令的结果、依赖声明、benchmark 比较、回滚和批准状态。这些事实只适用于实际配置和执行的内容。 |
| **语义审阅** | AI 检查代码与图是否描述预期行为、检查是否充分，以及哪些生产风险尚未验证。推理说明与实测证据分开展示。 |
| **人的决定** | 用户审阅完整 Clarify 准备结果和最终证据包。工具和 AI review 都不能替代这些决定。 |

节点加全绿检查不是语义证明。已批准的 blueprint 可能有误；测试可能遗漏重要交互；环境可能阻断集成验证。autodev 让依据和限制可以被检查，不承诺完美协议或生产就绪。

`report` 生成自包含的最终 `handoff.html`：开发交付 as-built 图，修复交付约定测试结果，优化交付过程图。页面包含源码与原始证据、提供时的 AI review，以及未完成工作。阻塞或局部结果也可以展示，但必须如实标注。

Handoff 批准与进度快照分开。配置检查或 guard 时，批准要求针对保留 commit 的当前验证成功，并有当前最终报告。批准绑定源码、验证记录和报告哈希；源码变化、新验证或最终报告变化都会使其失效。验证失败会阻止批准。未配置检查时，证据包明确标注未配置验证。记录用户批准之后，再合并分支和清理 worktree。

具体操作见[验证](autodev/references/verification.md)、[可视化](autodev/references/visualization.md)和 [Handoff](autodev/references/handoff.md)。产品验证、评估设计与研究背景单独放在[产品验证](docs/evaluation.md)。先把 skill 做成有用的软件，论文是可选结果。

## Skill 结构

| 文件 | 何时加载 |
|---|---|
| [SKILL.md](autodev/SKILL.md) | 判断是否适用并进入流程 |
| [Clarify](autodev/references/clarify.md) | 准备或重新对齐约定 |
| [功能开发](autodev/references/clarify-development.md)、[问题修复](autodev/references/clarify-bugfix.md)、[性能优化](autodev/references/clarify-optimization.md) | 准备相应 target、baseline 和范围 |
| [Loop](autodev/references/loop.md) | 执行已批准约定，或接管运行中的 loop |
| [可视化](autodev/references/visualization.md)、[验证](autodev/references/verification.md) | 展示实际状态并评估支撑证据 |
| [Handoff](autodev/references/handoff.md) | 准备和审阅最终证据包 |
| [项目宪法](autodev/references/constitution.md) | 使用长期项目约束 |
| [裁决脚本](autodev/scripts/autodev_verify.py)、[渲染器](autodev/scripts/autodev_render.py) | 运行本地证据工具；命令细节见其帮助 |

只加载当前阶段和对应分支，不预加载整个参考目录。工具使用 Python 3 标准库，调用项目自己的命令；本仓库不为用户项目提供替代工作负载。

## 参与贡献

保持 skill、双语 README 和配图源文件一致。再生成与验证方式见 [CONTRIBUTING.md](CONTRIBUTING.md)。提出改进时请提供具体任务背景、观察到的行为和证据。

## 许可

[MIT](LICENSE)
