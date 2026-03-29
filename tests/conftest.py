"""Shared pytest fixtures."""

from datetime import datetime

import pytest

from models.property import PropertyRecord


@pytest.fixture
def sample_property_record() -> PropertyRecord:
    """Minimal property record with required fields only."""
    return PropertyRecord(
        source="test",
        source_url="https://example.com/properties/12345",
    )


@pytest.fixture
def complete_property_record() -> PropertyRecord:
    """Property record with all fields populated."""
    return PropertyRecord(
        source="test",
        source_url="https://example.com/properties/12345",
        display_address="123 Test Street",
        property_type="flat",
        bedrooms=2,
        bathrooms=1,
        size_sqft=750,
        floor_level="2nd",
        furnished="furnished",
        price_pcm=1500,
        price_pw=346,
        original_price_pcm=1600,
        price_reduction_count=1,
        latitude=51.5074,
        longitude=-0.1278,
        postcode="SW1A 1AA",
        postcode_outcode="SW1A",
        postcode_incode="1AA",
        description="A lovely test property",
        key_features=["Feature 1", "Feature 2"],
        images=["https://example.com/img1.jpg"],
        epc_rating="C",
        council_tax_band="C",
        agent_name="Test Agent",
        agent_address="456 Agent Road",
        listing_update_reason="price_change",
        available_date="2024-03-01",
        scraped_at=datetime(2024, 2, 15, 10, 30, 0),
        property_hash="abc123def456",
    )


def make_property(**overrides: object) -> PropertyRecord:
    """Factory function to create PropertyRecord with overrides."""
    defaults: dict[str, object] = {
        "source": "test",
        "source_url": "https://example.com/properties/12345",
    }
    defaults.update(overrides)
    return PropertyRecord(**defaults)  # type: ignore[arg-type]
