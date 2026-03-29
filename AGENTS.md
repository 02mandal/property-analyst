# Development Workflow

## Pre-commit Hooks

Checks run automatically on commit:

```bash
poetry run ruff check .
poetry run pyright
```

To bypass hooks temporarily: `git commit --no-verify`

## Skills

Load specialized knowledge with the `/skill` command:

- **conventional-commits**: Commit message format and conventions
- **testing**: Test structure, fixtures, and mocking patterns

## Adding New Tests

See the `testing` skill for detailed guidance on test conventions and patterns.
