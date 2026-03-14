# Runbooks

## Local Setup

```bash
uv sync --dev
npm install -g agent-browser
agent-browser install
uv run gstack-codex doctor
```

## QA Report Bootstrap

```bash
uv run gstack-codex qa-report --url http://localhost:3000 --mode full --out .gstack/qa-reports
```

## Save and Reuse Auth State

```bash
uv run gstack-codex save-state ./states/dev.json
uv run gstack-codex load-state ./states/dev.json
```

## Ship Plan Preview

```bash
uv run gstack-codex ship-steps
```

## Retro Window Validation

```bash
uv run gstack-codex retro-window \"compare 14d\"
```

## CI Validation

```bash
uv run pytest
```
