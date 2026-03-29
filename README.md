# Property Analyst

A lightweight property scraper for rental listings from Rightmove (and extensible for other sources).

## Features

- Scrape individual property listings from Rightmove
- Search and stream properties via API
- Manage watchlists with search criteria
- Store properties in SQLite
- Rate limiting and exponential backoff
- Extensible architecture

## Quick Start

```bash
poetry install
poetry run python -m cli.main init
```

### Search properties

```bash
poetry run python -m cli.main search --location "SE16" --max-bedrooms 2 --max-price 3000
```

### Scrape a property

```bash
poetry run python -m cli.main scrape "https://www.rightmove.co.uk/properties/173794763"
```

### Watchlist

```bash
poetry run python -m cli.main watchlist-add --name "SE16" --location "SE16" --max-price 300000
poetry run python -m cli.main run
```

### Query

```bash
poetry run python -m cli.main query --bedrooms 2 --max-price 350000
```

## Architecture

```
├── models/        # Data models
├── scrapers/      # Source scrapers (Rightmove, extensible)
├── storage/       # Database layer
├── services/      # Utilities
├── cli/           # CLI entry point
└── config.py      # Configuration
```

## Extending

Subclass `AbstractScraper` in `scrapers/base.py`. See `scrapers/rightmove.py` for an example.
