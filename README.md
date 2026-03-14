# gstack-codex

**gstack-codex turns Codex from one generic assistant behavior into explicit engineering operating modes.**

This repository is not a prompt list. It is a workflow system:
- 8 skills in `.agents/skills`, each with a clear job and output contract
- a Python CLI (`gstack-codex`) for deterministic helper actions
- direct `agent-browser` commands for browser QA and authenticated session reuse

If your team already relies on coding agents, this repo gives you a practical way to standardize planning depth, review rigor, release safety, browser QA evidence, and retro quality.

## Why this exists

Most teams do not fail because models cannot write code. They fail because process quality is inconsistent:
- one day planning is sharp, next day scope drifts
- one PR gets deep review, another gets “looks good”
- release steps are remembered from memory and vary by person
- browser testing is ad-hoc and rarely reproducible
- retros are discussion-heavy but action-light

gstack-codex addresses that by making mode switching explicit. You choose the mode, and the session follows that mode’s contract.

## Without vs with gstack-codex

### Without

- Planning jumps to implementation before goal and scope are locked.
- “Review my PR” yields variable depth and blind spots.
- “Ship this” becomes a long back-and-forth checklist recreation.
- Browser regressions are found late because evidence is weak.
- Team learning loops depend on memory, not artifacts.

### With

| Skill | Mode | Primary outcome |
|---|---|---|
| `plan-ceo-review` | product/founder pressure test | Reframed goal, scope challenge, decision-forcing review |
| `plan-eng-review` | engineering manager/lead review | Buildable architecture + tests + operational risks |
| `review` | pre-landing reviewer | Findings-first review with severity and fix direction |
| `ship` | release operator | Ordered release workflow with explicit safety gates |
| `browse` | browser QA operator | Reproducible browser checks and evidence collection |
| `qa` | QA lead | Mode-based QA execution and report artifacts |
| `setup-browser-cookies` | session bootstrap | Reusable authenticated browser state |
| `retro` | retrospective facilitator | Structured periodic learning with snapshot history |

## One feature, multiple modes (realistic flow)

```text
You:   We want image-based listing creation.

You:   /plan-ceo-review
Agent: Challenges scope and identifies the real user job.

You:   /plan-eng-review
Agent: Produces implementation-ready architecture/test plan.

You:   [implement]

You:   /review
Agent: Flags race/correctness/trust-boundary issues with file:line references.

You:   /ship
Agent: Runs pre-flight, syncs default branch, runs tests, verifies review,
       updates version/changelog, commits, then asks confirmation for push/PR.

You:   /qa https://staging.example.com --quick
Agent: Runs fast browser QA and reports issues with explicit artifacts.
```

The value is predictable depth, not just speed.

## Who should use this

- Teams that already ship with Codex and want repeatable engineering quality.
- Engineers tired of re-explaining release/review rules in every session.
- Projects where browser-visible behavior is part of quality gates.
- Leads who want retrospectives to produce practical follow-up actions.

## Installation

## Requirements

- Python `3.11+`
- [`uv`](https://docs.astral.sh/uv/)
- Node.js + npm
- [`agent-browser`](https://github.com/vercel-labs/agent-browser)

Install browser tooling:

```bash
npm install -g agent-browser
agent-browser install
```

## Option A: run in this repository (recommended)

```bash
git clone <YOUR-REPO-URL> gstack-codex
cd gstack-codex
uv sync --dev
uv run gstack-codex doctor
```

Expected:

```text
OK: agent-browser is available
```

## Option B: register skills globally for Codex

Use this when you want the same skill set across projects.

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

## Option C: copy into a team repository

```bash
mkdir -p /path/to/project/.agents/skills
cp -R /path/to/gstack-codex/.agents/skills/* /path/to/project/.agents/skills/
```

Then add these skills to your project `AGENTS.md` to make trigger expectations explicit.

## 15-minute first run

Run this once to validate installation and basic workflow coverage:

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

Verify:
- tests pass
- coverage remains `>= 90%`
- report file exists in `.gstack/qa-reports/`
- `states/dev.json` can be saved and loaded

## Skill reference (deep version)

Each skill section below covers: when to use, what to ask for, expected output, and common failure patterns.

## `plan-ceo-review`

### Use this when

- the ticket sounds correct but you suspect the real opportunity is larger
- user value is unclear or success criteria are vague
- scope must be challenged before implementation cost locks in

### Ask for

- explicit problem reframing
- scope options (`expand`, `hold`, `reduce`) with tradeoffs
- failure modes tied to business/user impact
- a decision-complete recommendation

### Good output characteristics

- clear “not in scope” boundary
- concrete assumptions and risks
- recommendations you can act on immediately

### Common anti-patterns

- brainstorming without decisions
- generic product advice with no implementation implications
- skipping hard tradeoffs

## `plan-eng-review`

### Use this when

- product direction is stable
- implementation details are still ambiguous
- you want an engineer-ready plan, not additional ideation

### Ask for

- architecture boundaries
- data and control flow
- edge cases/failure modes
- test matrix and acceptance criteria
- rollout/rollback risks

### Good output characteristics

- implementation can start without major missing decisions
- explicit interface and validation expectations
- operational risks are surfaced before coding

### Common anti-patterns

- over-indexing on diagrams without testability details
- no failure-path handling
- plan still requires many new decisions during implementation

## `review`

### Use this when

- branch implementation is functionally complete
- you need merge-risk detection, not stylistic commentary

### Core execution shape

1. inspect branch + diff
2. load checklist from `.agents/skills/review/checklist.md`
3. optional Greptile triage (`.agents/skills/review/greptile-triage.md`)
4. two-pass review: critical first, informational second

### Expected output contract

- findings first
- ordered by severity
- each finding includes file/line and suggested fix
- if no findings, output residual risk/testing gaps explicitly

### Common anti-patterns

- summary-first output with hidden findings
- no file/line references
- “looks good overall” with zero actionable signal

## `ship`

### Use this when

- branch is already reviewed and ready to release
- you want a deterministic release flow with safety gates

### Canonical sequence

1. pre-flight (`git branch`, `git status`, diff/log vs default branch)
2. sync latest default branch
3. run `uv run pytest`
4. run pre-landing review
5. update `VERSION` and `CHANGELOG.md`
6. commit (`git add -A && git commit -m "chore: ship release"`)
7. run `git push` and `gh pr create --fill` only after explicit confirmation

### Safety behavior

- `push` and `create-pr` require user confirmation by policy
- if PR already exists, `gh pr create --fill` may return existing-PR message (expected)

### Common anti-patterns

- skipping changelog/version updates
- running push/PR without explicit confirmation
- assuming `main` branch name when repo default branch differs

## `browse`

### Use this when

- behavior is browser-visible
- screenshots/console/network evidence are required
- you need reproducible steps, not “manual click memory”

### Canonical command style

```bash
agent-browser open <url>
agent-browser snapshot --interactive
agent-browser console
agent-browser errors
agent-browser network requests
```

### Good practice

- define expected outcomes before interacting
- capture evidence immediately after each critical step
- separate functional and layout checks

## `qa`

### Use this when

- you need systematic verification instead of ad-hoc browsing

### Modes

- `diff-aware`: verify branch-affected areas
- `quick`: smoke coverage for fast signal
- `full`: broader exploratory pass
- `regression`: compare against known baseline

### Typical output

- Markdown report summary
- issue list and severity
- baseline/reference artifacts

## `setup-browser-cookies`

### Use this when

- authenticated routes must be tested repeatedly
- logging in manually is noisy or brittle

### Typical pattern

1. bootstrap cookie/session state
2. save state artifact
3. load same state in later sessions
4. run browse/qa checks against authenticated flows

## `retro`

### Use this when

- weekly or milestone retros need structure
- you want trend comparison, not one-off reflection

### Typical outcome

- metrics summary
- contributor-level observations
- compare-mode deltas
- persisted snapshot for future reference

## CLI reference

The `gstack-codex` command includes:

| Command | What it does |
|---|---|
| `doctor` | Validate `agent-browser` availability |
| `browse-open <url>` | Open a URL via `agent-browser` |
| `save-state <path>` | Save browser auth state |
| `load-state <path>` | Load browser auth state |
| `qa-report --url <url> [--mode] [--out] [--app]` | Generate QA report skeleton |
| `ship-steps [--no-pr]` | Print release command sequence |
| `retro-window [arg...]` | Parse and print retro window expression |

Examples:

```bash
uv run gstack-codex doctor
uv run gstack-codex browse-open https://example.com
uv run gstack-codex qa-report --url https://staging.example.com --mode quick
uv run gstack-codex ship-steps
uv run gstack-codex ship-steps --no-pr
uv run gstack-codex retro-window "compare 30d"
```

## Operating notes for real teams

## Branch naming mismatch (`main` vs `master`)

Some workflow docs/examples mention `origin/main`. If your repo default branch is different, detect it first:

```bash
git remote show origin | grep 'HEAD branch'
```

Then substitute branch name in manual ship commands.

## Existing PR behavior

If `gh pr create --fill` reports that a PR already exists, treat that as success for the “PR exists” condition and continue with the existing PR URL.

## Greptile triage behavior

Greptile triage in review/ship is additive. If PR context or credentials are unavailable, workflows should continue in degraded mode and report that status.

## Troubleshooting

## `Skipped loading ... invalid SKILL.md`

Cause: YAML frontmatter syntax error in a skill file.

Fix checklist:
- ensure frontmatter starts/ends with `---`
- quote fields containing `: ` (especially `description`)
- avoid malformed indentation

## `agent-browser` unavailable in `doctor`

```bash
npm install -g agent-browser
agent-browser install
uv run gstack-codex doctor
```

## `uv run pytest` fails coverage gate

Repository policy enforces coverage `>= 90%`. If tests pass but coverage fails, add or adjust tests before release.

## `gh` operations fail

Validate auth and context:

```bash
gh auth status
gh repo view
gh pr status
```

## Validation policy

Before delivery, run:

```bash
uv run pytest
```

Policy expectations:
- tests pass
- core package line coverage `>= 90%`
- unresolved risks are called out in the final delivery note

## Repository layout

```text
.agents/skills/         skill definitions and reference files
src/gstack_codex/       CLI + workflow helper implementation
tests/                  unit tests for CLI and skill modules
.gstack/                generated QA artifacts and local run outputs
states/                 sample state storage location
docs/                   migration and consistency notes
```

## Contribution note

When updating skills or workflow behavior:
- keep `SKILL.md` and implementation logic in sync
- update tests for behavior changes
- update README sections that expose command examples or workflow contracts

This keeps the docs operational rather than aspirational.
