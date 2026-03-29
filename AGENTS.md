# Development Workflow

## Branching with Git Worktrees

This project uses git worktrees for parallel development.

### Creating a Feature Branch

```bash
# From the main project directory
git worktree add ../<repo>-<branch-name> -b <branch-name>
cd ../<repo>-<branch-name>
```

### Configuration

OpenCode permissions are configured in `~/.config/opencode/opencode.json` to allow access to sibling worktrees:

```json
{
  "permission": {
    "external_directory": {
      "../**": "allow"
    }
  }
}
```

This allows editing files in the main project and sibling worktrees.

## Pre-commit Hooks

Checks run automatically on commit:

```bash
poetry run ruff check .
poetry run pyright
```

To bypass hooks temporarily: `git commit --no-verify`
