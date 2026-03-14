---
name: review
description: Pre-landing PR review with checklist enforcement and optional Greptile triage.
---

# Pre-Landing PR Review

## Step 1: Check Branch and Diff

```bash
git branch --show-current
git fetch origin main --quiet && git diff origin/main --stat
git diff origin/main
```

If no effective diff vs main, stop with a no-op summary.

## Step 2: Load Review Checklist

Read `.agents/skills/review/checklist.md`.
If missing, stop and report setup error.

## Step 3: Greptile Triage (Additive)

Read `.agents/skills/review/greptile-triage.md`.
- If PR/credentials/comments unavailable, skip and continue.
- If available, classify comments into `VALID`, `FIXED`, `FALSE_POSITIVE`, `SUPPRESSED`.

## Step 4: Two-Pass Review

- Pass 1 (critical): SQL/data safety, race conditions, trust boundaries
- Pass 2 (informational): quality, tests, frontend, maintainability

## Output Format

- Findings first, sorted by severity
- File and line references
- Suggested fix for each finding
- Greptile summary line if comments were processed

## Rules

- Read-only by default.
- Do not commit/push.
- If no findings, explicitly state residual risk and testing gaps.
