"""Watchlist entry model."""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class SearchCriteria:
    """Search criteria for a watchlist entry."""
    location: str
    radius_miles: float = 0.5
    listing_type: str = "rent"

    min_bedrooms: int | None = None
    max_bedrooms: int | None = None
    property_types: list[str] | None = None
    furnished: str = "either"

    min_price_pcm: int | None = None
    max_price_pcm: int | None = None

    available_within_days: int | None = None

    center_lat: float | None = None
    center_lng: float | None = None
    max_walk_minutes: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "location": self.location,
            "radius_miles": self.radius_miles,
            "listing_type": self.listing_type,
            "min_bedrooms": self.min_bedrooms,
            "max_bedrooms": self.max_bedrooms,
            "property_types": self.property_types,
            "furnished": self.furnished,
            "min_price_pcm": self.min_price_pcm,
            "max_price_pcm": self.max_price_pcm,
            "available_within_days": self.available_within_days,
            "center_lat": self.center_lat,
            "center_lng": self.center_lng,
            "max_walk_minutes": self.max_walk_minutes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SearchCriteria":
        return cls(
            location=data.get("location", ""),
            radius_miles=data.get("radius_miles", 0.5),
            listing_type=data.get("listing_type", "rent"),
            min_bedrooms=data.get("min_bedrooms"),
            max_bedrooms=data.get("max_bedrooms"),
            property_types=data.get("property_types"),
            furnished=data.get("furnished", "either"),
            min_price_pcm=data.get("min_price_pcm"),
            max_price_pcm=data.get("max_price_pcm"),
            available_within_days=data.get("available_within_days"),
            center_lat=data.get("center_lat"),
            center_lng=data.get("center_lng"),
            max_walk_minutes=data.get("max_walk_minutes"),
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> "SearchCriteria":
        return cls.from_dict(json.loads(json_str))


@dataclass
class WatchlistEntry:
    """A watchlist entry configuration."""
    name: str
    source: str
    criteria: SearchCriteria

    id: int | None = None
    scrape_interval_hours: int = 4
    enabled: bool = True

    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime | None = None
    last_scraped_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "source": self.source,
            "criteria": self.criteria.to_json(),
            "scrape_interval_hours": self.scrape_interval_hours,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_scraped_at": self.last_scraped_at.isoformat() if self.last_scraped_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WatchlistEntry":
        created_at = data.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        updated_at = data.get("updated_at")
        if updated_at and isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)

        last_scraped_at = data.get("last_scraped_at")
        if last_scraped_at and isinstance(last_scraped_at, str):
            last_scraped_at = datetime.fromisoformat(last_scraped_at)

        criteria = data.get("criteria")
        if isinstance(criteria, str):
            criteria = SearchCriteria.from_json(criteria)
        elif isinstance(criteria, dict):
            criteria = SearchCriteria.from_dict(criteria)
        else:
            criteria = SearchCriteria(location="")

        return cls(
            id=data.get("id"),
            name=data["name"],
            source=data["source"],
            criteria=criteria,
            scrape_interval_hours=data.get("scrape_interval_hours", 4),
            enabled=data.get("enabled", True),
            created_at=created_at or datetime.now(),
            updated_at=updated_at,
            last_scraped_at=last_scraped_at,
        )
