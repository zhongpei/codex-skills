---
name: ship
description: "Structured ship workflow: sync, test, review, version/changelog prep, and PR creation with push/PR confirmation gate."
---

# Ship Workflow

This workflow is automation-first, but `git push` and `gh pr create --fill` require explicit confirmation to satisfy project safety policy.

## Step 1: Pre-flight

```bash
git branch --show-current
git status
git diff origin/main...HEAD --stat
git log origin/main..HEAD --oneline
```

## Step 2: Merge Main Before Tests

```bash
git fetch origin main && git merge origin/main --no-edit
```

## Step 3: Run Tests

```bash
uv run pytest
```

If failures exist, stop and report.

## Step 4: Pre-Landing Review

Run `review` workflow and address blocking findings.

## Step 5: Version + Changelog

- Update `VERSION` using 4-part semantics.
- Update `CHANGELOG.md` with comprehensive entry for the ship set.

## Step 6: Commit

```bash
git add -A
git commit -m "chore: ship release"
```

## Step 7: Push + PR (confirmation required)

```bash
git push
gh pr create --fill
```

## Greptile Handling

If credentials/PR context are available, include Greptile triage and action summary.
If not available, continue and mark as degraded mode.
