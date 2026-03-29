# Project Memory

## Project-Specific Notes

### Search Feature
- Added `listings_from_api()` and `stream_from_api()` to RightmoveScraper
- Use `search` CLI command for one-off property searches

### Architecture
- Scrapers extend `AbstractScraper`
- Registry pattern for source management
- Rightmove supports both scraping and API-based search

## Setup Notes

- Uses poetry for dependency management
- Pre-commit hooks run ruff + pyright
- CI runs on GitHub Actions

