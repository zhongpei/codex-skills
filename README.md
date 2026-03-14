# gstack-codex

Codex-native migration of gstack with eight workflow skills, detailed skill specs, and direct `agent-browser` integration.

## Requirements

- Python 3.11+
- `uv`
- `agent-browser` installed and initialized:

```bash
npm install -g agent-browser
agent-browser install
```

## Quick Start

```bash
uv sync --dev
uv run gstack-codex doctor
uv run pytest
```

## CLI Helpers

```bash
uv run gstack-codex qa-report --url https://example.com --out .gstack/qa-reports
uv run gstack-codex ship-steps
uv run gstack-codex retro-window \"compare 14d\"
uv run gstack-codex save-state ./states/dev.json
```

## Layout

- `.agents/skills/` skill specs (`SKILL.md`) and templates/checklists
- `src/gstack_codex/` workflow orchestration and command adapters
- `tests/` unit, integration, and e2e checks
- `docs/` migration, runbook, and consistency audit artifacts

E2E acceptance change
