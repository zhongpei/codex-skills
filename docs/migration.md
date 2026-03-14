# Migration Notes: gstack -> gstack-codex

## Status

This repository is the new primary path. Legacy slash/Claude scaffolding is replaced by Codex-native skills while preserving workflow semantics.

## Key Changes

- Switched from `.claude/skills` to Codex-native `.agents/skills`.
- Preserved eight-skill workflow model with expanded specs, templates, and triage references.
- Browser execution uses direct `agent-browser` commands (no hidden wrappers).
- QA reports and retro snapshots are generated under project-local paths (`.gstack/qa-reports`, `.context/retros`).
- Core implementation is Python-first (`uv + pytest`).

## Operational Impact

- Update-check/inline-upgrade flow from legacy gstack is intentionally not migrated.
- Greptile flow is additive: missing credentials causes graceful degradation, not workflow failure.
- Users must install and initialize `agent-browser` separately.
