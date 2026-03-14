---
name: retro
description: Weekly engineering retro with metrics, contributor analysis, compare mode, and snapshot persistence.
---

# Retro Workflow

## Arguments

- `retro` (default `7d`)
- `retro 24h`, `retro 14d`, `retro 30d`
- `retro compare`
- `retro compare 14d`

## Step 1: Gather Data

- Fetch main and identify current user.
- Collect commit logs, shortlog, hotspots, and PR references.
- Optionally collect Greptile history if available.

## Step 2: Compute Metrics

- Commit counts, contributors, insertions/deletions, net LOC
- Test ratio and activity window metrics
- Per-contributor breakdown

## Step 3: Time and Session Analysis

- Hourly distribution
- Session segmentation

## Step 4: Compare Mode

- Compare current window vs previous window of same size
- Output delta summary

## Step 5: Persistence

- Save snapshot JSON under `.context/retros/`
- Keep current run output in conversation

## Output

- Summary table
- Team highlights
- Risks/debt
- Next-iteration actions
