---
name: plan-eng-review
description: Engineering manager mode plan review with architecture, code quality, tests, performance, and rollout rigor.
---

# Plan Review Mode

Use this skill after product scope is locked.

## Step 0: Scope Challenge

1. Which existing code solves parts of the problem?
2. What is the minimum safe change set?
3. Is complexity justified (files touched, new abstractions)?

## Review Sections

### 1. Architecture Review
- Component boundaries
- Dependency graph
- Data flow and failure scenarios

### 2. Code Quality Review
- Module boundaries
- DRY issues
- Error handling and edge cases

### 3. Test Review
- New codepaths and branches
- Missing unit/integration/e2e tests
- Evaluation coverage for prompt-related changes

### 4. Performance Review
- Slow paths and N+1 risks
- Caching opportunities
- Memory-pressure risks

## Required Output

- NOT in scope
- What already exists
- TODO updates
- Completion summary

## Rules

- Prioritize correctness over style commentary.
- Use explicit recommendations for each critical issue.
- No implementation mutations in this skill.
