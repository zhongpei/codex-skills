---
name: plan-ceo-review
description: CEO/founder-mode plan review with scope challenge, failure-mode pressure testing, and decision-forcing outputs.
---

# Mega Plan Review Mode

Use this skill before implementation to challenge the premise and produce a decision-complete plan.

## Step 0: Nuclear Scope Challenge + Mode Selection

### 0A. Premise Challenge
1. Is this the right problem to solve?
2. Is the proposed implementation solving user outcome or just a proxy?
3. What is the cost of doing nothing?

### 0B. Existing Code Leverage
1. What already exists and can be reused?
2. What should be refactored instead of rebuilt?

### 0C. Dream State Mapping
```
CURRENT -> THIS PLAN -> 12-MONTH IDEAL
```

### 0D. Mode Selection
- `scope_expansion`
- `hold_scope`
- `scope_reduction`

Commit to selected mode and do not silently drift.

## Review Sections

1. Architecture Review
2. Error & Rescue Map
3. Security & Threat Model
4. Data Flow & Edge Cases
5. Test Matrix and Missing Coverage
6. Deployment, Rollback, and Observability

## Required Output

- NOT in scope
- What already exists
- Failure Modes Registry
- Diagram requirements
- Completion summary with open decisions

## Rules

- Findings are concrete, not generic.
- Every critical issue includes recommendation + alternatives.
- No implementation mutations in this skill.
