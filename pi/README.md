# Pi 适配：同一套 harness，换模型跑

[Pi](https://www.npmjs.com/package/@earendil-works/pi-coding-agent) 是一个极简的 agent harness：核心只有 read / write / edit / bash 四个工具，模型通过 `--model provider/id` 切换。这里用它当执行器：harness 决定模型看到什么，Pi 负责 agent loop，模型只是参数。

## 工作区如何映射到 Pi

| 工作区内容 | Pi 输入 |
|---|---|
| 规则层（playbook、检查点、记忆、常驻 Skill） | `--append-system-prompt` |
| 路由选中的 Skill | `--skill` |
| golden 样本、run record 契约、时点内来源 | `@file` 附件 |
| 任务 + `asof` + 路由 | `-p` 的消息正文 |

另外三个开关保证可复现：`--no-session`（不带历史）、`--no-context-files`（不自动读取 AGENTS.md 等上下文文件，只给路由选中的内容）、`--tools read`（只读）。纠错记录换成按路由筛过的副本；来源文件只包含 `asof` 及之前的材料。

## 安装与配置

```bash
npm install -g @earendil-works/pi-coding-agent
# 遇到 EACCES：npm config set prefix ~/.npm-global，并把 ~/.npm-global/bin 加入 PATH
```

内置 provider（如 anthropic、openai）直接读取对应的环境变量。其他兼容 OpenAI 接口的模型（如 DeepSeek）在 `~/.pi/agent/models.json` 里声明，可以从 `pi/models.example.json` 复制。`apiKey` 填**环境变量名**，不填明文 key；字段以 Pi 文档为准：

```bash
mkdir -p ~/.pi/agent && cp pi/models.example.json ~/.pi/agent/models.json
export DEEPSEEK_API_KEY=...        # 只放在本机 shell 或 .env，永不提交
```

## 运行

```bash
# 只落盘工作区并打印 Pi 命令，不调用模型
irh run "帮我做 AI 陪伴硬件赛道的 mapping，看哪些机构投了" --asof 2026-09-30 \
  --sources examples/ai-companion-hardware/sources.json --dry-run

# 真正调用模型；结果在 runs/<时间>-<路由>/：workspace/、output.md、run.json
pi/run.sh "帮我做 AI 陪伴硬件赛道的 mapping，看哪些机构投了" 2026-09-30 \
  examples/ai-companion-hardware/sources.json deepseek/deepseek-chat
```

运行结束后，`irh run` 会从输出末尾抽取 JSON run record，并直接跑 8 个关口；接着可以 `irh score runs/<id>/run.json --sources ...` 打分。

## 模型对比

固定题目、工作区与判分，只换模型：

```bash
pi/compare_models.sh "帮我做 AI 陪伴硬件赛道的 mapping，看哪些机构投了" 2026-09-30 \
  examples/ai-companion-hardware/sources.json deepseek/deepseek-chat anthropic/claude-sonnet-5-5
```

两边都挂在同一个关口上，多半是 harness 或 Skill 的问题；只有一边挂，才更像是模型能力的差异。

运行需要能访问模型 API 的网络环境。
