"""CLI for property scraper."""

import argparse
import logging
import sys
from datetime import datetime

from models.watchlist import SearchCriteria, WatchlistEntry
from scrapers import RightmoveScraper, ScraperRegistry
from storage import PropertyDatabase

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def init_db(args: argparse.Namespace) -> None:
    """Initialize database schema."""
    db = PropertyDatabase(args.db)
    db.init_schema()
    print(f"Database initialized at {args.db}")
    db.close()


def run_watchlist(args: argparse.Namespace) -> None:
    """Run scrapes for watchlist entries."""
    db = PropertyDatabase(args.db)
    db.init_schema()

    if args.watchlist_id:
        entry = db.get_watchlist(args.watchlist_id)
        if entry is None:
            print(f"Watchlist entry {args.watchlist_id} not found")
            sys.exit(1)
        entries = [entry]
    else:
        entries = db.get_enabled_watchlist()

    if not entries:
        print("No enabled watchlist entries found")
        sys.exit(0)

    print(f"Running {len(entries)} watchlist entries...")

    for entry in entries:
        print(f"\n--- {entry.name} ---")

        scraper = ScraperRegistry.create(entry.source)
        if scraper is None:
            print(f"Unknown source: {entry.source}")
            continue

        try:
            results = list(scraper.stream(entry.criteria, progress=lambda i, t: print(f"\rScraping {i}/{t}...", end="", flush=True)))
            print()

            new_count = 0
            for result in results:
                if result.record:
                    if db.insert(result.record):
                        new_count += 1

            print(f"  Scraped {len(results)} listings, {new_count} new")

            entry.last_scraped_at = datetime.now()
            if entry.id:
                db.update_watchlist(entry)

        except Exception as e:
            logger.error(f"Error scraping {entry.name}: {e}")

    db.close()


def add_watchlist(args: argparse.Namespace) -> None:
    """Add a new watchlist entry."""
    db = PropertyDatabase(args.db)
    db.init_schema()

    criteria = SearchCriteria(
        location=args.location,
        radius_miles=args.radius,
        min_bedrooms=args.min_bedrooms,
        max_bedrooms=args.max_bedrooms,
        property_types=args.property_type,
        furnished=args.furnished,
        min_price_pcm=args.min_price,
        max_price_pcm=args.max_price,
    )

    entry = WatchlistEntry(
        name=args.name,
        source=args.source,
        criteria=criteria,
        scrape_interval_hours=args.interval,
    )

    entry_id = db.add_watchlist(entry)
    print(f"Added watchlist entry {entry_id}: {args.name}")
    db.close()


def list_watchlist(args: argparse.Namespace) -> None:
    """List all watchlist entries."""
    db = PropertyDatabase(args.db)
    db.init_schema()

    entries = db.watchlist()

    if not entries:
        print("No watchlist entries")
        return

    for entry in entries:
        status = "enabled" if entry.enabled else "disabled"
        print(f"[{entry.id}] {entry.name} ({entry.source}) - {status}")
        print(f"    Location: {entry.criteria.location}, radius: {entry.criteria.radius_miles}mi")
        if entry.last_scraped_at:
            print(f"    Last scraped: {entry.last_scraped_at}")
        print()

    db.close()


def delete_watchlist(args: argparse.Namespace) -> None:
    """Delete a watchlist entry."""
    db = PropertyDatabase(args.db)
    db.init_schema()

    db.delete_watchlist(args.id)
    print(f"Deleted watchlist entry {args.id}")
    db.close()


def query_properties(args: argparse.Namespace) -> None:
    """Query properties from database."""
    db = PropertyDatabase(args.db)
    db.init_schema()

    filters = {}

    if args.source:
        filters["source"] = args.source
    if args.bedrooms:
        filters["bedrooms"] = args.bedrooms
    if args.postcode:
        filters["postcode_outcode"] = args.postcode
    if args.max_price:
        filters["price_pcm__lte"] = args.max_price
    if args.min_price:
        filters["price_pcm__gte"] = args.min_price

    results = db.where(**filters)

    if args.limit:
        results = results.limit(args.limit)

    if args.order:
        desc = args.order.startswith("-")
        field = args.order.lstrip("-")
        results = results.order_by(field, desc)

    records = results.all()

    print(f"Found {len(records)} properties:")
    for r in records:
        price_str = f"£{r.price_pcm / 100:.0f}pcm" if r.price_pcm else "N/A"
        print(f"  [{r.id}] {r.display_address} - {price_str} - {r.bedrooms}bed")

    db.close()


def scrape_url(args: argparse.Namespace) -> None:
    """Scrape a single URL."""
    db = PropertyDatabase(args.db)
    db.init_schema()

    scraper = RightmoveScraper()
    result = scraper(args.url)

    if result and not isinstance(result, list):
        db.insert(result)
        print(f"Scraped: {result.display_address}")
        print(f"  Price: £{result.price_pcm / 100 if result.price_pcm else 0:.0f}pcm")
        print(f"  Bedrooms: {result.bedrooms}")
        print(f"  Bathrooms: {result.bathrooms}")
        print(f"  Agent: {result.agent_name}")
    else:
        print("Failed to scrape URL")

    db.close()


def main():
    parser = argparse.ArgumentParser(description="Property scraper CLI")
    parser.add_argument("--db", default="data/properties.db", help="Database path")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    subparsers.add_parser("init", help="Initialize database")

    run_parser = subparsers.add_parser("run", help="Run watchlist scrapes")
    run_parser.add_argument("--watchlist-id", type=int, help="Specific watchlist ID to run")

    watchlist_add = subparsers.add_parser("watchlist-add", help="Add watchlist entry")
    watchlist_add.add_argument("--name", required=True, help="Watchlist name")
    watchlist_add.add_argument("--source", default="rightmove", help="Source (rightmove)")
    watchlist_add.add_argument("--location", required=True, help="Location (e.g., SE16)")
    watchlist_add.add_argument("--radius", type=float, default=0.5, help="Search radius in miles")
    watchlist_add.add_argument("--min-bedrooms", type=int, dest="min_bedrooms")
    watchlist_add.add_argument("--max-bedrooms", type=int, dest="max_bedrooms")
    watchlist_add.add_argument("--property-type", nargs="+", choices=["flat", "house", "studio"])
    watchlist_add.add_argument("--furnished", choices=["furnished", "unfurnished", "either"], default="either")
    watchlist_add.add_argument("--min-price", type=int, help="Min price in pence PCM")
    watchlist_add.add_argument("--max-price", type=int, help="Max price in pence PCM")
    watchlist_add.add_argument("--interval", type=int, default=4, help="Scrape interval in hours")

    subparsers.add_parser("watchlist-list", help="List watchlist entries")

    watchlist_delete = subparsers.add_parser("watchlist-delete", help="Delete watchlist entry")
    watchlist_delete.add_argument("id", type=int, help="Watchlist entry ID")

    query_parser = subparsers.add_parser("query", help="Query properties")
    query_parser.add_argument("--source")
    query_parser.add_argument("--bedrooms", type=int)
    query_parser.add_argument("--postcode")
    query_parser.add_argument("--min-price", type=int)
    query_parser.add_argument("--max-price", type=int)
    query_parser.add_argument("--limit", type=int)
    query_parser.add_argument("--order")

    scrape_parser = subparsers.add_parser("scrape", help="Scrape a single URL")
    scrape_parser.add_argument("url", help="Property URL to scrape")

    args = parser.parse_args()

    if args.command == "init":
        init_db(args)
    elif args.command == "run":
        run_watchlist(args)
    elif args.command == "watchlist-add":
        add_watchlist(args)
    elif args.command == "watchlist-list":
        list_watchlist(args)
    elif args.command == "watchlist-delete":
        delete_watchlist(args)
    elif args.command == "query":
        query_properties(args)
    elif args.command == "scrape":
        scrape_url(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
