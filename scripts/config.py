# scripts/config.py
"""
Centralized configuration for RaceRadar scripts.
Adjust these values to tune the behavior of the pipeline.
"""
from dataclasses import dataclass


@dataclass
class ScrapingConfig:
    """Configuration for web scraping behavior."""
    # HTTP request timeout in seconds
    REQUEST_TIMEOUT: int = 25

    # Delay between requests in seconds (be polite to race websites)
    SCRAPE_DELAY: float = 1.0

    # Maximum retry attempts for failed requests
    MAX_RETRIES: int = 3

    # User agent string for HTTP requests
    USER_AGENT: str = "Mozilla/5.0 (RaceRadarBot/1.0; +https://github.com/yourusername/raceradar)"


@dataclass
class ClassificationConfig:
    """Configuration for status classification."""
    # Minimum confidence threshold to update event status (0.0 - 1.0)
    MIN_CONFIDENCE: float = 0.6

    # Time window in hours for detecting status flip-flopping
    ANTI_FLAP_WINDOW_HOURS: int = 24

    # Maximum number of different statuses allowed in the anti-flap window
    MAX_STATUS_CHANGES: int = 2


@dataclass
class DatabaseConfig:
    """Configuration for database operations."""
    # Batch size for bulk operations
    BATCH_SIZE: int = 50

    # Default timeout for Supabase API calls in seconds
    DB_TIMEOUT: int = 45


@dataclass
class LoggingConfig:
    """Configuration for logging."""
    # Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_LEVEL: str = "INFO"

    # Whether to include debug logs for individual event checks
    LOG_INDIVIDUAL_CHECKS: bool = False


# Singleton instances
scraping = ScrapingConfig()
classification = ClassificationConfig()
database = DatabaseConfig()
logging_config = LoggingConfig()


# Timezone mapping (extend as needed)
TIMEZONE_MAP = {
    "UK": "Europe/London",
    "United Kingdom": "Europe/London",
    "England": "Europe/London",
    "Ireland": "Europe/Dublin",
    "Northern Ireland": "Europe/London",
    "Germany": "Europe/Berlin",
    "France": "Europe/Paris",
    "Spain": "Europe/Madrid",
    "Portugal": "Europe/Lisbon",
    "Italy": "Europe/Rome",
    "Netherlands": "Europe/Amsterdam",
    "Denmark": "Europe/Copenhagen",
    "Sweden": "Europe/Stockholm",
    "Norway": "Europe/Oslo",
    "Finland": "Europe/Helsinki",
    "Belgium": "Europe/Brussels",
    "Austria": "Europe/Vienna",
    "Switzerland": "Europe/Zurich",
    "Turkey": "Europe/Istanbul",
    "Greece": "Europe/Athens",
    "Poland": "Europe/Warsaw",
    "Czech Republic": "Europe/Prague",
    "Hungary": "Europe/Budapest",
    "Romania": "Europe/Bucharest",
    "Slovenia": "Europe/Ljubljana",
    "Estonia": "Europe/Tallinn",
    "Bosnia & Herzegovina": "Europe/Sarajevo",
    "Luxembourg": "Europe/Luxembourg",
    # Add more as needed
    "USA": "America/New_York",  # Default; specific cities vary
    "Canada": "America/Toronto",  # Default; specific cities vary
    "Australia": "Australia/Sydney",  # Default; specific cities vary
    "Japan": "Asia/Tokyo",
    "China": "Asia/Shanghai",
    "Singapore": "Asia/Singapore",
    "South Korea": "Asia/Seoul",
    "Israel": "Asia/Jerusalem",
    "UAE": "Asia/Dubai",
    "South Africa": "Africa/Johannesburg",
    "Morocco": "Africa/Casablanca",
    "Argentina": "America/Argentina/Buenos_Aires",
    "Mexico": "America/Mexico_City",
    "Taiwan": "Asia/Taipei",
    "Indonesia": "Asia/Jakarta",
    "Thailand": "Asia/Bangkok",
    "New Zealand": "Pacific/Auckland",
}

# EU countries for date format preference (DD/MM/YYYY vs MM/DD/YYYY)
EU_COUNTRIES = {
    "UK", "United Kingdom", "England", "Ireland", "Northern Ireland",
    "Germany", "France", "Spain", "Portugal", "Italy", "Netherlands",
    "Denmark", "Sweden", "Norway", "Finland", "Belgium", "Austria",
    "Switzerland", "Turkey", "Greece", "Poland", "Czech Republic",
    "Hungary", "Romania", "Slovenia", "Estonia", "Bosnia & Herzegovina",
    "Luxembourg",
}
