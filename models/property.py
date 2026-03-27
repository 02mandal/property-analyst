"""Property record model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class PropertyRecord:
    """A property listing record."""
    source: str
    source_url: str
    
    display_address: str | None = None
    property_type: str | None = None
    bedrooms: int | None = None
    bathrooms: int | None = None
    size_sqft: int | None = None
    floor_level: str | None = None
    furnished: str | None = None
    
    price_pcm: int | None = None
    price_pw: int | None = None
    original_price_pcm: int | None = None
    price_reduction_count: int = 0
    
    latitude: float | None = None
    longitude: float | None = None
    postcode: str | None = None
    postcode_outcode: str | None = None
    postcode_incode: str | None = None
    
    description: str | None = None
    key_features: list[str] = field(default_factory=list)
    images: list[str] = field(default_factory=list)
    
    epc_rating: str | None = None
    council_tax_band: str | None = None
    
    agent_name: str | None = None
    agent_address: str | None = None
    
    listing_update_reason: str | None = None
    available_date: str | None = None
    
    scraped_at: datetime = field(default_factory=datetime.now)
    first_seen_at: datetime | None = None
    updated_at: datetime | None = None
    
    raw_data: dict[str, Any] | None = None
    status: str = "active"
    
    @property
    def id(self) -> str:
        return self.source_url.split("/")[-1].split("#")[0]
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "source_url": self.source_url,
            "status": self.status,
            "display_address": self.display_address,
            "property_type": self.property_type,
            "bedrooms": self.bedrooms,
            "bathrooms": self.bathrooms,
            "size_sqft": self.size_sqft,
            "floor_level": self.floor_level,
            "furnished": self.furnished,
            "price_pcm": self.price_pcm,
            "price_pw": self.price_pw,
            "original_price_pcm": self.original_price_pcm,
            "price_reduction_count": self.price_reduction_count,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "postcode": self.postcode,
            "postcode_outcode": self.postcode_outcode,
            "postcode_incode": self.postcode_incode,
            "description": self.description,
            "key_features": self.key_features,
            "images": self.images,
            "epc_rating": self.epc_rating,
            "council_tax_band": self.council_tax_band,
            "agent_name": self.agent_name,
            "agent_address": self.agent_address,
            "listing_update_reason": self.listing_update_reason,
            "available_date": self.available_date,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
            "first_seen_at": self.first_seen_at.isoformat() if self.first_seen_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "raw_data": self.raw_data,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PropertyRecord":
        scraped_at = data.get("scraped_at")
        if scraped_at and isinstance(scraped_at, str):
            scraped_at = datetime.fromisoformat(scraped_at)
        
        first_seen_at = data.get("first_seen_at")
        if first_seen_at and isinstance(first_seen_at, str):
            first_seen_at = datetime.fromisoformat(first_seen_at)
        
        updated_at = data.get("updated_at")
        if updated_at and isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        
        return cls(
            source=data["source"],
            source_url=data["source_url"],
            status=data.get("status", "active"),
            display_address=data.get("display_address"),
            property_type=data.get("property_type"),
            bedrooms=data.get("bedrooms"),
            bathrooms=data.get("bathrooms"),
            size_sqft=data.get("size_sqft"),
            floor_level=data.get("floor_level"),
            furnished=data.get("furnished"),
            price_pcm=data.get("price_pcm"),
            price_pw=data.get("price_pw"),
            original_price_pcm=data.get("original_price_pcm"),
            price_reduction_count=data.get("price_reduction_count", 0),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            postcode=data.get("postcode"),
            postcode_outcode=data.get("postcode_outcode"),
            postcode_incode=data.get("postcode_incode"),
            description=data.get("description"),
            key_features=data.get("key_features", []),
            images=data.get("images", []),
            epc_rating=data.get("epc_rating"),
            council_tax_band=data.get("council_tax_band"),
            agent_name=data.get("agent_name"),
            agent_address=data.get("agent_address"),
            listing_update_reason=data.get("listing_update_reason"),
            available_date=data.get("available_date"),
            scraped_at=scraped_at or datetime.now(),
            first_seen_at=first_seen_at,
            updated_at=updated_at,
            raw_data=data.get("raw_data"),
        )
