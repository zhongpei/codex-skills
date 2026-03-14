# gstack-codex

`gstack-codex` is a Codex-native workflow pack for engineering teams that want explicit operating modes instead of one generic assistant behavior.

It combines:
- 8 production-oriented skills under `.agents/skills`
- A Python CLI (`gstack-codex`) for repeatable helper flows
- Direct `agent-browser` command integration (no hidden wrappers)

This README is written as an operator manual: command-first, implementation-aligned, and ready for daily use.

## Table of Contents

1. [What You Get](#what-you-get)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Skill Reference (8 Skills)](#skill-reference-8-skills)
6. [CLI Reference](#cli-reference)
7. [Full Multi-Mode Example](#full-multi-mode-example)
8. [Artifacts and Repository Layout](#artifacts-and-repository-layout)
9. [Troubleshooting](#troubleshooting)
10. [Validation Policy](#validation-policy)

## What You Get

### Skill Inventory

| Skill | Primary Use | Typical Output |
|---|---|---|
| `plan-ceo-review` | Challenge premise and scope before implementation | Decision-complete product/strategy review |
| `plan-eng-review` | Lock architecture/test/perf plan after scope is fixed | Implementation-ready engineering plan |
| `review` | Pre-landing PR review with checklist + optional Greptile triage | Findings-first review with severity and file/line refs |
| `ship` | Structured release workflow with push/PR confirmation gates | Ordered release actions and safety checks |
| `browse` | Browser-visible QA and dogfooding checks | Evidence-backed pass/fail + screenshots/logs |
| `qa` | Systematic QA in `diff-aware` / `full` / `quick` / `regression` modes | Markdown QA report + baseline JSON |
| `setup-browser-cookies` | Auth/session bootstrap with `state save/load` | Reusable authenticated browser state |
| `retro` | Weekly/team retro with compare mode and snapshots | Metrics summary + persisted JSON snapshots |

### Why This Package Exists

This repo separates cognitive modes so teams can switch intentionally:
- strategy mode (`plan-ceo-review`)
- engineering design mode (`plan-eng-review`)
- paranoid code review mode (`review`)
- release execution mode (`ship`)
- browser validation mode (`browse`, `qa`)
- session/auth bootstrap (`setup-browser-cookies`)
- team learning loop (`retro`)

## Requirements

- Python `3.11+`
- [`uv`](https://docs.astral.sh/uv/)
- Node.js/npm (for `agent-browser` installation)
- [`agent-browser`](https://github.com/vercel-labs/agent-browser) installed and initialized:

```bash
npm install -g agent-browser
agent-browser install
```

## Installation

### Option A: Use in This Repository (recommended for development)

```bash
git clone <YOUR-REPO-URL> gstack-codex
cd gstack-codex
uv sync --dev
uv run gstack-codex doctor
```

Expected doctor output:

```text
OK: agent-browser is available
```

### Option B: Install Skills Globally for Codex Sessions

Use this when you want the skills available across projects.

```bash
# 1) Clone this repo somewhere stable
mkdir -p "$HOME/.codex/skills-src"
git clone <YOUR-REPO-URL> "$HOME/.codex/skills-src/gstack-codex"
cd "$HOME/.codex/skills-src/gstack-codex"

# 2) Link each skill into CODEX_HOME/skills (default: ~/.codex/skills)
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
mkdir -p "$CODEX_HOME/skills"
for skill_dir in .agents/skills/*; do
  ln -sfn "$(pwd)/$skill_dir" "$CODEX_HOME/skills/$(basename "$skill_dir")"
done

# 3) Validate tooling in this clone
uv sync --dev
uv run gstack-codex doctor
```

Notes:
- This repo keeps skills under `.agents/skills/*/SKILL.md`; global registration links each skill directory directly.
- If your Codex setup requires project instructions, add a short section in project `AGENTS.md` naming the skill set you expect to use.

### Option C: Add to a Team Repository (project-local)

If you want teammates to get the same skill definitions by cloning the repo:

```bash
mkdir -p /path/to/your-project/.agents/skills
cp -R /path/to/gstack-codex/.agents/skills/* /path/to/your-project/.agents/skills/
```

Then in your project `AGENTS.md`, list the imported skills so sessions reliably trigger them.

If you also want CLI helpers, keep a local clone of this repo and run `uv run gstack-codex ...` from it.

## Quick Start

Run this sequence end-to-end once:

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

After running the sequence, verify:
- tests pass and coverage remains `>=90%`
- `.gstack/qa-reports/` contains report artifacts
- `states/dev.json` is created and loadable

## Skill Reference (8 Skills)

Invocation note:
- trigger by skill name (for example: `plan-ceo-review`, `qa`, `ship`)
- some clients also support slash aliases like `/qa`; semantics are the same

### `plan-ceo-review`

Use before implementation to pressure-test whether you are solving the right problem.

Focus areas:
- premise challenge
- scope decision (`scope_expansion` / `hold_scope` / `scope_reduction`)
- failure mode registry
- architecture/security/data-flow/test/deploy risk framing

Expected output:
- `NOT in scope`
- `What already exists`
- failure modes + recommendations
- open decisions and completion summary

### `plan-eng-review`

Use after scope is fixed to produce an implementation-safe technical plan.

Focus areas:
- minimal safe change set
- architecture boundaries and failure scenarios
- test matrix (unit/integration/e2e)
- performance and operational risks

Expected output:
- concrete recommendations by criticality
- explicit TODO updates
- completion summary ready for implementation handoff

### `review`

Use for pre-landing review on feature branches.

Execution shape:
1. Check branch + diff against `origin/main`
2. Load `.agents/skills/review/checklist.md`
3. Optional Greptile triage from `.agents/skills/review/greptile-triage.md`
4. Two-pass review: critical then informational

Output contract:
- findings first, severity ordered
- file/line references
- suggested fix per finding
- residual risk + testing gaps when no findings

### `ship`

Use for structured release execution when branch content is already ready.

Pipeline:
1. pre-flight checks
2. merge latest `origin/main`
3. run `uv run pytest`
4. run review workflow
5. update `VERSION` and `CHANGELOG.md`
6. commit
7. push + PR creation (confirmation required)

Safety behavior:
- `git push` and `gh pr create --fill` require explicit confirmation.

### `browse`

Use for browser-visible verification and evidence collection via direct `agent-browser` commands.

Canonical command patterns:

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

Use for systematic QA with four modes:
- `diff-aware`: route-scoped checks based on changed files
- `full`: broad app traversal with issue reporting
- `quick`: smoke validation
- `regression`: compare against baseline health

Required artifacts:
- `.gstack/qa-reports/report.md`
- `.gstack/qa-reports/baseline.json`
- `.gstack/qa-reports/screenshots/*`

Canonical template:
- `.agents/skills/qa/templates/qa-report-template.md`

### `setup-browser-cookies`

Use when tests require authenticated pages without redoing login every run.

Command flow:

```bash
agent-browser --auto-connect state save ./states/<name>.json
agent-browser --state ./states/<name>.json open <target-url>
agent-browser state load ./states/<name>.json
agent-browser cookies
```

Rules:
- treat state files as secrets
- keep `states/` out of git
- fall back to manual browser debug setup if `--auto-connect` is unavailable

### `retro`

Use for weekly/team engineering retrospectives.

Supported inputs:
- `retro` (defaults to `7d`)
- `retro 24h`, `retro 14d`, `retro 30d`
- `retro compare`
- `retro compare 14d`

Output includes:
- summary table
- highlights and risks
- next-iteration actions
- snapshot JSON under `.context/retros/`

## CLI Reference

Command root:

```bash
uv run gstack-codex <command>
```

### `doctor`

Validate local `agent-browser` availability.

```bash
uv run gstack-codex doctor
```

Returns:
- success: `OK: agent-browser is available`
- failure: actionable install message

### `browse-open <url>`

Open one URL through the configured `agent-browser` CLI wrapper.

```bash
uv run gstack-codex browse-open https://example.com
```

### `save-state <path>` / `load-state <path>`

Persist and restore browser auth/session state.

```bash
uv run gstack-codex save-state ./states/dev.json
uv run gstack-codex load-state ./states/dev.json
```

`save-state` creates parent directories automatically.

### `qa-report --url ... [--app ...] [--mode ...] [--out ...]`

Generate a QA report skeleton.

```bash
uv run gstack-codex qa-report \
  --app "Demo App" \
  --url "https://example.com" \
  --mode full \
  --out .gstack/qa-reports
```

Defaults:
- `--app App`
- `--mode full`
- `--out .gstack/qa-reports`

### `ship-steps [--no-pr]`

Print the release step commands from the ship workflow.

```bash
uv run gstack-codex ship-steps
uv run gstack-codex ship-steps --no-pr
```

Typical `ship-steps` output:

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

Parse and validate retro window arguments.

```bash
uv run gstack-codex retro-window
uv run gstack-codex retro-window 14d
uv run gstack-codex retro-window compare 14d
```

Output format:

```text
raw=<window> amount=<n> unit=<h|d|w> compare=<true|false>
```

## Full Multi-Mode Example

The sequence below shows one complete feature cycle using all major modes.

```text
You: [plan mode] Add photo-first listing creation for sellers.

You: plan-ceo-review
Agent: Scope challenge complete. You are solving conversion, not upload UI only.
       Recommended mode: hold_scope with one expansion (auto-title draft).

You: plan-eng-review
Agent: Architecture locked. Async upload->classify->draft pipeline, trust boundaries,
       failure registry, and unit/integration/e2e matrix attached.

You: [implement]

You: review
Agent: 2 critical findings, 1 medium.
       - Race condition in cover-image selection.
       - Missing validation around external metadata ingestion.
       - Missing regression test for failed-upload cleanup.

You: [fix findings]

You: ship
Agent: Pre-flight OK, tests green, review clean.
       Push/PR steps are gated and need explicit confirmation.

You: qa
Agent: Diff-aware run complete. Report + baseline written to .gstack/qa-reports/.

You: setup-browser-cookies
Agent: Saved state to ./states/dev.json and verified cookies.

You: retro compare 14d
Agent: Generated compare summary and saved snapshot to .context/retros/.
```

Example operator command set around implementation/release:

```bash
uv run pytest
uv run gstack-codex ship-steps
uv run gstack-codex qa-report --url http://localhost:3000 --mode diff-aware --out .gstack/qa-reports
uv run gstack-codex retro-window "compare 14d"
```

## Artifacts and Repository Layout

Core paths:
- `.agents/skills/` skill specs and templates/checklists
- `src/gstack_codex/` Python modules (CLI, workflows, adapters)
- `tests/` unit/integration/e2e coverage
- `.gstack/qa-reports/` QA artifacts
- `.context/retros/` retro snapshots
- `states/` local browser state files (gitignored)

## Troubleshooting

### `doctor` fails with binary not found

Run:

```bash
npm install -g agent-browser
agent-browser install
uv run gstack-codex doctor
```

### Browser session/auth keeps resetting

Use persistent state flow:

```bash
uv run gstack-codex save-state ./states/dev.json
uv run gstack-codex load-state ./states/dev.json
```

Also ensure `states/` remains gitignored.

### QA reports missing expected artifacts

Check:
- command includes `--out` (or default `.gstack/qa-reports`)
- write permissions for output directory
- mode selection is valid (`full`, `quick`, `diff-aware`, `regression`)

### `retro-window` rejects argument

Valid window examples:
- `24h`
- `7d`
- `14d`
- `2w`
- `compare`
- `compare 14d`

## Validation Policy

Project policy requires:
- run `uv run pytest` before delivery
- keep coverage at `>=90%`
- document unresolved risks in your final communication

Current codebase is configured with:
- pytest coverage gate in `pyproject.toml`
- default test command: `uv run pytest`
