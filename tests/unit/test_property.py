"""Tests for PropertyRecord model."""

from datetime import datetime

from models.property import PropertyRecord, generate_property_hash


class TestGeneratePropertyHash:
    def test_hash_with_all_fields(self):
        result = generate_property_hash(
            address="123 Test Street",
            postcode="SW1A 1AA",
            floor="2nd",
            size=750,
            bedrooms=2,
            bathrooms=1,
        )
        assert result is not None
        assert len(result) == 16
        assert result.isalnum()

    def test_hash_with_address_only(self):
        result = generate_property_hash(
            address="123 Test Street",
            postcode=None,
            floor=None,
            size=None,
            bedrooms=None,
            bathrooms=None,
        )
        assert result is not None
        assert len(result) == 16

    def test_hash_with_postcode_only(self):
        result = generate_property_hash(
            address=None,
            postcode="SW1A 1AA",
            floor=None,
            size=None,
            bedrooms=None,
            bathrooms=None,
        )
        assert result is not None
        assert len(result) == 16

    def test_hash_with_neither_address_nor_postcode(self):
        result = generate_property_hash(
            address=None,
            postcode=None,
            floor="2nd",
            size=750,
            bedrooms=2,
            bathrooms=1,
        )
        assert result is None

    def test_hash_empty_strings(self):
        result = generate_property_hash(
            address="",
            postcode="",
            floor=None,
            size=None,
            bedrooms=None,
            bathrooms=None,
        )
        assert result is None

    def test_hash_address_normalization(self):
        hash1 = generate_property_hash(
            address="123 TEST STREET",
            postcode="sw1a 1aa",
            floor=None,
            size=None,
            bedrooms=None,
            bathrooms=None,
        )
        hash2 = generate_property_hash(
            address="123 test street",
            postcode="SW1A 1AA",
            floor=None,
            size=None,
            bedrooms=None,
            bathrooms=None,
        )
        assert hash1 == hash2

    def test_hash_different_addresss_produce_different_hashes(self):
        hash1 = generate_property_hash(
            address="123 Test Street",
            postcode="SW1A 1AA",
            floor=None,
            size=None,
            bedrooms=None,
            bathrooms=None,
        )
        hash2 = generate_property_hash(
            address="124 Test Street",
            postcode="SW1A 1AA",
            floor=None,
            size=None,
            bedrooms=None,
            bathrooms=None,
        )
        assert hash1 != hash2

    def test_hash_different_bedrooms_produce_different_hashes(self):
        hash1 = generate_property_hash(
            address="123 Test Street",
            postcode="SW1A 1AA",
            floor=None,
            size=None,
            bedrooms=2,
            bathrooms=None,
        )
        hash2 = generate_property_hash(
            address="123 Test Street",
            postcode="SW1A 1AA",
            floor=None,
            size=None,
            bedrooms=3,
            bathrooms=None,
        )
        assert hash1 != hash2

    def test_hash_consistency_same_inputs(self):
        hash1 = generate_property_hash(
            address="123 Test Street",
            postcode="SW1A 1AA",
            floor="2nd",
            size=750,
            bedrooms=2,
            bathrooms=1,
        )
        hash2 = generate_property_hash(
            address="123 Test Street",
            postcode="SW1A 1AA",
            floor="2nd",
            size=750,
            bedrooms=2,
            bathrooms=1,
        )
        assert hash1 == hash2


class TestPropertyRecordId:
    def test_id_from_valid_url(self, sample_property_record):
        assert sample_property_record.id == "12345"

    def test_id_from_url_with_different_path(self):
        record = PropertyRecord(
            source="test",
            source_url="https://example.com/properties/67890",
        )
        assert record.id == "67890"

    def test_id_from_url_without_number(self):
        record = PropertyRecord(
            source="test",
            source_url="https://example.com/some/path",
        )
        assert record.id == ""

    def test_id_from_empty_url(self):
        record = PropertyRecord(
            source="test",
            source_url="",
        )
        assert record.id == ""


class TestPropertyRecordEquality:
    def test_equal_when_hash_and_price_match(self):
        record1 = PropertyRecord(
            source="test",
            source_url="https://example.com/properties/1",
            property_hash="abc123",
            price_pcm=1500,
        )
        record2 = PropertyRecord(
            source="test",
            source_url="https://example.com/properties/2",
            property_hash="abc123",
            price_pcm=1500,
        )
        assert record1 == record2

    def test_not_equal_when_hash_differs(self):
        record1 = PropertyRecord(
            source="test",
            source_url="https://example.com/properties/1",
            property_hash="abc123",
            price_pcm=1500,
        )
        record2 = PropertyRecord(
            source="test",
            source_url="https://example.com/properties/2",
            property_hash="def456",
            price_pcm=1500,
        )
        assert record1 != record2

    def test_not_equal_when_price_differs(self):
        record1 = PropertyRecord(
            source="test",
            source_url="https://example.com/properties/1",
            property_hash="abc123",
            price_pcm=1500,
        )
        record2 = PropertyRecord(
            source="test",
            source_url="https://example.com/properties/2",
            property_hash="abc123",
            price_pcm=1600,
        )
        assert record1 != record2

    def test_equal_to_non_propertyrecord_returns_not_implemented(self):
        record = PropertyRecord(
            source="test",
            source_url="https://example.com/properties/1",
        )
        assert record.__eq__("not a property") is NotImplemented


class TestPropertyRecordHash:
    def test_hash_consistent_with_equality(self):
        record1 = PropertyRecord(
            source="test",
            source_url="https://example.com/properties/1",
            property_hash="abc123",
            price_pcm=1500,
        )
        record2 = PropertyRecord(
            source="test",
            source_url="https://example.com/properties/2",
            property_hash="abc123",
            price_pcm=1500,
        )
        assert hash(record1) == hash(record2)

    def test_hash_different_when_not_equal(self):
        record1 = PropertyRecord(
            source="test",
            source_url="https://example.com/properties/1",
            property_hash="abc123",
            price_pcm=1500,
        )
        record2 = PropertyRecord(
            source="test",
            source_url="https://example.com/properties/2",
            property_hash="def456",
            price_pcm=1500,
        )
        assert hash(record1) != hash(record2)


class TestPropertyRecordSerialization:
    def test_to_dict_includes_required_fields(self, sample_property_record):
        data = sample_property_record.to_dict()
        assert data["source"] == "test"
        assert data["source_url"] == "https://example.com/properties/12345"
        assert data["id"] == "12345"
        assert data["status"] == "active"

    def test_to_dict_includes_all_fields(self, complete_property_record):
        data = complete_property_record.to_dict()
        assert data["display_address"] == "123 Test Street"
        assert data["property_type"] == "flat"
        assert data["bedrooms"] == 2
        assert data["bathrooms"] == 1
        assert data["size_sqft"] == 750
        assert data["floor_level"] == "2nd"
        assert data["furnished"] == "furnished"
        assert data["price_pcm"] == 1500
        assert data["price_pw"] == 346
        assert data["original_price_pcm"] == 1600
        assert data["price_reduction_count"] == 1
        assert data["latitude"] == 51.5074
        assert data["longitude"] == -0.1278
        assert data["postcode"] == "SW1A 1AA"
        assert data["postcode_outcode"] == "SW1A"
        assert data["postcode_incode"] == "1AA"
        assert data["description"] == "A lovely test property"
        assert data["key_features"] == ["Feature 1", "Feature 2"]
        assert data["images"] == ["https://example.com/img1.jpg"]
        assert data["epc_rating"] == "C"
        assert data["council_tax_band"] == "C"
        assert data["agent_name"] == "Test Agent"
        assert data["agent_address"] == "456 Agent Road"
        assert data["listing_update_reason"] == "price_change"
        assert data["available_date"] == "2024-03-01"
        assert data["property_hash"] == "abc123def456"

    def test_from_dict_roundtrip(self, complete_property_record):
        original_data = complete_property_record.to_dict()
        restored = PropertyRecord.from_dict(original_data)
        assert restored.source == complete_property_record.source
        assert restored.source_url == complete_property_record.source_url
        assert restored.display_address == complete_property_record.display_address
        assert restored.price_pcm == complete_property_record.price_pcm
        assert restored.property_hash == complete_property_record.property_hash

    def test_from_dict_handles_iso_datetime_strings(self):
        data = {
            "source": "test",
            "source_url": "https://example.com/properties/1",
            "scraped_at": "2024-02-15T10:30:00",
            "first_seen_at": "2024-02-14T08:00:00",
            "updated_at": "2024-02-15T12:00:00",
        }
        record = PropertyRecord.from_dict(data)
        assert record.scraped_at == datetime(2024, 2, 15, 10, 30, 0)
        assert record.first_seen_at == datetime(2024, 2, 14, 8, 0, 0)
        assert record.updated_at == datetime(2024, 2, 15, 12, 0, 0)

    def test_from_dict_handles_missing_optional_fields(self):
        data = {
            "source": "test",
            "source_url": "https://example.com/properties/1",
        }
        record = PropertyRecord.from_dict(data)
        assert record.status == "active"
        assert record.price_reduction_count == 0
        assert record.key_features == []
        assert record.images == []
        assert record.scraped_at is not None

    def test_from_dict_handles_null_datetime_strings(self):
        data = {
            "source": "test",
            "source_url": "https://example.com/properties/1",
            "scraped_at": None,
            "first_seen_at": None,
            "updated_at": None,
        }
        record = PropertyRecord.from_dict(data)
        assert record.scraped_at is not None
        assert record.first_seen_at is None
        assert record.updated_at is None

    def test_to_dict_serializes_datetime(self, complete_property_record):
        data = complete_property_record.to_dict()
        assert data["scraped_at"] == "2024-02-15T10:30:00"
        assert data["first_seen_at"] is None
        assert data["updated_at"] is None
