# AGENTS.md

## Working Model

- Use Codex skill triggers from `.agents/skills` for workflow-specific behavior.
- For risky actions (`git push`, release, destructive operations), require explicit user confirmation.
- For browser-visible changes, validate with `browse` or `qa` before claiming completion.
- Keep command execution explicit and reproducible. Prefer deterministic shell snippets.

## Browser Policy

- Browser actions must use `agent-browser` commands directly.
- Do not introduce wrappers that hide command semantics from skills.
- Persist auth via `agent-browser state save/load` or session/profile flags.

## Validation Policy

- Run `uv run pytest` before delivery.
- Keep core package line coverage >= 90%.
- Document unresolved risks in final response.
