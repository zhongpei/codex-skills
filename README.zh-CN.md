# gstack-codex

`gstack-codex` 是面向 Codex 的工程工作流技能包，适合希望在不同阶段切换“明确工作模式”而非单一泛化助手行为的团队。

它包含：
- `.agents/skills` 下的 8 个工程化技能
- Python CLI（`gstack-codex`）用于可复现的辅助流程
- 与 `agent-browser` 的直接命令集成（无隐藏包装）

本文档是“操作手册”风格：命令优先、与实现对齐、可直接落地。

## 目录

1. [你将获得什么](#你将获得什么)
2. [环境要求](#环境要求)
3. [安装方式](#安装方式)
4. [快速开始](#快速开始)
5. [技能参考（8 Skills）](#技能参考8-skills)
6. [CLI 参考](#cli-参考)
7. [完整多模式示例](#完整多模式示例)
8. [产物与仓库结构](#产物与仓库结构)
9. [故障排查](#故障排查)
10. [验证策略](#验证策略)

## 你将获得什么

### 技能清单

| Skill | 主要用途 | 典型输出 |
|---|---|---|
| `plan-ceo-review` | 实现前挑战问题定义与范围 | 决策完整的产品/策略评审 |
| `plan-eng-review` | 范围确定后的架构与测试方案收敛 | 可直接实现的工程计划 |
| `review` | 合并前代码评审（清单 + 可选 Greptile 分诊） | 按严重级排序的问题清单（含文件/行号） |
| `ship` | 结构化发版流程，含 push/PR 确认门禁 | 顺序化发布动作与安全检查 |
| `browse` | 浏览器可见变更验证与狗粮测试 | 证据化的通过/失败结论 + 截图/日志 |
| `qa` | `diff-aware` / `full` / `quick` / `regression` 系统化 QA | Markdown 报告 + baseline JSON |
| `setup-browser-cookies` | 通过 `state save/load` 完成登录态复用 | 可复用的认证浏览器状态 |
| `retro` | 周期性工程复盘，支持 compare 与快照落盘 | 指标摘要 + JSON 历史快照 |

### 这个仓库解决什么问题

该仓库把不同认知模式显式拆分，团队可以按阶段切换：
- 策略模式（`plan-ceo-review`）
- 工程设计模式（`plan-eng-review`）
- 偏保守审查模式（`review`）
- 发布执行模式（`ship`）
- 浏览器验证模式（`browse`、`qa`）
- 登录态会话模式（`setup-browser-cookies`）
- 团队复盘模式（`retro`）

## 环境要求

- Python `3.11+`
- [`uv`](https://docs.astral.sh/uv/)
- Node.js/npm（用于安装 `agent-browser`）
- 已安装并初始化 [`agent-browser`](https://github.com/vercel-labs/agent-browser)：

```bash
npm install -g agent-browser
agent-browser install
```

## 安装方式

### 方式 A：在本仓库直接使用（开发推荐）

```bash
git clone <YOUR-REPO-URL> gstack-codex
cd gstack-codex
uv sync --dev
uv run gstack-codex doctor
```

`doctor` 期望输出：

```text
OK: agent-browser is available
```

### 方式 B：全局安装 Skills（跨项目复用）

用于让这些技能在多个项目的 Codex 会话中可用。

```bash
# 1) 把仓库克隆到稳定目录
mkdir -p "$HOME/.codex/skills-src"
git clone <YOUR-REPO-URL> "$HOME/.codex/skills-src/gstack-codex"
cd "$HOME/.codex/skills-src/gstack-codex"

# 2) 把每个 skill 目录链接到 CODEX_HOME/skills（默认 ~/.codex/skills）
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
mkdir -p "$CODEX_HOME/skills"
for skill_dir in .agents/skills/*; do
  ln -sfn "$(pwd)/$skill_dir" "$CODEX_HOME/skills/$(basename "$skill_dir")"
done

# 3) 在该 clone 中验证工具链
uv sync --dev
uv run gstack-codex doctor
```

说明：
- 本仓库将技能放在 `.agents/skills/*/SKILL.md`，全局注册时逐个链接 skill 目录。
- 若你的 Codex 运行环境依赖项目说明，可在项目 `AGENTS.md` 增加技能使用约定。

### 方式 C：复制到团队项目（项目内分发）

如果你希望团队成员只靠 `git clone` 就得到同一技能定义：

```bash
mkdir -p /path/to/your-project/.agents/skills
cp -R /path/to/gstack-codex/.agents/skills/* /path/to/your-project/.agents/skills/
```

随后在项目 `AGENTS.md` 中列出这些已引入技能，确保会话可稳定触发。

如果你还需要 CLI 辅助命令，建议保留本仓库 clone，并在该仓库中执行 `uv run gstack-codex ...`。

## 快速开始

建议先完整跑一遍以下链路：

```bash
uv sync --dev
uv run gstack-codex doctor
uv run pytest
uv run gstack-codex qa-report --url http://localhost:3000 --mode full --out .gstack/qa-reports
uv run gstack-codex ship-steps
uv run gstack-codex retro-window "compare 14d"
uv run gstack-codex save-state ./states/dev.json
uv run gstack-codex load-state ./states/dev.json
```

执行后检查：
- 测试通过且覆盖率保持 `>=90%`
- `.gstack/qa-reports/` 已生成报告产物
- `states/dev.json` 已创建且可加载

## 技能参考（8 Skills）

触发说明：
- 直接使用技能名触发（例如：`plan-ceo-review`、`qa`、`ship`）
- 部分客户端也支持 `/qa` 这类斜杠别名，语义等价

### `plan-ceo-review`

用于实现前的前置挑战，验证“是不是在解正确问题”。

关注点：
- 前提挑战
- 范围决策（`scope_expansion` / `hold_scope` / `scope_reduction`）
- 失败模式清单
- 架构/安全/数据流/测试/部署风险框架

期望输出：
- `NOT in scope`
- `What already exists`
- 失败模式与建议
- 开放决策与完成摘要

### `plan-eng-review`

在范围已经稳定后，用于产出可落地的工程方案。

关注点：
- 最小安全改动集
- 架构边界与失败场景
- 测试矩阵（unit/integration/e2e）
- 性能与运维风险

期望输出：
- 按严重级给出明确建议
- 显式 TODO 更新
- 可直接交付实现的完成摘要

### `review`

用于功能分支的合并前评审。

执行结构：
1. 对比 `origin/main` 检查分支和 diff
2. 读取 `.agents/skills/review/checklist.md`
3. 可选读取 `.agents/skills/review/greptile-triage.md` 做分诊
4. 双轮评审：先关键问题，再信息性建议

输出契约：
- 结论先给 findings，按严重级排序
- 包含文件/行号定位
- 每个问题给建议修复方向
- 若无问题，也需明确残余风险与测试缺口

### `ship`

用于“内容已就绪”的结构化发布执行。

流程：
1. 预检
2. 合并最新 `origin/main`
3. 执行 `uv run pytest`
4. 执行 `review` 工作流
5. 更新 `VERSION` 与 `CHANGELOG.md`
6. 提交 commit
7. push + 创建 PR（需确认）

安全行为：
- `git push` 与 `gh pr create --fill` 必须显式确认后执行。

### `browse`

用于浏览器可见行为验证和证据采集，直接调用 `agent-browser`。

典型命令模式：

```bash
agent-browser open <url>
agent-browser snapshot --interactive
agent-browser console
agent-browser errors
agent-browser network requests
```

```bash
agent-browser screenshot --annotate
agent-browser screenshot --full
```

```bash
agent-browser set viewport 375 812
agent-browser screenshot mobile.png
agent-browser set viewport 768 1024
agent-browser screenshot tablet.png
agent-browser set viewport 1280 720
agent-browser screenshot desktop.png
```

### `qa`

用于系统化 QA，支持四种模式：
- `diff-aware`：基于改动文件推断受影响路由后做定向检查
- `full`：核心路径全量检查并产出问题清单
- `quick`：快速冒烟
- `regression`：与 baseline 做健康分对比

必需产物：
- `.gstack/qa-reports/report.md`
- `.gstack/qa-reports/baseline.json`
- `.gstack/qa-reports/screenshots/*`

规范模板：
- `.agents/skills/qa/templates/qa-report-template.md`

### `setup-browser-cookies`

用于需要登录态页面的测试，避免每次重复手动登录。

命令流：

```bash
agent-browser --auto-connect state save ./states/<name>.json
agent-browser --state ./states/<name>.json open <target-url>
agent-browser state load ./states/<name>.json
agent-browser cookies
```

规则：
- 状态文件视为敏感信息
- `states/` 不入库
- 若 `--auto-connect` 不可用，退化为手动调试连接方案

### `retro`

用于团队周期复盘。

支持输入：
- `retro`（默认 `7d`）
- `retro 24h`、`retro 14d`、`retro 30d`
- `retro compare`
- `retro compare 14d`

输出包含：
- 指标摘要表
- 团队亮点与风险
- 下一轮动作
- `.context/retros/` 下的快照 JSON

## CLI 参考

命令入口：

```bash
uv run gstack-codex <command>
```

### `doctor`

验证本机 `agent-browser` 可用性。

```bash
uv run gstack-codex doctor
```

返回：
- 成功：`OK: agent-browser is available`
- 失败：可执行的安装提示

### `browse-open <url>`

通过 CLI 包装器打开指定页面。

```bash
uv run gstack-codex browse-open https://example.com
```

### `save-state <path>` / `load-state <path>`

保存并加载浏览器认证/会话状态。

```bash
uv run gstack-codex save-state ./states/dev.json
uv run gstack-codex load-state ./states/dev.json
```

`save-state` 会自动创建父目录。

### `qa-report --url ... [--app ...] [--mode ...] [--out ...]`

生成 QA 报告骨架。

```bash
uv run gstack-codex qa-report \
  --app "Demo App" \
  --url "https://example.com" \
  --mode full \
  --out .gstack/qa-reports
```

默认值：
- `--app App`
- `--mode full`
- `--out .gstack/qa-reports`

### `ship-steps [--no-pr]`

打印 ship 工作流里的发布步骤命令。

```bash
uv run gstack-codex ship-steps
uv run gstack-codex ship-steps --no-pr
```

典型 `ship-steps` 输出：

```text
git branch --show-current
git status
git diff origin/main...HEAD --stat
git fetch origin main && git merge origin/main --no-edit
uv run pytest
run review workflow
update VERSION
update CHANGELOG.md
git add -A && git commit -m 'chore: ship release'
git push
gh pr create --fill
```

### `retro-window [args...]`

解析并校验 retro 窗口参数。

```bash
uv run gstack-codex retro-window
uv run gstack-codex retro-window 14d
uv run gstack-codex retro-window compare 14d
```

输出格式：

```text
raw=<window> amount=<n> unit=<h|d|w> compare=<true|false>
```

## 完整多模式示例

下面是一个覆盖主要模式的完整功能周期示例：

```text
你： [计划模式] 我要做“卖家拍照后自动生成商品草稿”。

你： plan-ceo-review
Agent：范围挑战完成。你的核心目标是提升转化，不是只加上传按钮。
       建议模式：hold_scope，并附带一项扩展（自动标题草稿）。

你： plan-eng-review
Agent：技术方案锁定。给出 upload->classify->draft 异步管线、信任边界、
       失败模式清单，以及 unit/integration/e2e 测试矩阵。

你： [编码实现]

你： review
Agent：发现 2 个 critical、1 个 medium：
       - 封面图选择存在竞态条件；
       - 外部元数据注入缺少校验；
       - 失败上传后的清理回归测试缺失。

你： [修复问题]

你： ship
Agent：预检通过，测试通过，review 清零。
       push/PR 步骤已门禁，等待显式确认。

你： qa
Agent：Diff-aware 执行完成，报告与 baseline 已写入 .gstack/qa-reports/。

你： setup-browser-cookies
Agent：状态已保存到 ./states/dev.json，cookies 已验证。

你： retro compare 14d
Agent：已生成对比摘要，并保存快照到 .context/retros/。
```

围绕实现与发布的一组操作命令示例：

```bash
uv run pytest
uv run gstack-codex ship-steps
uv run gstack-codex qa-report --url http://localhost:3000 --mode diff-aware --out .gstack/qa-reports
uv run gstack-codex retro-window "compare 14d"
```

## 产物与仓库结构

关键路径：
- `.agents/skills/`：技能规范与模板/清单
- `src/gstack_codex/`：Python 模块（CLI、工作流、适配器）
- `tests/`：unit/integration/e2e 覆盖
- `.gstack/qa-reports/`：QA 产物
- `.context/retros/`：retro 快照
- `states/`：本地浏览器状态文件（已 gitignore）

## 故障排查

### `doctor` 报二进制不存在

执行：

```bash
npm install -g agent-browser
agent-browser install
uv run gstack-codex doctor
```

### 浏览器会话/登录态总是丢失

使用持久化状态流程：

```bash
uv run gstack-codex save-state ./states/dev.json
uv run gstack-codex load-state ./states/dev.json
```

并确认 `states/` 仍被 gitignore。

### QA 报告缺少期望产物

检查：
- 是否传入 `--out`（或使用默认 `.gstack/qa-reports`）
- 输出目录是否可写
- 模式值是否有效（`full`、`quick`、`diff-aware`、`regression`）

### `retro-window` 参数不合法

合法示例：
- `24h`
- `7d`
- `14d`
- `2w`
- `compare`
- `compare 14d`

## 验证策略

项目策略要求：
- 交付前执行 `uv run pytest`
- 覆盖率保持 `>=90%`
- 在最终沟通中记录未解决风险

当前仓库已配置：
- `pyproject.toml` 中 pytest 覆盖率门槛
- 默认测试命令：`uv run pytest`
