# Skills

English | [中文](README.md)

My AI Agent Skills collection.

## Agent Access

Agents can read [`skills.json`](skills.json) to discover all available skills without traversing the repo.

```
https://raw.githubusercontent.com/Momoyeyu/skills/master/skills.json
```

### Query available skills

```bash
curl -s https://raw.githubusercontent.com/Momoyeyu/skills/master/skills.json | python3 -c "
import json, sys
for s in json.load(sys.stdin)['skills']:
    print(f\"{s['invoke']}  {s['description']}\")
"
```

### Install a single skill

```bash
git clone --depth 1 https://github.com/Momoyeyu/skills.git /tmp/_skills
cp -r /tmp/_skills/<skill-name> ~/.claude/skills/
rm -rf /tmp/_skills
```

## Skills

| Invoke | Description | Dependencies |
|--------|-------------|--------------|
| `/gen-images` | Generate images via OpenAI-compatible APIs, multi-model parallel | Python 3, pyyaml |
| `/tdd` | Test-Driven Development workflow | None |
| `/deepseek-cc` | Point Claude Code at DeepSeek (incl. fixing the 2.1.154+ 400 `system` error) | Python 3 |

## Manual Install (all)

```bash
git clone https://github.com/Momoyeyu/skills.git /tmp/_skills
cp -r /tmp/_skills/gen-images /tmp/_skills/tdd /tmp/_skills/deepseek-cc ~/.claude/skills/
rm -rf /tmp/_skills
```

## License

[MIT](LICENSE)
