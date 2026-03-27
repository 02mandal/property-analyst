# Property Analyst

Property scraper for UK rental listings from Rightmove (extensible).

## Tech Stack

- Python 3.10+
- Poetry for dependency management
- SQLite (DuckDB-ready for analytics)

## Commands

```bash
# Install
poetry install

# Run linters (required before commit)
poetry run ruff check .
poetry run pyright

# Run CLI
poetry run python -m cli.main --help
```

## Pre-commit Hook

Before committing, always run:

```bash
poetry run ruff check .
poetry run pyright
```

## Project Structure

```
property-analyst/
├── cli/              # CLI entry point
├── config.py         # Configuration
├── models/           # Data models
├── scrapers/         # Property scrapers
├── services/         # Utilities
├── storage/          # Database layer
└── pyproject.toml    # Dependencies
```
