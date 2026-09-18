<p align="center">
  <a href="./README.md">English</a> · <strong>简体中文</strong>
</p>

# autodev

**别再让 Agent 自己给自己打分。**

Agent 说「feature 做完了」，或者说「性能优化好了」，这两句话你其实都没法验证。autodev 把它们变成可验证的：先把 benchmark 定下来，只让它改指定的文件，最后由脚本判定这次改动到底有没有变好。没变好的一律回滚。

![autodev 的工作流程：contract、baseline、loop、review](docs/assets/autodev-overview.zh.png)

| 阶段 | 发生什么 | 你要做什么 |
|---|---|---|
| **contract** | 写下目标、验收标准、预算，以及哪些文件能改、哪些不能 | 确认一次 |
| **baseline** | 先写 test 或搭 benchmark，跑一次得到 baseline，并给不许改的文件算哈希 | 不用管 |
| **loop** | 改文件 → 跑 benchmark → 脚本判定 → 接受就 commit、拒绝就回滚 → 记一条日志 | 等它用完你批准的预算 |
| **review** | 对最终代码重跑全部 test，再重构，最后汇报这次拿到了多少收益 | 不用管 |

![License](https://img.shields.io/badge/license-MIT-22c55e?style=flat-square)
![Agent Skill](https://img.shields.io/badge/skill-autodev-7C3AED?style=flat-square)
![Version](https://img.shields.io/badge/version-3.0.3-0891b2?style=flat-square)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)

```bash
npx skills add Momoyeyu/autodev -g
```

支持 Claude Code、Cursor、Codex CLI、OpenCode，以及任何能读 `SKILL.md` 的工具。

## 要解决的问题

你让 Agent「把这里弄快点」，它会痛快地改一通、宣布搞定、然后继续下一件事。有三件事会出错，而且都不是因为它偷懒：

1. **自己给自己打分。** 改之前没有测量，「更快」就只是一种说法。先写代码后补的 test 一次就过，什么也证明不了；没有 baseline 的性能数字也一样。
2. **优化的是测量，不是代码。** 缓存 benchmark 输入、缩小评测集、放松容差、跑五遍只报最好的一次。这些在 diff 里看起来全都像进步。
3. **它会忘。** 三十次尝试之后换了个上下文窗口，它会把已经失败过两次的想法再试一遍。

autodev 就是来堵这三个洞的。它把两个已经被验证过的做法拼在一起：

- **测试驱动开发（TDD）**当正确性 gate：先写一个会失败的 test，再写刚好能让它通过的代码。从没失败过的 test 什么也证明不了，所以没有 test 的 feature 不算做完。
- 来自 [autoresearch](https://github.com/karpathy/autoresearch) 的**接受 / 拒绝 loop**：冻结 benchmark、固定预算，由脚本决定留下什么。

## 两种模式，同一套规则

不需要你来选，看需求长什么样就行：

| 你说的话 | 怎么算成功 | 模式 | 时间预算 |
|---|---|---|---|
| 加 / 实现 / 修 X | 一个 test 从失败变成通过 | **开发**（TDD） | **没有** —— 只有做完和没做完 |
| 让 X 更快 / 更小 / 更便宜 | 一个数字打败 baseline | **优化** | **必需** |
| 两个都要：「加 X，而且得快」 | 两个都算 | 优化 | 必需 |

**两种模式都绕不开 TDD。** 优化是在 TDD 之上再加一个 benchmark，而不是把它替换掉：test 照样要过，新代码照样先写 test。如果一次改动让数字变好了、却把 test 弄红了，它会和其他失败一样被回滚 —— 这就是「Agent 靠弄坏 feature 把跑分刷上去」的完整答案。

开发模式没有时间预算。一个 feature 不会因为做到一半被放弃而变得更好；真要是大到一次做不完，autodev 会把它拆成几个小单元。

## 快速开始

### 1. 安装

```bash
npx skills add Momoyeyu/autodev -g
```

只装到 Claude Code、全局、免交互：

```bash
npx -y skills add Momoyeyu/autodev --skill autodev -a claude-code -g --copy -y
```

不想安装，只想试一次：

```bash
npx skills use Momoyeyu/autodev@autodev --agent claude-code
```

### 2. 直接提需求

**开发 feature** —— 没有预算，只有做完和没做完：

```text
实现筛选后交易列表的 CSV 导出
```

```text
RED       写 test "exports filtered rows as csv"   → FAIL: exportCsv is not defined
GREEN     最小实现，12 行                          → PASS（test 全绿）
REFACTOR  抽出 CsvWriter                          → 仍然 PASS
```

**做优化** —— 注意你会先拿到一份待确认的 contract：

```text
让首页加载更快
```

```text
待确认的 contract：
  metric   p95_ms ↓   目标 200ms   测 5 次取中位数（实测噪声 ±2.1%）
  tests    npm test —— 断言数量只增不减
  frozen   bench/**  tests/**  package-lock.json  vite.config.ts
  surface  src/home/**
  budget   15 次尝试 / 约 8 分钟
```

```text
attempt  commit   tests  metric  delta   verdict   note
1        a1b2c3d  pass   184.2   —       baseline  初始状态
2        b2c3d4e  pass   171.5   -12.7   accept    预加载首屏图
3        c3d4e5f  fail   —       —       fail      内联关键 CSS 弄挂了 test
4        d4e5f6g  pass   183.9   +12.4   reject    memo 化请求，没有实际收益
```

### 3. 重点看它拒绝做什么

真正有信息量的是那些被拒绝的尝试。一次从不回滚的运行，要么任务太平凡，要么它在作弊 —— 下面这些规则就是用来分辨这两种情况的。

## 动手之前，它先问什么

autodev 不要求你懂它的内部机制。它最多问两个问题，每个都给出具体选项加自定义项，而且只问需求里还没确定的部分：

```text
优化首页刷新速度

Q1  用哪个指标？
    A. p95 导航延迟        （推荐 —— 覆盖服务端 + 网络 + 渲染）
    B. 可交互时间          （画得快，但响应慢）
    C. gzip 后的包体积     （怀疑是载荷问题）
    D. 自定义

Q2  预算？你在为实际耗时付费，所以价格一并给出：
    A. 快试      ~5 次尝试  / 约 2 分钟
    B. 标准      ~15 次尝试 / 约 8 分钟      （推荐）
    C. 跑到收敛   通常 30-60 次 / 约 30 分钟
    D. 自定义
```

然后完整 contract 给你确认一次。这是整个 loop 里唯一需要人的地方。

开发 feature 什么都不问，因为没什么可问的 —— 那个失败的 test 本身就是验收标准，写下它就是第一件工作。

`--dry-run` 只打印 contract，然后停下。

## 为什么这套 loop 没法作弊

每次尝试都会检查这七条。它们就是「优化代码」和「优化测量」之间的分界线：

1. **不许改的文件在每次尝试前后都算哈希。** 哈希变了，这次尝试直接判失败。
2. **test 只能变强。** 断言数量只许增加或持平，绝不减少。
3. **不许新增依赖、网络调用或硬件分支。**
4. **不许靠缩小工作量造假收益** —— 减少评测样本、缓存结果、memo 化输入、contract 里没要求的预热。
5. **不许 best-of-N。** 固定重复次数，取中位数。跑到某次走运为止就是作弊。
6. **不许用 `.skip`、`xfail` 或放松容差**把 test 刷绿。
7. **数字一样时，改动更小的赢。** 指标不是完整的目标函数，没有这条兜底，loop 只会不断堆复杂度。

## 仓库内容

按需加载 —— 一个每次请求都灌 9k token 的 skill 会被卸载。只有核心是默认加载的，其他文件在触发条件满足时才读。

| 文件 | 何时加载 | 体积 | 内容 |
|---|---|---|---|
| [`autodev/SKILL.md`](autodev/SKILL.md) | skill 被触发时 | **~2.7k tok** | 三条规则、两种模式、四个阶段、判定逻辑、回滚、实验日志、停止条件、反作弊 |
| [`references/gate.md`](autodev/references/gate.md) | 写生产代码或碰 test 时 | ~2.5k tok | 完整的 TDD gate：铁律、两道验证、借口对照表、危险信号、完成前清单 |
| [`references/contracts.md`](autodev/references/contracts.md) | 起草 contract 时 | ~1.5k tok | 怎么选指标、各场景该冻结什么、contract 范例、怎么搭 benchmark |
| [`references/testing-anti-patterns.md`](autodev/references/testing-anti-patterns.md) | 加 mock 或 test 工具时 | ~2.1k tok | 五个反模式，每个都配自查步骤和正确写法 |

开发一个 feature 大约加载 **5.2k token**（核心 + 正确性 gate）；做一次优化大约 **6.7k**（核心 + contract + gate）。除非任务真的横跨全部内容，否则不会四个文件一起加载 —— 而全塞进一个文件的话，每次调用都是 8.7k。

## 适用场景

同样的两层结构换个组合，不需要任何新机制：

| 场景 | test | 指标 | 不许改的文件 |
|---|---|---|---|
| 开发 feature | 新 test 失败 → 通过，套件全绿 | — | 既有 test suite |
| 修 bug | 复现 test 失败 → 通过 | — | 复现 test 本身 |
| 重构 | 行为 test 全绿 | 复杂度 ↓ / 覆盖率 ↑ | 行为规格 |
| 性能 | 全绿 | p95 ↓ | benchmark 脚本、数据集、硬件 |
| 构建耗时 | 全绿 | 构建秒数 ↓ | 核数、并发度、缓存状态 |
| 包体积 | 全绿 | 字节数 ↓ | 构建配置、目标浏览器 |
| 成本 | 全绿 | $/请求 ↓ | 流量形态、价格表 |
| 模型质量 | 不崩、不出 NaN | 验证损失 ↓ | 训练脚本、验证集、**时间预算** |

最后一行正好说明为什么不许改的文件必须按场景推理、不能照抄：在模型训练那里，固定的训练时长**就是**目标本身 —— 「五分钟内能训出来的最好模型」。换成网页就毫无意义，该保护的是机器、数据集和缓存状态。

## 支持的 Agent

任何支持 [Agent Skills 规范](https://agentskills.io)的 Agent 都能用。常见工具的全局安装路径：

| Agent | `--agent` | 全局路径 |
|---|---|---|
| Claude Code | `claude-code` | `~/.claude/skills/` |
| Cursor | `cursor` | `~/.cursor/skills/` |
| Codex CLI | `codex` | `~/.codex/skills/` |
| OpenCode | `opencode` | `~/.config/opencode/skills/` |
| GitHub Copilot | `github-copilot` | `~/.copilot/skills/` |
| Gemini CLI | `gemini-cli` | `~/.gemini/skills/` |
| Windsurf | `windsurf` | `~/.codeium/windsurf/skills/` |
| Amp / Replit / 通用 | `universal` | `~/.config/agents/skills/` |

不想用 CLI 的话，手动安装：

```bash
git clone --depth 1 https://github.com/Momoyeyu/autodev.git /tmp/_autodev
cp -r /tmp/_autodev/autodev ~/.claude/skills/
rm -rf /tmp/_autodev
```

## 范围

autodev 覆盖测试先行的实现、bug 修复、重构，以及优化任何一个你能明确说出来的指标。它刻意不带任何脚本和依赖：contract 在 Phase 0 现场生成，判定复用你项目里已有的命令 —— `npm test`、`pytest`、你自己的 benchmark 脚本。

框架专用模板是有意排除的。一旦这个 skill 认识了 Jest，它就不再适用于 Rust。

- [Skill 核心](autodev/SKILL.md) · [正确性 gate](autodev/references/gate.md) · [contract](autodev/references/contracts.md) · [反模式](autodev/references/testing-anti-patterns.md) · [更新日志](CHANGELOG.md) · [贡献指南](CONTRIBUTING.md)

## 许可

[MIT](LICENSE) —— 可自由使用、修改与分发。

## 贡献

欢迎提 Issue 和 PR，尤其欢迎真实的 loop 运行记录 —— 包括 Agent 试图糊弄自己 benchmark 的那些。请先看[贡献指南](CONTRIBUTING.md)。
