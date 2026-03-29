# Personal Development Workflow

## Branching with Git Worktrees

For parallel development, use git worktrees:

```bash
# From the main project directory
git worktree add ../<repo>-<branch-name> -b <branch-name>
cd ../<repo>-<branch-name>
```

When finished with a feature branch:

```bash
# Go back to main
cd ../<repo>
git worktree remove ../<repo>-<branch-name>
```

This allows working on multiple features simultaneously while maintaining access to all branches.

## Pre-commit Hooks

Checks run automatically on commit:

```bash
poetry run ruff check .
poetry run pyright
```

To bypass hooks temporarily: `git commit --no-verify`
