# gstack vs gstack-codex Consistency Audit (Post-Remediation)

Date: 2026-03-14
Scope: Functional/task consistency between legacy `gstack` and current `gstack-codex` after remediation.
Method: Skill-contract comparison + implementation/path checks + workflow tests.

## Verdict

`gstack-codex` has moved from MVP skeleton to a parity-oriented implementation with all 8 workflows present and executable helpers added.

Status summary:
- Skill inventory parity: pass (8/8)
- Structural workflow parity: substantially improved
- Remaining differences: intentional and accepted by product decisions

## Accepted Differences

1. Upgrade flow (`gstack-update-check` / inline-upgrade) is intentionally not migrated.
2. `setup-browser-cookies` uses command-based state/cookie flow instead of legacy picker UI.
3. `ship` keeps confirmation gate for `push/PR` to satisfy current AGENTS safety policy.

## Evidence Snapshot

| Area | Legacy (`gstack`) | Current (`gstack-codex`) | Status |
|---|---|---|---|
| Skill inventory | 8 named workflows | 8 matching skills under `.agents/skills` | Pass |
| Review support files | Checklist + Greptile triage docs | Migrated to `.agents/skills/review/` | Pass |
| QA report template | Canonical markdown template | Migrated to `.agents/skills/qa/templates/` | Pass |
| QA modes | diff-aware/full/quick/regression | Implemented in skill + workflow module | Pass |
| Ship pipeline | preflight/test/review/version/changelog/push/PR | Implemented with confirmation gate | Pass (policy-adjusted) |
| Retro snapshots | `.context/retros` history | Implemented snapshot load/save + compare helpers | Pass |
| Browse command adapter | broad QA command set | Expanded `agent-browser` wrapper + legacy mapping helpers | Partial |

## Keyword/Capability Signal

Legacy hits vs new hits (selected signals):
- `Greptile`: 22 -> 17
- `Health Score`: 1 -> 1
- `compare`: 10 -> 11
- `VERSION`: 8 -> 2 (reduced mentions, functionality present in ship helpers)
- `CHANGELOG`: 12 -> 2 (reduced mentions, functionality present in ship helpers)
- `gstack-update-check`: 8 -> 0 (intentional)
- `cookie-import-browser`: 4 -> 0 (intentional command-based replacement)

## Validation

- `uv run pytest`
- Result: 26 passed
- Coverage gate: pass (91.73% >= 90%)

## Conclusion

Current `gstack-codex` now satisfies the agreed migration direction:
- follow legacy workflow intent and structure,
- keep new repository architecture and `agent-browser` adaptation,
- retain safety constraints in AGENTS.

Further parity work should focus on deepening browse/qa runtime behavior rather than structural gaps.
