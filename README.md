# Personal Development Configuration

## Quick Start

1. Install Python 3.10+
2. Clone your repo
3. Run: `python3 ~/.config/bootstrap.py`
4. Set GitHub token: `export GITHUB_TOKEN=ghp_your_token`

## What This Does

- **Pre-push hook**: Blocks direct pushes to `main`/`master`
- **Pre-commit hook**: Runs `ruff` and `pyright` checks
- **Repo template**: Copies standard files (AGENTS.md, CI, pyright config)

## Directory Structure

```
~/.config/
├── README.md           # This file
├── INSTRUCTIONS.md     # Detailed workflow documentation
├── bootstrap.py        # Setup script
├── hooks/
│   ├── pre-push        # Blocks main/master pushes
│   └── pre-commit      # Runs ruff + pyright
├── opencode/
│   ├── opencode.json   # OpenCode permissions
│   └── INSTRUCTIONS.md # OpenCode-specific workflow
└── repo-template/      # Files to copy into new repos
    ├── AGENTS.md
    ├── pyrightconfig.json
    └── .github/workflows/ci.yml
```

## Bootstrap Commands

| Command | Description |
|---------|-------------|
| `python3 ~/.config/bootstrap.py` | Auto-detect setup |
| `python3 ~/.config/bootstrap.py --hooks` | Install hooks only |
| `python3 ~/.config/bootstrap.py --template` | Copy template only |
| `python3 ~/.config/bootstrap.py --reset` | Reset to defaults (overwrites) |

## Environment Variables

- `GITHUB_TOKEN`: GitHub Personal Access Token (required for branch protection)
- Add to `~/.zshrc` or `~/.bashrc`: `export GITHUB_TOKEN=ghp_your_token`

## Detailed Workflow

See [INSTRUCTIONS.md](INSTRUCTIONS.md) for the complete development workflow.
