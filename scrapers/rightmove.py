"""Rightmove property scraper."""

import json
import logging
import re
from datetime import datetime
from typing import Any

import requests
from bs4 import BeautifulSoup

from models.property import PropertyRecord, generate_property_hash
from models.watchlist import SearchCriteria
from scrapers.base import AbstractScraper

logger = logging.getLogger(__name__)

API_BASE_URL = "https://api.rightmove.com"


class RightmoveAPI:
    """Client for Rightmove's internal search API."""

    @staticmethod
    def build_search_params(criteria: SearchCriteria, page: int = 0) -> dict[str, Any]:
        """Build API search parameters from criteria."""
        params = {
            "locationIdentifier": f"REGION^{criteria.location.replace(' ', '%20')}",
            "numberOfPropertiesRequested": 100,
            "page": page,
        }

        if criteria.min_bedrooms is not None:
            params["minBedrooms"] = criteria.min_bedrooms
        if criteria.max_bedrooms is not None:
            params["maxBedrooms"] = criteria.max_bedrooms

        if criteria.min_price_pcm is not None:
            params["minPrice"] = criteria.min_price_pcm // 4
        if criteria.max_price_pcm is not None:
            params["maxPrice"] = criteria.max_price_pcm // 4

        if criteria.property_types:
            type_map = {"flat": "flats", "house": "houses", "studio": "studios"}
            params["propertyType"] = ",".join(type_map.get(t, t) for t in criteria.property_types)

        if criteria.furnished == "furnished":
            params["furnishTypes"] = "furnished"
        elif criteria.furnished == "unfurnished":
            params["furnishTypes"] = "unfurnished"

        return params

    @staticmethod
    def extract_listing_ids(api_response: dict[str, Any]) -> list[str]:
        """Extract property IDs from API response."""
        listings = api_response.get("properties", [])
        return [str(p["id"]) for p in listings if p.get("id")]


class RightmoveScraper(AbstractScraper):
    """Scraper for Rightmove property listings."""

    name = "rightmove"
    base_url = "https://www.rightmove.co.uk"
    api_base_url = API_BASE_URL

    def search_urls(self, criteria: SearchCriteria) -> list[str]:
        """Generate Rightmove search URLs from criteria."""
        url = f"{self.base_url}/property-to-rent/"

        location = criteria.location.replace(" ", "+")
        url += f"{location}.html"

        params = []

        if criteria.radius_miles and criteria.radius_miles != 0.5:
            params.append(f"radius={criteria.radius_miles}")

        if criteria.min_bedrooms is not None:
            params.append(f"minBedrooms={criteria.min_bedrooms}")

        if criteria.max_bedrooms is not None:
            params.append(f"maxBedrooms={criteria.max_bedrooms}")

        if criteria.min_price_pcm is not None:
            price_pw = criteria.min_price_pcm // 4
            params.append(f"minPrice={price_pw}")

        if criteria.max_price_pcm is not None:
            price_pw = criteria.max_price_pcm // 4
            params.append(f"maxPrice={price_pw}")

        if criteria.property_types:
            type_map = {
                "flat": "flats",
                "house": "houses",
                "studio": "studios",
            }
            prop_types = [type_map.get(t, t) for t in criteria.property_types]
            params.append(f"propertyType={','.join(prop_types)}")

        if criteria.furnished == "furnished":
            params.append("furnishTypes=furnished")
        elif criteria.furnished == "unfurnished":
            params.append("furnishTypes=unfurnished")

        if criteria.available_within_days is not None:
            params.append(f"availableWithin={criteria.available_within_days}")

        params.append("includeLetAgreed=false")
        params.append("_includeLetAgreed=on")

        if params:
            url += "?" + "&".join(params)

        return [url]

    def listings_from_search(self, html: str) -> list[str]:
        """
        Extract listing URLs from search results page.

        Note: Rightmove search pages are JavaScript-rendered (SPA),
        so this will return an empty list with the current implementation.
        For search functionality, consider using Selenium or Rightmove's API.
        """
        soup = BeautifulSoup(html, "lxml")
        urls = []

        for link in soup.find_all("a", class_="propertyLink"):
            href = str(link.get("href", ""))
            if href and "/properties/" in href:
                full_url = href if href.startswith("http") else f"{self.base_url}{href}"
                url_id = full_url.split("/")[-1].split("#")[0]
                urls.append(f"{self.base_url}/properties/{url_id}")

        return list(dict.fromkeys(urls))

    def search_api_url(self, criteria: SearchCriteria, page: int = 0) -> str:
        """Build Rightmove internal API URL for rental search."""
        params = RightmoveAPI.build_search_params(criteria, page)
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.api_base_url}/property-rental-api/search?{query}"

    def listings_from_api(self, criteria: SearchCriteria, page: int = 0) -> list[str]:
        """Fetch listings from Rightmove JSON API."""
        api_url = self.search_api_url(criteria, page)
        domain = api_url.split("/")[2]
        self.rate_limiter.wait(domain)

        try:
            response = self.session.get(api_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            ids = RightmoveAPI.extract_listing_ids(data)
            return [f"{self.base_url}/properties/{id}" for id in ids]
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return []

    def stream_from_api(
        self,
        criteria: SearchCriteria,
        progress: Any = None,
    ) -> list[str]:
        """Fetch all listing URLs from API with pagination."""
        all_ids: list[str] = []
        page = 0
        max_pages = 100

        while page < max_pages:
            if progress:
                progress(page + 1, max_pages)

            ids = self.listings_from_api(criteria, page)
            if not ids:
                break
            all_ids.extend(ids)
            page += 1

        return list(dict.fromkeys(all_ids))

    def parse_listing(self, url: str, html: str) -> PropertyRecord:
        """Parse a Rightmove listing page HTML into a PropertyRecord."""
        data = self._extract_property_data(html)

        images = []
        for img in data.get("images", []):
            if isinstance(img, dict):
                images.append(img.get("url", ""))
            else:
                images.append(str(img))

        epc_rating = None
        epc_graphs = data.get("epcGraphs", [])
        if epc_graphs and isinstance(epc_graphs[0], dict):
            epc_rating = epc_graphs[0].get("rating")

        postcode = data.get("address", {}).get("displayAddress", "")

        sizing = data.get("sizings", [])
        size_sqft = None
        for s in sizing:
            if isinstance(s, dict) and s.get("unit") == "sqft":
                size_sqft = s.get("maximumSize")
                break

        price_pcm_str = data.get("prices", {}).get("primaryPrice", "")
        price_pcm = self._parse_price(price_pcm_str)

        price_pw_str = data.get("prices", {}).get("secondaryPrice", "")
        price_pw = self._parse_price(price_pw_str)

        original_price = data.get("prices", {}).get("message")
        original_price_pcm = None
        if original_price and "was" in original_price.lower():
            match = re.search(r"£[\d,]+", original_price)
            if match:
                original_price_pcm = self._parse_price(match.group(0))

        key_features = data.get("keyFeatures", []) or []

        customer = data.get("customer", {})

        address = data.get("address", {}).get("displayAddress")
        full_postcode = self._extract_postcode(postcode)
        floor_level = self._extract_floor_level(key_features)
        bedrooms = data.get("bedrooms")
        bathrooms = data.get("bathrooms")
        property_hash = generate_property_hash(
            address=address,
            postcode=full_postcode,
            floor=floor_level,
            size=size_sqft,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
        )

        return PropertyRecord(
            source=self.name,
            source_url=url,
            display_address=data.get("address", {}).get("displayAddress"),
            property_type=data.get("text", {}).get("propertyPhrase"),
            bedrooms=data.get("bedrooms"),
            bathrooms=data.get("bathrooms"),
            size_sqft=size_sqft,
            floor_level=self._extract_floor_level(key_features),
            furnished=data.get("lettings", {}).get("furnishType"),
            price_pcm=price_pcm,
            price_pw=price_pw,
            original_price_pcm=original_price_pcm,
            price_reduction_count=data.get("misInfo", {}).get("premiumDisplay", 0),
            latitude=data.get("location", {}).get("latitude"),
            longitude=data.get("location", {}).get("longitude"),
            postcode=full_postcode,
            postcode_outcode=data.get("address", {}).get("outcode"),
            postcode_incode=data.get("address", {}).get("incode"),
            description=data.get("text", {}).get("description"),
            key_features=key_features,
            images=images,
            epc_rating=epc_rating,
            council_tax_band=data.get("livingCosts", {}).get("councilTaxBand"),
            agent_name=customer.get("branchDisplayName"),
            agent_address=customer.get("displayAddress"),
            listing_update_reason=data.get("listingHistory", {}).get("listingUpdateReason"),
            available_date=data.get("lettings", {}).get("letAvailableDate"),
            scraped_at=datetime.now(),
            property_hash=property_hash,
            raw_data=data,
        )

    def _extract_property_data(self, html: str) -> dict[str, Any]:
        """Extract the propertyData JSON from HTML page."""
        start_idx = html.find('"propertyData":')
        if start_idx == -1:
            raise ValueError("Could not find propertyData in page")

        brace_start = html.find("{", start_idx)
        if brace_start == -1:
            raise ValueError("Could not find JSON object start")

        depth = 0
        i = brace_start
        while i < len(html):
            if html[i] == "{":
                depth += 1
            elif html[i] == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1

        return json.loads(html[brace_start:i + 1])

    def _parse_price(self, price_str: str) -> int | None:
        """Parse price string like '£3,469 pcm' to pence (int)."""
        if not price_str:
            return None

        match = re.search(r"£([\d,]+)", price_str)
        if match:
            num_str = match.group(1).replace(",", "")
            return int(num_str) * 100

        return None

    def _extract_postcode(self, address: str) -> str | None:
        """Extract full postcode from address string."""
        match = re.search(r"[A-Z]{1,2}[0-9][0-9A-Z]?\s*[0-9][A-Z]{2}", address.upper())
        if match:
            return match.group(0).replace(" ", "")
        return None

    def _extract_floor_level(self, features: list[str]) -> str | None:
        """Extract floor level from key features."""
        for feature in features:
            match = re.search(r"[Ff]loor\s+(\d+|[A-Za-z]+)", feature)
            if match:
                return match.group(0)
        return None
