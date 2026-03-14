---
name: qa
description: Systematic QA workflow with diff-aware, full, quick, and regression modes plus report generation.
---

# QA: Systematic Testing

## Inputs

- URL (optional in diff-aware mode)
- Mode: `diff-aware`, `full`, `quick`, `regression`
- Output dir: default `.gstack/qa-reports/`
- Optional baseline path for regression

## Modes

### Diff-aware
1. Analyze changed files (`git diff main...HEAD --name-only`).
2. Infer affected routes/pages.
3. Test each affected route with browser evidence.
4. Generate scoped report.

### Full
1. Traverse critical flows and major routes.
2. Collect console/errors/network/screenshot evidence.
3. Report 5-10 issues with severity.

### Quick
- 30-second smoke run for primary routes and console health.

### Regression
1. Run full or scoped checks.
2. Compare current health score and issues to baseline.
3. Append regression delta section.

## Workflow Phases

1. Initialize output structure under `.gstack/qa-reports/`
2. Authenticate/session prep if needed
3. Run mode-specific execution
4. Score health
5. Write markdown report + baseline JSON snapshot

## Required Artifacts

- `.gstack/qa-reports/report.md`
- `.gstack/qa-reports/baseline.json`
- `.gstack/qa-reports/screenshots/*`

## Template

Use `.agents/skills/qa/templates/qa-report-template.md` as canonical report structure.
