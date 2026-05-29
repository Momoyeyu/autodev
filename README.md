# Skills

[English](README_en.md) | 中文

我的 AI Agent Skills 合集。

## Agent 接入

Agent 可以通过读取 [`skills.json`](skills.json) 快速发现所有可用 skill，无需遍历仓库。

```
https://raw.githubusercontent.com/Momoyeyu/skills/master/skills.json
```

### 查询可用 skills

```bash
curl -s https://raw.githubusercontent.com/Momoyeyu/skills/master/skills.json | python3 -c "
import json, sys
for s in json.load(sys.stdin)['skills']:
    print(f\"{s['invoke']}  {s['description']}\")
"
```

### 安装单个 skill

```bash
git clone --depth 1 https://github.com/Momoyeyu/skills.git /tmp/_skills
cp -r /tmp/_skills/<skill-name> ~/.claude/skills/
rm -rf /tmp/_skills
```

## Skills 列表

| 调用 | 说明 | 依赖 |
|------|------|------|
| `/gen-images` | 通过 OpenAI 兼容 API 生成配图，支持多模型并行 | Python 3, pyyaml |
| `/tdd` | 测试驱动开发流程 | 无 |
| `/deepseek-claude-code-setup` | 把 Claude Code 接入 DeepSeek（含修复 2.1.154+ 的 400 `system` 报错） | Python 3 |
| `/consistent-commit` | 提交前对齐仓库历史的 author/email 与 message 风格（采样一组提交而非只看 HEAD） | git |

## 手动安装（全部）

```bash
git clone https://github.com/Momoyeyu/skills.git /tmp/_skills
cp -r /tmp/_skills/gen-images /tmp/_skills/tdd /tmp/_skills/deepseek-claude-code-setup ~/.claude/skills/
rm -rf /tmp/_skills
```

## 许可

[MIT](LICENSE)
