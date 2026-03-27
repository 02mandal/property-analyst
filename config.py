"""Configuration for property scraper."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class RetryConfig:
    """Retry behavior configuration."""
    max_retries: int = 3
    base_delay: float = 2.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: float = 0.5


@dataclass
class RateLimitConfig:
    """Rate limiting configuration per source."""
    min_delay: float = 2.0
    max_delay: float = 10.0
    jitter: float = 0.5


@dataclass
class DatabaseConfig:
    """Database configuration."""
    path: Path = Path("data/properties.db")
    duckdb_path: Path = Path("data/analytics.duckdb")


@dataclass
class Config:
    """Main application configuration."""
    database: DatabaseConfig = DatabaseConfig()
    retry: RetryConfig = RetryConfig()
    rate_limit: RateLimitConfig = RateLimitConfig()
    
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"


DEFAULT_CONFIG = Config()
