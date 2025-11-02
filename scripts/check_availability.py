# scripts/check_availability.py
import os
import re
import time
import requests
from bs4 import BeautifulSoup
from logger import setup_logger

logger = setup_logger(__name__)

# ---- Supabase config ----
try:
    SB_URL = os.environ["SUPABASE_URL"].rstrip("/")
    SB_KEY = os.environ["SUPABASE_SERVICE_KEY"]
    logger.info("Supabase configuration loaded")
except KeyError as e:
    logger.error(f"Missing environment variable: {e}")
    raise SystemExit(f"Missing env var: {e}. Did you export SUPABASE_URL and SUPABASE_SERVICE_KEY?")

HDRS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

GET_EVENTS = (
    f"{SB_URL}/rest/v1/race_event"
    "?select=event_id,series_id,year,reg_url"
    "&general_access_status=in.(unknown,not_yet_open,open)"
    "&reg_url=not.is.null"
)

POST_OBS = f"{SB_URL}/rest/v1/status_observation"

KEYS = {
    "open":   [r"enter now", r"register", r"sign up", r"inscr", r"iscriv", r"inscript", r"anmelden"],
    "sold":   [r"sold out", r"entries closed", r"agotado", r"complet", r"ausgebucht"],
    "wait":   [r"waitlist", r"waiting list", r"lista de espera"],
    "notyet": [r"opens", r"opening", r"goes on sale", r"abre"],
}

UA = {"User-Agent": "Mozilla/5.0 (RaceRadarBot/0.1)"}

def classify(text: str):
    t = text.lower()
    def m(keys): return any(re.search(p, t) for p in keys)
    if m(KEYS["sold"]):   return "sold_out", 0.95
    if m(KEYS["wait"]):   return "waitlist", 0.80
    if m(KEYS["notyet"]) and not m(KEYS["open"]):
        return "not_yet_open", 0.70
    if m(KEYS["open"]):   return "open", 0.80
    return "unknown", 0.40

def post_obs(event_id: str, url: str, status: str, conf: float, excerpt: str):
    r = requests.post(
        POST_OBS, headers=HDRS, json={
            "event_id": event_id,
            "source": "official_site",
            "raw_excerpt": excerpt[:500],
            "parsed_status": status,
            "confidence": conf,
            "url": url,
        },
        timeout=45
    )
    if r.status_code >= 300:
        logger.error(f"Failed to post observation for {event_id}: {r.status_code} {r.text}")

def main():
    logger.info("Fetching events to check...")
    resp = requests.get(GET_EVENTS, headers=HDRS, timeout=45)
    resp.raise_for_status()
    events = resp.json()
    logger.info(f"Retrieved {len(events)} events to verify")

    checked = 0
    failed = 0
    for ev in events:
        url = ev.get("reg_url")
        if not url:
            continue
        try:
            html = requests.get(url, headers=UA, timeout=25).text
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(" ", strip=True)
            status, conf = classify(text)
            post_obs(ev["event_id"], url, status, conf, text[:300])
            logger.debug(f"Checked {ev.get('series_id')}/{ev.get('year')}: {status} (confidence: {conf:.2f})")
            checked += 1
            if checked % 10 == 0:
                logger.info(f"Progress: checked {checked}/{len(events)} events")
            time.sleep(1.0)  # be polite
        except Exception as e:
            failed += 1
            logger.warning(f"Failed to fetch {ev.get('series_id')}/{ev.get('year')}: {e}")

    logger.info(f"✅ Completed. Successfully checked {checked} events, {failed} failures")

if __name__ == "__main__":
    main()