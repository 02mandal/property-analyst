# Property Analyst

A lightweight property scraper for rental listings from Rightmove (and extensible for other sources).

## Features

- Scrape individual property listings from Rightmove
- Manage watchlists with search criteria
- Store properties in SQLite with DuckDB-ready schema
- Rate limiting and exponential backoff to avoid detection
- Extensible architecture for adding new sources

## Installation

```bash
# Install dependencies
poetry install

# Or with pip
pip install requests beautifulsoup4 lxml
```

## Quick Start

### Initialize database

```bash
poetry run python -m cli.main init
```

### Scrape a single property

```bash
poetry run python -m cli.main scrape "https://www.rightmove.co.uk/properties/173794763"
```

### Add a watchlist

```bash
poetry run python -m cli.main watchlist-add \
  --name "SE16 flats" \
  --location "SE16" \
  --max-bedrooms 2 \
  --max-price 300000
```

### List watchlists

```bash
poetry run python -m cli.main watchlist-list
```

### Query properties

```bash
# All properties
poetry run python -m cli.main query

# Filter by bedrooms
poetry run python -m cli.main query --bedrooms 2

# Filter by price
poetry run python -m cli.main query --max-price 300000

# Combine filters
poetry run python -m cli.main query --source rightmove --bedrooms 2 --max-price 350000
```

### Run all watchlist scrapes

```bash
poetry run python -m cli.main run
```

### Search and scrape properties

```bash
poetry run python -m cli.main search \
  --location "SE16" \
  --max-bedrooms 2 \
  --max-price 3000 \
  --furnished furnished
```

This uses Rightmove's API to discover properties matching your criteria and scrapes full details into the database.

## Architecture

```
property-analyst/
├── models/           # Data models (PropertyRecord, WatchlistEntry)
├── scrapers/         # Source scrapers (Rightmove, extensible)
│   ├── base.py      # AbstractScraper, RateLimiter
│   ├── rightmove.py
│   └── registry.py
├── storage/          # Database layer (SQLite + DuckDB ready)
├── services/        # Utilities (geocoding for walk times)
├── cli/             # CLI entry point
└── config.py        # Configuration
```

## Database Schema

Properties are stored with:

- Address, postcode, location (lat/lng)
- Bedrooms, bathrooms, size, property type
- Price (in pence for accuracy)
- EPC rating, council tax band
- Agent information
- Listing history (price reductions, updates)
- Raw data for debugging

## Scheduling

Run via cron for periodic updates:

```bash
# Every 4 hours
0 */4 * * * cd /path/to/property-analyst && poetry run python -m cli.main run
```

## Extending

Add a new source by subclassing `AbstractScraper`:

```python
from scrapers.base import AbstractScraper
from models.property import PropertyRecord

class MyScraper(AbstractScraper):
    name = "mysource"
    
    def search_urls(self, criteria):
        # Return search URLs from criteria
        return [...]
    
    def listings_from_search(self, html):
        # Extract listing URLs from search page
        return [...]
    
    def parse_listing(self, url, html):
        # Parse HTML into PropertyRecord
        return PropertyRecord(...)
    
    def search_api_url(self, criteria, page=0):
        # For API-based search (optional)
        return f"https://api.example.com/search?..."
    
    def listings_from_api(self, criteria, page=0):
        # Fetch listings from API (optional)
        return [...]
```

Register in `ScraperRegistry`:

```python
from scrapers.registry import ScraperRegistry
ScraperRegistry.register("mysource", MyScraper)
```
