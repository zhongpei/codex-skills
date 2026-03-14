# gstack-codex

`gstack-codex` 的核心不是“多一组提示词”，而是把 Codex 的工作过程拆成可执行的工程流程。

一句话定义：
- 用 8 个技能把规划、评审、发布、浏览器 QA、复盘分工明确
- 用 `gstack-codex` CLI 把关键动作做成可复现命令
- 用 `agent-browser` 做真实页面验证，不靠“我点过了，应该没问题”

如果你们团队已经在用 AI 写代码，但质量稳定性还靠个人经验，这个仓库就是为这种阶段准备的。

## 为什么要这样做

现实里的问题通常不是“模型不会写代码”，而是流程不稳：
- 需求还没收敛，开发就开始了
- 同样一句“帮我 review”，有时候很深入，有时候很敷衍
- ship 靠记忆清单，谁来执行谁的步骤都不一样
- 浏览器回归靠手点，没证据、不可复盘
- 周会复盘像聊天，真正可执行的改进项不多

`gstack-codex` 想解决的是这件事：
**把“风格”变成“流程”，把“经验”变成“可复现动作”。**

## 不用这套和用这套，有什么区别

### 不用时

- 计划阶段容易直接写实现细节
- 评审结果随机，取决于当次会话状态
- 发布动作容易漏项（尤其是版本与变更日志）
- 浏览器问题发现得晚，证据又不完整
- 复盘难形成持续改进闭环

### 用了之后

| 技能 | 角色定位 | 结果形态 |
|---|---|---|
| `plan-ceo-review` | 产品/创始人视角压力测试 | 范围取舍、失败模式、决策结论 |
| `plan-eng-review` | 工程负责人视角 | 可落地实现方案（架构/测试/风险） |
| `review` | 合并前守门人 | findings 优先，带定位和修复建议 |
| `ship` | 发布执行者 | 固定顺序发布流 + 风险动作确认门禁 |
| `browse` | 浏览器实测执行 | 可追溯的页面验证证据 |
| `qa` | QA 负责人 | 按模式执行的系统化 QA 结果 |
| `setup-browser-cookies` | 会话状态管理员 | 可复用登录态 |
| `retro` | 复盘主持 | 结构化复盘 + 快照沉淀 |

## 一条完整链路（真实可用，不是口号）

```text
你：   我们要做“拍照后自动生成商品信息”

你：   /plan-ceo-review
系统：先判断目标是否正确，挑战范围，识别失败模式

你：   /plan-eng-review
系统：给出工程实现边界、数据流、测试矩阵和风险点

你：   [按计划实现]

你：   /review
系统：先给阻塞问题，再给非阻塞建议，附文件行号

你：   /ship
系统：预检 -> 同步主分支 -> 测试 -> 复核 -> 版本/日志 -> 提交
       -> 询问确认后再 push/建 PR

你：   /qa https://staging.example.com --quick
系统：给出冒烟结果和可复现问题清单
```

这里最关键的是：每一步都有输入、输出和验收标准。

## 适用人群

- 已经把 Codex 用到日常开发里的团队
- 需要稳定 review/ship 质量，而不是靠“这次碰巧严谨”
- 前端/全栈项目，需要浏览器实测证据
- 需要做工程复盘并长期跟踪改进的负责人

## 安装与接入

### 环境要求

- Python `3.11+`
- [`uv`](https://docs.astral.sh/uv/)
- Node.js / npm
- [`agent-browser`](https://github.com/vercel-labs/agent-browser)

先安装浏览器工具：

```bash
npm install -g agent-browser
agent-browser install
```

### 方式 A：在本仓库直接使用（推荐）

```bash
git clone <YOUR-REPO-URL> gstack-codex
cd gstack-codex
uv sync --dev
uv run gstack-codex doctor
```

出现下列输出表示基础环境正确：

```text
OK: agent-browser is available
```

### 方式 B：全局注册技能（跨项目共用）

```bash
mkdir -p "$HOME/.codex/skills-src"
git clone <YOUR-REPO-URL> "$HOME/.codex/skills-src/gstack-codex"
cd "$HOME/.codex/skills-src/gstack-codex"

CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
mkdir -p "$CODEX_HOME/skills"
for skill_dir in .agents/skills/*; do
  ln -sfn "$(pwd)/$skill_dir" "$CODEX_HOME/skills/$(basename "$skill_dir")"
done

uv sync --dev
uv run gstack-codex doctor
```

### 方式 C：把技能复制到团队项目

```bash
mkdir -p /path/to/project/.agents/skills
cp -R /path/to/gstack-codex/.agents/skills/* /path/to/project/.agents/skills/
```

复制后建议在项目 `AGENTS.md` 明确写出可用技能列表和触发规则。

## 首次跑通（建议 15 分钟）

```bash
uv sync --dev
uv run gstack-codex doctor
uv run pytest

uv run gstack-codex ship-steps
uv run gstack-codex ship-steps --no-pr

uv run gstack-codex qa-report --url http://localhost:3000 --mode full --out .gstack/qa-reports
uv run gstack-codex save-state ./states/dev.json
uv run gstack-codex load-state ./states/dev.json
uv run gstack-codex retro-window "compare 14d"
```

跑完请确认：
- 测试通过
- 覆盖率仍然 `>= 90%`
- `.gstack/qa-reports/` 里有报告文件
- `states/dev.json` 可保存、可加载

## 8 个技能怎么真正用起来

下面不是“功能说明书”，而是落地建议。

## `plan-ceo-review`：先确认你在做对的事

### 什么时候用

- 需求刚提出，还没写代码
- 你怀疑“需求描述”不等于“真正目标”
- 需要做范围取舍（扩/稳/收）

### 你应该要求它输出什么

- 问题重定义
- 范围取舍及代价
- 明确失败模式
- 可决策结论（而不是继续发散）

### 常见误用

- 把它当头脑风暴工具，只收集想法不做决策
- 输出看起来很大，但对实现没有约束力

## `plan-eng-review`：把方向变成能落地的方案

### 什么时候用

- 产品方向已经定了
- 还没进入大规模编码
- 你希望“实现前把坑挖出来”

### 核心关注点

- 架构边界和依赖关系
- 数据流和状态迁移
- 失败路径和降级策略
- 分层测试计划（unit/integration/e2e）

### 常见误用

- 图画得很多，但接口/边界没说清楚
- 没有验收标准，导致实现时继续拍脑袋

## `review`：合并前守住质量底线

### 什么时候用

- 功能已经实现，准备合并前

### 推荐执行顺序

1. 看分支 diff
2. 读取 `.agents/skills/review/checklist.md`
3. 有 PR 上下文时做 Greptile 分诊
4. 先关键问题，再信息性建议

### 你应该拿到的输出

- findings 放在最前面
- 按严重级排序
- 每条有文件/行号
- 每条有修复建议
- 若无问题，也要写清残余风险和测试缺口

### 常见误用

- 总结先行，问题藏在后面
- 没有定位信息，落地成本高
- 用“整体不错”代替具体结论

## `ship`：把发布动作变成固定流程

### 什么时候用

- 分支内容已经 ready
- 你要的是“稳定执行”，不是“边聊边想下一步”

### 标准流程

1. 预检（分支、状态、和默认主分支的差异）
2. 同步默认主分支最新代码
3. 跑 `uv run pytest`
4. 复跑 review 流程
5. 更新 `VERSION` 和 `CHANGELOG.md`
6. 提交（`git add -A && git commit -m "chore: ship release"`）
7. 在明确确认后执行 `git push` 和 `gh pr create --fill`

### 安全门禁

- `push` / `create-pr` 属于风险动作，必须确认
- 如果 PR 已存在，`gh pr create --fill` 报“already exists”是预期行为

### 常见误用

- 只跑测试，不更新版本和变更记录
- 未确认直接 push
- 把 `origin/main` 当固定事实（有些仓库默认分支是 `master`）

## `browse`：让页面验证可复现

### 什么时候用

- 改动是浏览器可见行为
- 你需要可回看的证据（不是“我看起来没问题”）

### 常用命令

```bash
agent-browser open <url>
agent-browser snapshot --interactive
agent-browser console
agent-browser errors
agent-browser network requests
```

### 实操建议

- 先列预期，再执行操作
- 关键路径每一步都留证据
- 功能正确性和布局兼容性分开检查

## `qa`：用模式驱动测试，不靠临场发挥

### 模式选择建议

- `diff-aware`：功能分支改动验证
- `quick`：发版前冒烟
- `full`：较大改动后的全面检查
- `regression`：和历史基线对比

### 典型产物

- Markdown 报告
- 问题清单（含严重级）
- 基线/快照类文件

## `setup-browser-cookies`：解决登录态复用

### 适用场景

- 需要频繁验证登录后页面
- 不希望每次手动登录

### 建议流程

1. 导入或建立会话状态
2. 保存到状态文件
3. 后续会话直接加载状态
4. 结合 `browse/qa` 运行认证路径验证

## `retro`：把复盘变成长期资产

### 什么时候用

- 每周固定复盘
- 里程碑后做阶段复盘

### 目标

- 沉淀指标变化
- 形成可执行改进项
- 保留快照，支持趋势对比

## CLI 参考

当前 `gstack-codex` 子命令如下：

| 命令 | 作用 |
|---|---|
| `doctor` | 校验 `agent-browser` 可用性 |
| `browse-open <url>` | 打开 URL |
| `save-state <path>` | 保存浏览器登录态 |
| `load-state <path>` | 加载浏览器登录态 |
| `qa-report --url <url> [--mode] [--out] [--app]` | 生成 QA 报告骨架 |
| `ship-steps [--no-pr]` | 输出 ship 步骤命令 |
| `retro-window [arg...]` | 解析并打印 retro 时间窗口 |

示例：

```bash
uv run gstack-codex doctor
uv run gstack-codex browse-open https://example.com
uv run gstack-codex qa-report --url https://staging.example.com --mode quick
uv run gstack-codex ship-steps
uv run gstack-codex ship-steps --no-pr
uv run gstack-codex retro-window "compare 30d"
```

## 团队落地时的几个细节

### 1) 默认主分支不一致

有的工作流示例写 `origin/main`，但你的仓库可能是 `master`。
发布前先确认：

```bash
git remote show origin | grep 'HEAD branch'
```

### 2) Greptile 分诊是增强项，不是阻塞项

`review` / `ship` 在没有 PR 上下文或凭据时，应进入降级模式并继续，而不是整条流程停掉。

### 3) 文档与实现要一起维护

改了技能行为或 CLI 参数，就同步更新：
- 对应 `SKILL.md`
- 单元测试
- README 中的命令示例

否则很快就会出现“文档能看、流程不能跑”。

## 常见问题与处理

### `Skipped loading ... invalid SKILL.md`

通常是 frontmatter YAML 写错。
检查项：
- `---` 起止是否完整
- 含 `: ` 的描述字段是否加引号
- 缩进是否破坏 YAML 结构

### `doctor` 提示找不到 `agent-browser`

```bash
npm install -g agent-browser
agent-browser install
uv run gstack-codex doctor
```

### `gh pr create --fill` 提示 PR 已存在

这是正常情况，说明当前分支已有 PR。直接继续在该 PR 上推进。

### 测试通过但覆盖率不达标

仓库策略要求 `>=90%`。需要补测后再 ship。

## 交付前质量门槛

发布前至少执行：

```bash
uv run pytest
```

并确认：
- 测试全通过
- 核心包行覆盖率 `>= 90%`
- 若有未解风险，在交付说明里显式写出

## 仓库结构速览

```text
.agents/skills/         技能定义与配套模板/清单
src/gstack_codex/       CLI 与工作流实现
tests/                  单元测试
.gstack/                本地 QA 产物与运行输出
states/                 浏览器状态文件示例
docs/                   迁移说明与一致性文档
```

这份文档的定位是“可执行说明”，不是“概念介绍”。
如果你打算在团队长期使用，建议再补上你们自己的分支策略、发布节奏和环境地址，形成项目内版本。
