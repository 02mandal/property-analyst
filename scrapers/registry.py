"""Scraper registry for managing multiple sources."""

from typing import Type

from scrapers.base import AbstractScraper
from scrapers.rightmove import RightmoveScraper


class ScraperRegistry:
    """Registry of available scrapers by source name."""
    
    _scrapers: dict[str, Type[AbstractScraper]] = {}
    
    @classmethod
    def register(cls, name: str, scraper_class: Type[AbstractScraper]) -> None:
        """Register a scraper class."""
        cls._scrapers[name] = scraper_class
    
    @classmethod
    def get(cls, name: str) -> Type[AbstractScraper] | None:
        """Get a scraper class by name."""
        return cls._scrapers.get(name)
    
    @classmethod
    def create(cls, name: str, **kwargs) -> AbstractScraper | None:
        """Create a scraper instance by name."""
        scraper_class = cls.get(name)
        if scraper_class is None:
            return None
        return scraper_class(**kwargs)
    
    @classmethod
    def names(cls) -> list[str]:
        """List all registered scraper names."""
        return list(cls._scrapers.keys())
    
    @classmethod
    def available(cls) -> dict[str, Type[AbstractScraper]]:
        """Get all registered scrapers."""
        return cls._scrapers.copy()


ScraperRegistry.register("rightmove", RightmoveScraper)
