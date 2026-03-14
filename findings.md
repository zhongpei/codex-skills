# Findings & Decisions

## Requirements
- 交付物是“详细计划落地实现”，不是只补文档。
- 改造范围为 gstack 八技能全量迁移。
- 最终工程形态是独立仓 `gstack-codex`。
- 触发模型采用 Codex 原生技能体系（`AGENTS.md` + `.agents/skills`）。
- 浏览器方案最终定为 `agent-browser`，不使用 `browser-use`。
- 浏览器调用方式为技能直接调用，无中间抽象层。
- cookie 能力按“能力等价”定义，不要求旧 UI 1:1。
- 覆盖率门禁为 Python 核心包行覆盖率 >= 90%。
- 一致性目标调整为“规范等价优先”（技能结构/步骤尽量按老版 1:1）。
- `ship` 的 `push/PR` 保留确认闸（遵循现有 AGENTS 安全规则）。
- Greptile 能力要求全量迁移，但无凭据时降级继续。
- 升级检查流（`gstack-update-check`）明确不迁移。
- QA 与 Retro 要求完整复刻老版关键规范（四模式+报告、14-step+compare+快照）。

## Research Findings
- `agent-browser` 是 CLI 优先工具，核心命令包含 `open/snapshot/click/fill/screenshot/console/errors/network`。
- `agent-browser` 已支持 `cookies` 与 `state save/load`，可支持登录会话复用。
- `agent-browser` 支持 `--session`、`--profile`、`--session-name`，可用于隔离和持久会话。
- 旧 `gstack` 依赖 `.claude/skills` 与 slash 命令模型，不适合直接搬到 Codex。
- 初始一致性审计识别出结构和功能缺口，已据此完成补齐实现。
- 实施后审计结论为“通过（含已批准偏差）”，详见 `docs/consistency-audit.md`。
- 真实链路验收已覆盖：`review -> ship -> qa(diff/full/regression) -> retro compare`。
- `agent-browser` 运行链路在本机可用，`gstack-codex doctor` 已通过。
- `gh` 缺失导致 PR 创建和 Greptile 远程动作进入降级分支（符合设计）。

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
| 采用 Python 包方式组织核心逻辑 | 方便测试、覆盖率统计、CI 门禁 |
| 将浏览器命令包装为轻量 runner | 保持“直接调用 agent-browser”同时提升可测性 |
| 技能规范落到 `.agents/skills/*/SKILL.md` | 符合 Codex 技能目录约定 |
| `setup-browser-cookies` 使用 `state save/load` 工作流 | 与 agent-browser 能力对齐并满足“能力等价” |
| 使用 GitHub Actions 执行测试与覆盖率门禁 | 提供持续质量保障 |
| review 技能引入 checklist + greptile triage 支撑文件 | 对齐老版审查规范 |
| ship 工作流改为“自动优先 + push/PR确认” | 同时满足老版流程和现有安全策略 |
| qa 输出固定到 `.gstack/qa-reports` 并生成 baseline JSON | 对齐老版报告与回归模式 |
| retro 快照固定写入 `.context/retros` | 对齐老版历史追踪路径 |

## Issues Encountered
| Issue | Resolution |
|-------|------------|
| agent-browser 官方仓无 Python SDK 入口 | 通过 CLI 进程调用，保持实现与官方能力一致 |
| 用户要求确认新老功能任务高度一致，但现阶段实现较薄 | 输出逐技能证据化审计并明确缺口清单 |
| 本机未安装 GitHub CLI (`gh`) | ship/review 在需 GitHub API 的步骤降级并继续 |

## Resources
- https://github.com/vercel-labs/agent-browser
- https://raw.githubusercontent.com/vercel-labs/agent-browser/main/README.md
- docs/consistency-audit.md

## 2026-03-14 GH Validation Scope

- `gh` 直接相关技能路径已确认：`review`（Greptile triage fetch）与 `ship`（`gh pr create`）。
- `retro` 仅在文档中声明“可选 Greptile 历史”，当前 Python 实现未直接调用 `gh`。
- 当前仓库 remote 已切到 GitHub：`git@github-personal:zhongpei/codex-skills.git`。
- 在沙箱内执行 `gh` 会出现网络不可达/凭据无效假象；提权执行后状态正常（已登录 `zhongpei`，repo scope 可用）。

## 2026-03-14 GH Validation Results

- 已验证 `review` 的两类上下文：
  - 无 PR（`master`）：`gh pr view` 返回 `no pull requests found`，符合降级跳过预期。
  - 有 PR（`chore/gh-skill-validation-20260314`，PR `#1`）：`gh repo view` 与 `gh pr view` 均可正确解析上下文。
- 已实测 Greptile 拉取命令（两个端点）可执行且返回空结果：
  - `repos/$REPO/pulls/$PR_NUMBER/comments`
  - `repos/$REPO/issues/$PR_NUMBER/comments`
- 已对 `review.py` 实现层命令生成进行实测：`greptile_fetch_commands(...)` 产出的两条 `gh api` 命令均返回 `RC=0`。
- 已实测 `ship` 的 PR 创建路径：
  - 首次 `gh pr create --fill` 成功创建 PR：`https://github.com/zhongpei/codex-skills/pull/1`
  - 再次执行返回“already exists”，符合重复创建边界行为。
- 发现并修复一致性问题：`ShipWorkflow` 原步骤为裸 `gh pr create`，在非交互环境会失败；已改为 `gh pr create --fill`，并同步 SKILL 文档和测试。
