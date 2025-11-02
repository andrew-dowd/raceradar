# scripts/import_seed_csv.py
import os
import csv
import requests
from slugify import slugify
from logger import setup_logger
from config import TIMEZONE_MAP, EU_COUNTRIES

logger = setup_logger(__name__)
logger.info("Starting import_seed_csv.py")

# ---- Supabase config (from your Supabase project) ----
try:
    SB_URL = os.environ["SUPABASE_URL"].rstrip("/")
    SB_KEY = os.environ["SUPABASE_SERVICE_KEY"]
except KeyError as e:
    logger.error(f"Missing environment variable: {e}")
    raise SystemExit(f"Missing env var: {e}. Did you run 'export SUPABASE_URL=...' and 'export SUPABASE_SERVICE_KEY=...'?")

# Important: Prefer header so PostgREST returns JSON on upsert
HDRS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation,resolution=merge-duplicates"
}

SERIES_URL = f"{SB_URL}/rest/v1/race_series"
EVENTS_URL = f"{SB_URL}/rest/v1/race_event"

def upsert(url: str, rows: list, on_conflict: str | None = None):
    """Upsert rows; tolerate empty/204 responses; return parsed JSON or []."""
    if not rows:
        return []
    params = {"on_conflict": on_conflict} if on_conflict else {}
    r = requests.post(url, headers=HDRS, json=rows, params=params, timeout=45)
    if r.status_code >= 300:
        logger.error(f"Supabase error {r.status_code}: {r.text}")
        raise SystemExit(f"Supabase error {r.status_code}: {r.text}")
    # Some responses are empty (201/204). Avoid json() crash.
    if not (r.text or "").strip():
        return []
    try:
        return r.json()
    except Exception:
        logger.warning(f"Non-JSON response received: {r.status_code}, {(r.text or '')[:200]}")
        return []

def parse_distance_km(dist_text: str | None):
    if not dist_text:
        return None
    t = dist_text.lower().strip()
    if "half" in t:
        return 21.097
    if "10k" in t or t == "10":
        return 10
    if "5k" in t or t == "5":
        return 5
    if "marathon" in t and "half" not in t:
        return 42.195
    return None

def parse_date_to_yyyy_mm_dd(date_str: str | None, country: str = ""):
    """
    Parse date with country-aware format preference.

    Args:
        date_str: Date string in format 'm/d/yyyy', 'd/m/yyyy', or with dashes
        country: Country name to determine date format preference

    Returns:
        'YYYY-MM-DD' formatted string or None if parsing fails
    """
    if not date_str:
        return None

    s = date_str.strip().replace("-", "/")
    parts = [p.strip() for p in s.split("/")]
    if len(parts) != 3:
        return None

    a, b, y = parts

    # EU countries prefer DD/MM/YYYY format
    prefer_eu = country in EU_COUNTRIES

    try:
        if prefer_eu:
            # Try EU format first: DD/MM/YYYY
            d, m, year = int(a), int(b), int(y)
        else:
            # Try US format first: MM/DD/YYYY
            m, d, year = int(a), int(b), int(y)

        # Validate month and day ranges
        if 1 <= m <= 12 and 1 <= d <= 31:
            return f"{year:04d}-{m:02d}-{d:02d}"
    except (ValueError, IndexError):
        pass

    # If primary format failed, try the opposite format
    try:
        if prefer_eu:
            # Try US format: MM/DD/YYYY
            m, d, year = int(a), int(b), int(y)
        else:
            # Try EU format: DD/MM/YYYY
            d, m, year = int(a), int(b), int(y)

        if 1 <= m <= 12 and 1 <= d <= 31:
            logger.debug(f"Date '{date_str}' parsed using fallback format for country '{country}'")
            return f"{year:04d}-{m:02d}-{d:02d}"
    except (ValueError, IndexError):
        pass

    logger.warning(f"Could not parse date '{date_str}' for country '{country}'")
    return None

def main():
    seed_path = "data/seed_races.csv"
    if not os.path.exists(seed_path):
        logger.error(f"Missing CSV at {seed_path}")
        raise SystemExit(f"Missing CSV at {seed_path}. Put your file there and try again.")

    logger.info(f"Reading seed data from {seed_path}")
    series_rows, event_rows = [], []

    with open(seed_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"Event", "City", "Country", "Distance", "Date", "Link"}
        if set(reader.fieldnames or []) < required:
            logger.error(f"CSV missing required columns. Found: {reader.fieldnames}")
            raise SystemExit(
                "CSV headers must be exactly: Event,City,Country,Distance,Date,Link\n"
                f"Found: {reader.fieldnames}"
            )

        for row in reader:
            name = (row.get("Event") or "").strip()
            if not name:
                continue  # skip blank lines

            city = (row.get("City") or "").strip() or None
            country = (row.get("Country") or "").strip() or None
            dist_text = (row.get("Distance") or "").strip()
            link = (row.get("Link") or "").strip() or None
            date = (row.get("Date") or "").strip() or None

            distance_km = parse_distance_km(dist_text)
            series_id = slugify(name)
            tz = TIMEZONE_MAP.get(country or "", None)

            series_rows.append(
                {
                    "series_id": series_id,
                    "name": name,
                    "city": city,
                    "country": country,
                    "distance_km": distance_km,
                    "official_url": link,
                    "timezone": tz,
                }
            )

            event_local_date = parse_date_to_yyyy_mm_dd(date, country or "")
            if event_local_date:
                year = int(event_local_date[:4])
            else:
                # If date missing/unparsable, default to 2025; you can adjust later.
                year = 2025

            event_rows.append(
                {
                    "series_id": series_id,
                    "year": year,
                    "event_local_date": event_local_date,
                    "event_timezone": tz,
                    "reg_url": link,
                    "general_access_status": "unknown",
                }
            )

    logger.info(f"Prepared {len(series_rows)} series rows and {len(event_rows)} event rows")

    # Bulk upserts (idempotent)
    logger.info("Upserting race series...")
    s_res = upsert(SERIES_URL, series_rows, on_conflict="series_id")
    logger.info("Upserting race events...")
    e_res = upsert(EVENTS_URL, event_rows, on_conflict="series_id,year")

    logger.info(f"✅ Upsert complete. race_series affected: {len(s_res) if s_res is not None else 0}, "
                f"race_event affected: {len(e_res) if e_res is not None else 0}")
    logger.info("Import completed successfully")

if __name__ == "__main__":
    main()