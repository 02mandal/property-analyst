"""Geocoding services for walk time calculations."""

from typing import Protocol


class WalkTimeCalculator(Protocol):
    """Protocol for walk time calculators."""

    def calculate(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate walking time between two points in minutes.

        Args:
            lat1, lon1: Origin coordinates
            lat2, lon2: Destination coordinates

        Returns:
            Walking time in minutes
        """
        ...


class HaversineDistanceCalculator:
    """Calculate straight-line distance using Haversine formula."""

    EARTH_RADIUS_KM = 6371

    def calculate(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance in kilometers."""
        import math

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_lat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return self.EARTH_RADIUS_KM * c

    def to_miles(self, km: float) -> float:
        return km * 0.621371


class RadiusWalkTimeEstimator(WalkTimeCalculator):
    """Estimate walk time using straight-line radius + average speed."""

    AVERAGE_WALKING_SPEED_KMH = 5.0

    def __init__(self, calculator: HaversineDistanceCalculator | None = None):
        self._distance_calc = calculator or HaversineDistanceCalculator()

    def calculate(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Estimate walking time in minutes."""
        distance_km = self._distance_calc.calculate(lat1, lon1, lat2, lon2)
        hours = distance_km / self.AVERAGE_WALKING_SPEED_KMH
        return hours * 60


class ORSWalkTimeCalculator(WalkTimeCalculator):
    """Calculate actual walk time using OpenRouteService API."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        self.base_url = "https://api.openrouteservice.org/v2/directions/foot-walking"

    def calculate(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate walking time in minutes using ORS API."""
        import requests

        if not self.api_key:
            raise ValueError("OpenRouteService API key required")

        url = f"{self.base_url}?api_key={self.api_key}"
        payload = {
            "coordinates": [[lon1, lat1], [lon2, lat2]]
        }

        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()

        data = response.json()
        duration_seconds = data["routes"][0]["summary"]["duration"]
        return duration_seconds / 60


def walk_time(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    method: str = "radius",
    **kwargs,
) -> float:
    """
    Calculate walking time between two points.

    Args:
        lat1, lon1: Origin coordinates
        lat2, lon2: Destination coordinates
        method: "radius" (estimate) or "ors" (OpenRouteService)
        **kwargs: Additional arguments for the calculator

    Returns:
        Walking time in minutes
    """
    if method == "radius":
        calculator = RadiusWalkTimeEstimator()
    elif method == "ors":
        calculator = ORSWalkTimeCalculator(**kwargs)
    else:
        raise ValueError(f"Unknown walk time method: {method}")

    return calculator.calculate(lat1, lon1, lat2, lon2)
