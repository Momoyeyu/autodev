<p align="center">
  <a href="./README.md">English</a> · <strong>简体中文</strong>
</p>

![测试驱动开发 —— 红、绿、重构](docs/assets/tdd-hero.svg)

# 测试驱动开发（TDD）

**让 AI Agent 用「一个先失败的测试」换取每一行生产代码。**

TDD 是一个单目录的 Agent Skill，支持 Claude Code、Cursor、Codex CLI、OpenCode 等一切能读取 `SKILL.md` 的工具。它内置了铁律、带强制验证关卡的 RED → GREEN → REFACTOR 完整循环，以及针对模型（或你自己）会抛出的每一个借口的现成反驳。

- **是硬性关卡，不是风格建议** —— 没有「亲眼看着失败」的测试，就不许写生产代码
- **两次验证都不可跳过** —— 先运行测试并确认它**因为预期原因**失败，再确认它通过且整套测试仍然全绿
- **每个借口都预先反驳** —— 「太简单不用测」「我回头补测试」「我手动测过了」「删掉几小时的活太浪费」，逐条对应答案
- **内置 mock 卫生检查** —— 配套文档专门抓「断言 mock 行为」「给生产类加测试专用方法」「静默不完整的 mock」
- **零依赖、零脚本** —— 纯 Markdown，任何 Agent 今天就能用

![License](https://img.shields.io/badge/license-MIT-22c55e?style=flat-square)
![Agent Skill](https://img.shields.io/badge/Agent-Skill-7C3AED?style=flat-square)
![Version](https://img.shields.io/badge/version-1.0.0-0891b2?style=flat-square)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)

```bash
npx skills add Momoyeyu/test-driven-development -g
```

## 要解决的问题

AI Agent 写代码又快又像模像样，但「像模像样」不等于「正确」。凡是 review 过 Agent 产出的人都熟悉这个固定剧本：

1. Agent 先把实现写完。
2. Agent 再补一批测试，用来描述它刚刚写完的实现。
3. 测试一次就过，于是什么都没被证明 —— 没有发现任何边界情况，没有抓到任何 bug，而测试套件把当前行为（连同其中的 bug）永久锁死了。

先写代码再补的测试回答的是「这段代码做了什么」；先写的测试回答的是「这段代码应该做什么」。只有第二个问题能找出你漏掉的情况。

## 循环

![TDD 循环：RED、GREEN、REFACTOR](docs/assets/tdd-cycle.svg)

| 阶段 | Agent 要做什么 | 不可跳过的验证 |
|---|---|---|
| **RED** | 写一个最小测试：名字清晰、只断言一个行为、针对真实代码 | 运行它，确认失败**原因是功能缺失**，而不是打错字或 import 失败 |
| **GREEN** | 写让这一个测试通过的最简代码 —— 不加多余选项，不加任何投机参数 | 运行它，确认通过、其余测试仍全绿、输出干净无警告 |
| **REFACTOR** | 消除重复、改善命名、抽取辅助函数 —— 行为保持不变 | 每次改动后始终保持绿色 |
| **重复** | 针对下一个行为，写下下一个失败测试 | —— |

Skill 明确写出了这个循环要守护的规则：

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
（没有先失败的测试，就没有生产代码）
```

先于测试写下的代码会被删除 —— 不是「留作参考」，也不是「写测试时顺手改改」。这正是 Agent 想「帮上忙」时最爱走的捷径，所以 Skill 把它点名并禁止。

## 快速开始

### 1. 安装

```bash
npx skills add Momoyeyu/test-driven-development -g
```

只装到 Claude Code、全局、免交互：

```bash
npx -y skills add Momoyeyu/test-driven-development --skill tdd -a claude-code -g --copy -y
```

不想安装，只想试一次：

```bash
npx skills use Momoyeyu/test-driven-development@tdd --agent claude-code
```

### 2. 直接提需求或报 bug

Skill 的描述就是为「实现类任务」触发而写的，所以正常说话即可：

```text
给 /login 接口加限流：每个 IP 每分钟最多 5 次。
```

```text
Bug：注册表单提交空邮箱居然能通过，修一下。
```

### 3. 看它的执行顺序

一次正确的运行长这样 —— 这也正是「装 Skill」比「临时口头要求 TDD」更可靠的原因：

```text
RED       写测试 "rejects empty email"        → npm test → FAIL: expected 'Email required', got undefined
GREEN     加上 trim() 校验                     → npm test → PASS（全绿）
REFACTOR  抽出共用的字段校验                    → npm test → 仍然 PASS
```

如果你的 Agent 收到需求后第一件事是打开实现文件，那说明 Skill 没装上 —— 或者被无视了，而 **Red Flags**（危险信号）章节就是用来抓这种情况的。

## 仓库内容

| 文件 | 作用 |
|---|---|
| [`tdd/SKILL.md`](tdd/SKILL.md) | Skill 本体：适用场景、铁律、三个阶段及其验证关卡、好测试的标准、借口对照表、危险信号、完整的 bug 修复示例、完成前检查清单 |
| [`tdd/testing-anti-patterns.md`](tdd/testing-anti-patterns.md) | 涉及测试或 mock 时加载：五个反模式，每个都给出违规写法、为什么错、门禁函数（Gate Function）和正确写法 |

## 为什么它真的管用

- **它拒绝「先写后补」的折中。** Skill 要的不是「更多测试」，而是改变顺序。顺序本身就是全部机制 —— 从未失败过的测试什么也证明不了。
- **它强制诊断失败原因。**「测试直接过？说明你在测已有行为，去改测试。」「测试报错？先修报错，重跑到它以正确方式失败。」两个最常见的静默失效点，得到的是明确指令而不是靠 Agent 自由裁量。
- **它用模型自己的语言反驳模型。** 模型很擅长生成听起来合理的借口，借口对照表用更短、更硬的答案逐条堵回去。
- **它管住了二阶伤害。** 断言 mock 的测试比没有测试更糟。反模式文档专门针对 Agent 最爱写的那类「假测试」。
- **它对范围保持诚实。** 一次性原型、生成代码、配置文件被列为**需要先问人**的例外，而不是可以钻的空子。

## Skill 要求 Agent 停下来的危险信号

- 测试之前先写了代码
- 实现完成之后才补测试
- 测试第一次运行就通过
- 说不清这个测试为什么失败
- 「我已经手动测过了」
- 「先写后补能达到同样目的，重要的是精神不是形式」
- 「先留着当参考，然后补测试」
- 「已经花了 X 小时，删掉太浪费」
- 「TDD 太教条了，我要务实一点」
- 「这次情况特殊，因为……」

以上每一条都指向同一个指令：**删掉代码，用 TDD 重来。**

## 常见借口与答案

| 借口 | Skill 的答案 |
|---|---|
| 「太简单了不用测」 | 再简单的代码也会坏，而测试只要 30 秒。 |
| 「我回头补测试」 | 一次就过的测试什么也证明不了。 |
| 「我已经手动测过了」 | 手动测试是临时的、不成体系的：没有记录、无法重跑、紧张时最容易漏。 |
| 「删掉几小时的活太浪费」 | 沉没成本。留着无法验证的代码才是真正的浪费。 |
| 「先留着当参考，我先把测试写好」 | 你一定会去改它，那就是先写后补。说删就是删。 |
| 「我得先探索一下」 | 可以 —— 探索完就扔掉，从 TDD 开始。 |
| 「这个测试很难写」 | 听它的。难测意味着难用。 |
| 「TDD 会拖慢我」 | TDD 比在生产环境调试快得多。 |

完整对照表见 [`tdd/SKILL.md`](tdd/SKILL.md)。

## 支持的 Agent

任何支持 [Agent Skills 规范](https://agentskills.io)的 Agent 都可以用。常见工具的全局安装路径：

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
git clone --depth 1 https://github.com/Momoyeyu/test-driven-development.git /tmp/_tdd
cp -r /tmp/_tdd/tdd ~/.claude/skills/
rm -rf /tmp/_tdd
```

## 参考与范围

- [Skill 定义](tdd/SKILL.md) · [测试反模式](tdd/testing-anti-patterns.md) · [更新日志](CHANGELOG.md) · [贡献指南](CONTRIBUTING.md)

本 Skill 覆盖的是「测试先行」的实现工作流：新功能、bug 修复、重构、行为变更。它不是测试框架教程，不是 mock 库指南，也不是覆盖率工具 —— 它刻意不绑定任何语言或框架，因此只要你的 Agent 在写代码，它就能用。

## 许可

[MIT](LICENSE) —— 可自由使用、修改与分发。

## 贡献

欢迎提 Issue 和 PR，尤其欢迎「Agent 无视了这个 Skill」或「Agent 乖乖照做」的真实对话记录。请先看[贡献指南](CONTRIBUTING.md)。

## Star 历史

<p align="center"><a href="https://star-history.com/#Momoyeyu/test-driven-development&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=Momoyeyu/test-driven-development&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=Momoyeyu/test-driven-development&type=Date" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=Momoyeyu/test-driven-development&type=Date" width="600" />
  </picture>
</a></p>
