# Task Plan: gstack -> gstack-codex 全量改造实现

## Goal
在独立仓 `gstack-codex` 中完成 Python 主栈 + Codex 原生 8 技能迁移，并基于 `agent-browser` 直接调用实现浏览器能力。

## Current Phase
Phase 6

## Phases

### Phase 1: Requirements & Discovery
- [x] Understand user intent
- [x] Identify constraints
- [x] Document in findings.md
- **Status:** complete

### Phase 2: Planning & Structure
- [x] Define approach
- [x] Create project structure
- **Status:** complete

### Phase 3: Implementation
- [x] Implement Python package and command wrappers
- [x] Add 8 skill specs under `.agents/skills`
- [x] Add docs and CI quality gates
- **Status:** complete

### Phase 4: Testing & Verification
- [x] Run unit tests
- [x] Check coverage gate (>=90%)
- [x] Document verification results
- **Status:** complete

### Phase 5: Delivery
- [x] Summarize changes and risks
- [x] Deliver implementation details to user
- **Status:** complete

### Phase 6: GH Skills Validation (Post-Remote Setup)
- [x] Re-verify GitHub auth and repo context
- [x] Enumerate all gh-related skill paths and expected behaviors
- [x] Run real review gh flow (repo/pr detection + greptile fetch endpoints)
- [x] Run real ship gh flow (`gh pr create --fill` success + duplicate handling)
- [x] Validate degraded path (no PR context) remains consistent
- [x] Consolidate evidence into findings/progress and final report
- **Status:** complete

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| 独立仓形态 | 用户指定 `gstack-codex` 与旧方案解耦 |
| 全量迁移 8 技能 | 用户指定全量而非分批 |
| 仅新方案 | 用户明确不需要旧方案并行 |
| Python + uv + pytest | 用户指定 |
| 浏览器底座仅 `agent-browser` | 用户最终指定并替代 `browser-use` |
| 技能层直接调用 `agent-browser` | 用户指定“接口全部直接调用” |
| 覆盖率门槛 90% | 用户指定并作为门禁 |

## Errors Encountered
| Error | Resolution |
|-------|------------|
| 克隆临时目录时 `rm -rf` 命令被策略拦截 | 改为唯一时间戳目录，避免破坏性命令 |
