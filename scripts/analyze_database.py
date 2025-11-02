# scripts/analyze_database.py
"""
Analyze the current state of the RaceRadar database.
Shows what data we have, quality metrics, and gaps.
"""
import os
import requests
from collections import Counter
from datetime import datetime

SB_URL = os.environ["SUPABASE_URL"].rstrip("/")
SB_KEY = os.environ["SUPABASE_SERVICE_KEY"]
HDRS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
}

def get_data(table, select="*", filters=""):
    url = f"{SB_URL}/rest/v1/{table}?select={select}{filters}"
    r = requests.get(url, headers=HDRS, timeout=60)
    r.raise_for_status()
    return r.json()

def analyze():
    print("=" * 80)
    print("🔍 RACERADAR DATABASE ANALYSIS")
    print("=" * 80)
    print()

    # ========== RACE SERIES ==========
    print("📊 RACE SERIES")
    print("-" * 80)
    series = get_data("race_series")
    print(f"Total race series: {len(series)}")

    # Countries
    countries = Counter(s.get('country') for s in series)
    print(f"\n📍 Countries represented: {len(countries)}")
    print("   Top 10 countries:")
    for country, count in countries.most_common(10):
        print(f"     • {country}: {count} races")

    # Distances
    distances = Counter(s.get('distance_km') for s in series)
    print(f"\n📏 Distance breakdown:")
    distance_names = {
        42.195: "Marathon",
        21.097: "Half Marathon",
        10.0: "10K",
        5.0: "5K",
        None: "Unknown"
    }
    for dist, count in sorted(distances.items(), key=lambda x: (x[0] or 0, x[1]), reverse=True):
        name = distance_names.get(dist, f"{dist}km")
        print(f"     • {name}: {count} races")

    # Timezones
    no_timezone = sum(1 for s in series if not s.get('timezone'))
    print(f"\n🌍 Timezone coverage:")
    print(f"     • With timezone: {len(series) - no_timezone}")
    print(f"     • Missing timezone: {no_timezone}")

    # URLs
    no_url = sum(1 for s in series if not s.get('official_url'))
    print(f"\n🔗 Official URLs:")
    print(f"     • With URL: {len(series) - no_url}")
    print(f"     • Missing URL: {no_url}")

    print()

    # ========== RACE EVENTS ==========
    print("=" * 80)
    print("🏃 RACE EVENTS")
    print("-" * 80)
    events = get_data("race_event")
    print(f"Total race events: {len(events)}")

    # Years
    years = Counter(e.get('year') for e in events)
    print(f"\n📅 Events by year:")
    for year in sorted(years.keys()):
        print(f"     • {year}: {years[year]} events")

    # Dates
    no_date = sum(1 for e in events if not e.get('event_local_date'))
    print(f"\n📆 Event dates:")
    print(f"     • With date: {len(events) - no_date}")
    print(f"     • Missing date: {no_date}")

    # Registration URLs
    no_reg_url = sum(1 for e in events if not e.get('reg_url'))
    broken_reg_url = sum(1 for e in events if e.get('reg_url') and not e.get('reg_url').startswith('http'))
    valid_reg_url = len(events) - no_reg_url - broken_reg_url
    print(f"\n🔗 Registration URLs:")
    print(f"     • Valid URLs (https://...): {valid_reg_url}")
    print(f"     • Broken URLs (no https://): {broken_reg_url}")
    print(f"     • Missing URLs (NULL): {no_reg_url}")

    # Status distribution
    statuses = Counter(e.get('general_access_status') for e in events)
    print(f"\n📊 Registration status:")
    for status, count in statuses.most_common():
        print(f"     • {status}: {count} events")

    # Confidence scores
    confidences = [e.get('status_confidence', 0) for e in events if e.get('status_confidence') is not None]
    if confidences:
        avg_conf = sum(confidences) / len(confidences)
        low_conf = sum(1 for c in confidences if c < 0.6)
        print(f"\n🎯 Confidence scores:")
        print(f"     • Average confidence: {avg_conf:.2f}")
        print(f"     • Low confidence (<0.6): {low_conf} events")
        print(f"     • High confidence (≥0.6): {len(confidences) - low_conf} events")

    # Last checked
    checked = [e for e in events if e.get('last_checked_at')]
    never_checked = len(events) - len(checked)
    print(f"\n⏰ Last checked:")
    print(f"     • Checked at least once: {len(checked)}")
    print(f"     • Never checked: {never_checked}")

    if checked:
        # Most recent check
        most_recent = max(checked, key=lambda e: e.get('last_checked_at', ''))
        print(f"     • Most recent check: {most_recent.get('last_checked_at', 'N/A')[:19]}")

    print()

    # ========== STATUS OBSERVATIONS ==========
    print("=" * 80)
    print("📝 STATUS OBSERVATIONS")
    print("-" * 80)
    obs = get_data("status_observation")
    print(f"Total observations: {len(obs)}")

    if obs:
        # Observations by event
        events_observed = len(set(o.get('event_id') for o in obs))
        avg_obs_per_event = len(obs) / events_observed if events_observed > 0 else 0
        print(f"\n📊 Observation coverage:")
        print(f"     • Events with observations: {events_observed}")
        print(f"     • Avg observations per event: {avg_obs_per_event:.1f}")

        # Status distribution
        obs_statuses = Counter(o.get('parsed_status') for o in obs)
        print(f"\n📊 Observed statuses:")
        for status, count in obs_statuses.most_common():
            print(f"     • {status}: {count} observations")

        # Confidence distribution
        obs_confidences = [o.get('confidence', 0) for o in obs if o.get('confidence') is not None]
        if obs_confidences:
            avg_obs_conf = sum(obs_confidences) / len(obs_confidences)
            print(f"\n🎯 Observation confidence:")
            print(f"     • Average: {avg_obs_conf:.2f}")
            low_conf_obs = sum(1 for c in obs_confidences if c < 0.6)
            print(f"     • Low confidence (<0.6): {low_conf_obs} ({low_conf_obs/len(obs_confidences)*100:.1f}%)")

        # Sources
        sources = Counter(o.get('source') for o in obs)
        print(f"\n📍 Observation sources:")
        for source, count in sources.most_common():
            print(f"     • {source}: {count} observations")

        # Recency
        most_recent_obs = max(obs, key=lambda o: o.get('observed_at', ''))
        oldest_obs = min(obs, key=lambda o: o.get('observed_at', ''))
        print(f"\n⏰ Observation timeline:")
        print(f"     • Oldest: {oldest_obs.get('observed_at', 'N/A')[:19]}")
        print(f"     • Newest: {most_recent_obs.get('observed_at', 'N/A')[:19]}")

    print()

    # ========== DATA QUALITY ISSUES ==========
    print("=" * 80)
    print("⚠️  DATA QUALITY ISSUES")
    print("-" * 80)

    issues = []

    # Past dates
    today = datetime.now().date()
    past_events = [e for e in events if e.get('event_local_date') and
                   datetime.fromisoformat(e['event_local_date']).date() < today]
    if past_events:
        issues.append(f"• {len(past_events)} events have dates in the past (need 2025/2026 updates)")

    # Broken URLs
    if broken_reg_url > 0:
        issues.append(f"• {broken_reg_url} events have broken registration URLs (no https://)")

    # Missing data
    if no_date > 0:
        issues.append(f"• {no_date} events missing event dates")
    if no_timezone > 0:
        issues.append(f"• {no_timezone} series missing timezone info")

    # Low confidence
    if confidences:
        if low_conf > 0:
            issues.append(f"• {low_conf} events with low confidence status ({low_conf/len(events)*100:.1f}%)")

    # Unknown status
    unknown_status = statuses.get('unknown', 0)
    if unknown_status > 0:
        issues.append(f"• {unknown_status} events with 'unknown' status ({unknown_status/len(events)*100:.1f}%)")

    if issues:
        for issue in issues:
            print(f"   {issue}")
    else:
        print("   ✅ No major data quality issues detected!")

    print()

    # ========== SUMMARY & RECOMMENDATIONS ==========
    print("=" * 80)
    print("📋 SUMMARY & RECOMMENDATIONS")
    print("-" * 80)

    print("\n✅ What's Working Well:")
    print(f"   • {len(series)} race series imported successfully")
    print(f"   • {valid_reg_url} events have valid registration URLs ({valid_reg_url/len(events)*100:.1f}%)")
    print(f"   • {events_observed if obs else 0} events have been checked for availability")
    if confidences and avg_conf >= 0.7:
        print(f"   • Average confidence score is good ({avg_conf:.2f})")

    print("\n❌ What's Missing/Needs Improvement:")
    if broken_reg_url > 0:
        print(f"   • {broken_reg_url} broken URLs need fixing")
    if len(past_events) > 0:
        print(f"   • {len(past_events)} events with past dates need 2025/2026 updates")
    if unknown_status > 10:
        print(f"   • {unknown_status} events still have 'unknown' status - need more checks")
    if never_checked > 0:
        print(f"   • {never_checked} events have never been checked")

    print("\n🎯 Recommended Next Steps:")
    print("   1. Fix remaining broken URLs (run fix_urls.py with more races)")
    print("   2. Update past event dates to 2025/2026")
    print("   3. Re-run availability checker to reduce 'unknown' statuses")
    print("   4. Add more multilingual keywords for better classification")
    print("   5. Implement confidence thresholds (only update if confidence > 0.6)")

    print()
    print("=" * 80)

if __name__ == "__main__":
    analyze()
