---
name: setup-browser-cookies
description: Command-based authenticated session bootstrap using agent-browser state/cookies features.
---

# Setup Browser Cookies

Goal: capability-equivalent authenticated session import without UI picker.

## Command Flow

```bash
agent-browser --auto-connect state save ./states/<name>.json
agent-browser --state ./states/<name>.json open <target-url>
agent-browser state load ./states/<name>.json
agent-browser cookies
```

## Rules

- Treat state files as secrets.
- Keep state files out of git.
- If auto-connect is unavailable, request manual browser debug setup and continue.

## Output

- Saved state path
- Cookie verification summary
- Any degraded-mode notes
