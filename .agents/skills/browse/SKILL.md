---
name: browse
description: Browser QA and dogfooding workflow using direct agent-browser commands.
---

# Browse: QA Testing & Dogfooding

Use this skill for browser-visible verification, screenshots, and interaction checks.

## Setup

- `agent-browser` must be installed
- `agent-browser install` completed

## Core QA Patterns

### Verify page load
```bash
agent-browser open <url>
agent-browser snapshot --interactive
agent-browser console
agent-browser errors
agent-browser network requests
```

### Test a user flow
```bash
agent-browser open <url>
agent-browser snapshot --interactive
agent-browser fill <selector-or-ref> "value"
agent-browser click <selector-or-ref>
agent-browser snapshot --interactive
```

### Visual evidence
```bash
agent-browser screenshot --annotate
agent-browser screenshot --full
```

### Responsive check
```bash
agent-browser set viewport 375 812
agent-browser screenshot mobile.png
agent-browser set viewport 768 1024
agent-browser screenshot tablet.png
agent-browser set viewport 1280 720
agent-browser screenshot desktop.png
```

### Upload / dialogs / diff
```bash
agent-browser upload <selector> <file>
agent-browser dialog accept
agent-browser diff url <url-a> <url-b> --screenshot
```

## Output

- Tested path and scope
- Pass/fail observations
- Evidence paths (screenshots, command outputs)
