# scripts/resolve_latest.py
import os
import requests
from datetime import datetime, timezone
from logger import setup_logger

logger = setup_logger(__name__)

SB_URL = os.environ["SUPABASE_URL"].rstrip("/")
SB_KEY = os.environ["SUPABASE_SERVICE_KEY"]
HDRS  = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

def get_latest_observations():
    logger.info("Fetching latest observations from database...")
    r = requests.get(
        f"{SB_URL}/rest/v1/status_observation"
        "?select=event_id,parsed_status,confidence,observed_at"
        "&order=observed_at.desc",
        headers=HDRS, timeout=60
    )
    r.raise_for_status()
    latest_by_event = {}
    for row in r.json():
        eid = row["event_id"]
        if eid not in latest_by_event:
            latest_by_event[eid] = {
                "status": row.get("parsed_status") or "unknown",
                "conf": row.get("confidence", 0.5)
            }
    logger.info(f"Found latest observations for {len(latest_by_event)} events")
    return latest_by_event

def patch_event(event_id, status, conf):
    # Generate ISO 8601 timestamp for last_checked_at
    now_timestamp = datetime.now(timezone.utc).isoformat()

    r = requests.patch(
        f"{SB_URL}/rest/v1/race_event?event_id=eq.{event_id}",
        headers=HDRS,
        json={
            "general_access_status": status,
            "status_confidence": conf,
            "last_checked_at": now_timestamp,
            "status_source": "official_site",
        },
        timeout=45
    )
    if r.status_code >= 300:
        logger.error(f"Failed to patch event {event_id}: {r.status_code} {r.text}")
        return False
    logger.debug(f"Updated event {event_id} to status '{status}' (confidence: {conf:.2f})")
    return True

def main():
    logger.info("Starting resolver to update event statuses...")
    winners = get_latest_observations()
    updated = 0
    failed = 0
    for eid, v in winners.items():
        if patch_event(eid, v["status"], v["conf"]):
            updated += 1
        else:
            failed += 1
    logger.info(f"✅ Resolver complete. Updated {updated} events, {failed} failures")

if __name__ == "__main__":
    main()
