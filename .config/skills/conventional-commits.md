# Conventional Commits

Format for commit messages following the Conventional Commits specification.

## Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

## Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, missing semicolons, etc |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `test` | Adding or modifying tests |
| `chore` | Maintenance tasks (deps, configs) |

## Rules

1. **Subject line**: imperative mood, lowercase, no period, max 72 chars
2. **Scope**: optional, lowercase, refers to module/package affected
3. **Breaking changes**: add `!` after type or `BREAKING CHANGE:` in footer

## Examples

```
feat(models): add property deduplication hash

Implements SHA256-based hash for matching properties across sources.
Excludes price (changes over time) and coordinates (source variance).

Closes #123
```

```
fix(scraper): handle 404 as non-retryable error

Previously 404 responses triggered retry logic causing unnecessary delays.
Now returns immediately with appropriate error message.
```

```
chore: add pytest and pytest-mock to dev dependencies
```

```
test(property): add serialization roundtrip tests
```

```
refactor(cli)!: change query output format

BREAKING CHANGE: Output columns renamed to use underscores.
Update any scripts parsing CLI output.
```
