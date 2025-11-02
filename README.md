# 🏃 RaceRadar

**Automated race availability tracking for runners worldwide.**

RaceRadar tracks registration availability for popular marathons, half marathons, and 10Ks across the UK, Europe, and beyond. Never miss another race registration opening — get real-time updates on when your target races go on sale, sell out, or open waitlists.

---

## 🎯 What Does It Do?

- **Tracks 150+ major races** across 30+ countries
- **Automatically checks** registration status daily
- **Detects status changes**: Open → Sold Out → Waitlist
- **Multilingual keyword detection** for European race websites
- **Nightly automated pipeline** via GitHub Actions

---

## 🏗️ Architecture

```
┌──────────────┐
│  seed_races  │  150+ races in CSV format
│     .csv     │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│  import_seed_csv │  Loads races into Supabase
│       .py        │  Creates race_series + race_event
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ check_availability│  Scrapes registration URLs
│       .py         │  Classifies status (open/sold/waitlist)
└──────┬────────────┘
       │
       ▼
┌──────────────────┐
│  resolve_latest  │  Updates master status
│       .py        │  from latest observations
└──────┬───────────┘
       │
       ▼
  ┌───────────┐
  │  Supabase │  PostgreSQL database
  │   (Live)  │  race_series, race_event, status_observation
  └───────────┘
```

---

## 📦 Database Schema

### Tables

**`race_series`**
Recurring race series (e.g., "London Marathon", "Berlin Marathon")

| Column | Type | Description |
|--------|------|-------------|
| series_id | TEXT (PK) | URL-safe slug (e.g., "london-marathon") |
| name | TEXT | Display name |
| city | TEXT | Host city |
| country | TEXT | Host country |
| distance_km | NUMERIC | Standard distance (21.097 for half) |
| official_url | TEXT | Race homepage |
| timezone | TEXT | IANA timezone |

**`race_event`**
Yearly instances of races

| Column | Type | Description |
|--------|------|-------------|
| event_id | UUID (PK) | Unique event identifier |
| series_id | TEXT (FK) | Links to race_series |
| year | INTEGER | Race year |
| event_local_date | DATE | Race date |
| reg_url | TEXT | Registration URL |
| general_access_status | TEXT | Current status (open/sold_out/waitlist/etc) |
| status_confidence | NUMERIC | Confidence score 0-1 |
| last_checked_at | TIMESTAMPTZ | Last check timestamp |

**`status_observation`**
Historical log of all status checks

| Column | Type | Description |
|--------|------|-------------|
| observation_id | UUID (PK) | Unique observation ID |
| event_id | UUID (FK) | Links to race_event |
| source | TEXT | Source (e.g., "official_site") |
| raw_excerpt | TEXT | Text excerpt from page |
| parsed_status | TEXT | Classified status |
| confidence | NUMERIC | Classification confidence |
| observed_at | TIMESTAMPTZ | Observation timestamp |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Supabase account (free tier works)
- GitHub account (for CI/CD)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/raceradar.git
cd raceradar
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Supabase

1. Create a new project at [supabase.com](https://supabase.com)
2. Run the schema:
   ```bash
   # In Supabase SQL Editor, paste contents of schema.sql
   ```
3. Get your API credentials:
   - Project URL: `https://xxxxx.supabase.co`
   - Service role key: Settings → API → service_role key

### 4. Configure Environment Variables

```bash
export SUPABASE_URL="https://xxxxx.supabase.co"
export SUPABASE_SERVICE_KEY="your-service-role-key"
```

**For persistent config**, add to `~/.bashrc` or `~/.zshrc`:
```bash
echo 'export SUPABASE_URL="https://xxxxx.supabase.co"' >> ~/.bashrc
echo 'export SUPABASE_SERVICE_KEY="your-key"' >> ~/.bashrc
source ~/.bashrc
```

### 5. Import Seed Data

```bash
python scripts/import_seed_csv.py
```

Expected output:
```
2025-01-15 10:30:15 [INFO] __main__: Starting import_seed_csv.py
2025-01-15 10:30:15 [INFO] __main__: Reading seed data from data/seed_races.csv
2025-01-15 10:30:16 [INFO] __main__: Prepared 151 series rows and 151 event rows
2025-01-15 10:30:18 [INFO] __main__: ✅ Upsert complete. race_series affected: 151, race_event affected: 151
```

### 6. Check Availability

```bash
python scripts/check_availability.py
```

This will:
- Fetch all events with status `unknown`, `not_yet_open`, or `open`
- Scrape each registration URL
- Classify status using multilingual keywords
- Post observations to database

### 7. Resolve Latest Statuses

```bash
python scripts/resolve_latest.py
```

Updates the master `race_event.general_access_status` from latest observations.

---

## ⚙️ Configuration

Edit `scripts/config.py` to customize behavior:

```python
# Scraping
scraping.REQUEST_TIMEOUT = 25  # seconds
scraping.SCRAPE_DELAY = 1.0    # delay between requests
scraping.MAX_RETRIES = 3

# Classification
classification.MIN_CONFIDENCE = 0.6  # threshold to update status

# Logging
logging_config.LOG_LEVEL = "INFO"
```

---

## 🤖 Automated Pipeline (GitHub Actions)

The workflow runs nightly at 2 AM UTC:

1. Import seed races (idempotent upsert)
2. Check availability for all active races
3. Resolve latest statuses

### Setup GitHub Secrets

1. Go to your repo → Settings → Secrets and variables → Actions
2. Add two secrets:
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_SERVICE_KEY`: Your service role key

### Manual Trigger

Go to Actions tab → "Nightly Race Data Pipeline" → "Run workflow"

---

## 📊 Querying Data

### Get All Open Races

```sql
SELECT * FROM open_races
ORDER BY event_local_date;
```

### Recently Sold Out

```sql
SELECT * FROM recently_sold_out;
```

### Custom Query via Supabase API

```python
import requests

url = "https://xxxxx.supabase.co/rest/v1/race_event"
headers = {"apikey": "your-anon-key", "Authorization": "Bearer your-anon-key"}
params = {"select": "*", "general_access_status": "eq.open"}

response = requests.get(url, headers=headers, params=params)
races = response.json()
```

---

## 🛠️ Development

### Project Structure

```
raceradar/
├── .github/
│   └── workflows/
│       └── nightly-pipeline.yml   # GitHub Actions workflow
├── data/
│   └── seed_races.csv             # Master race list
├── scripts/
│   ├── config.py                  # Configuration settings
│   ├── logger.py                  # Logging setup
│   ├── import_seed_csv.py         # CSV → Supabase importer
│   ├── check_availability.py      # Web scraper + classifier
│   └── resolve_latest.py          # Status resolver
├── schema.sql                     # Database schema
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

### Adding New Races

Edit `data/seed_races.csv`:

```csv
Event,City,Country,Distance,Date,Link
New York City Marathon,New York City,USA,Marathon,11/3/2024,https://www.nycmarathon.org
```

Then re-run:
```bash
python scripts/import_seed_csv.py
```

### Adding New Keywords

Edit `scripts/check_availability.py`:

```python
KEYS = {
    "open":   [r"enter now", r"register", r"sign up", r"inscr", ...],
    "sold":   [r"sold out", r"entries closed", r"agotado", ...],
    "wait":   [r"waitlist", r"waiting list", ...],
    "notyet": [r"opens", r"opening", r"goes on sale", ...],
}
```

---

## 🐛 Troubleshooting

### "Missing env var" Error

**Problem**: `Missing env var: 'SUPABASE_URL'`

**Solution**:
```bash
export SUPABASE_URL="https://xxxxx.supabase.co"
export SUPABASE_SERVICE_KEY="your-key"
```

### Timestamps Not Updating

**Fixed in v1.0.0** — The `resolve_latest.py` script now correctly generates ISO 8601 timestamps.

### Low Confidence Classifications

Many race sites use JavaScript rendering. Current limitation: basic HTML scraping only.

**Future enhancement**: Use Playwright for JS rendering (see Phase 2 roadmap).

### Date Parsing Errors

The importer now uses country-aware date parsing:
- EU countries default to DD/MM/YYYY
- USA/Canada default to MM/DD/YYYY

Check logs for warnings about unparseable dates.

---

## 🗺️ Roadmap

### Phase 1: Foundation ✅ (Complete)
- [x] Database schema
- [x] CSV import pipeline
- [x] Web scraper with multilingual keywords
- [x] Status resolver
- [x] GitHub Actions CI/CD
- [x] Structured logging
- [x] Configuration management

### Phase 2: Robustness (Next 2 Weeks)
- [ ] Playwright for JavaScript rendering
- [ ] Retry logic with exponential backoff
- [ ] Confidence thresholds and anti-flapping
- [ ] Enhanced timezone coverage
- [ ] Clean CSV data (fix broken URLs, update 2024 dates)

### Phase 3: User-Facing (Next Month)
- [ ] Simple web UI (FastAPI + TailwindCSS)
- [ ] Email alerts for status changes
- [ ] Public API for race data
- [ ] Search and filter by country/distance

### Phase 4: Monetization (2-3 Months)
- [ ] Affiliate links (RunSignup, Active.com)
- [ ] Premium alerts ($5/mo for instant SMS)
- [ ] Training plan upsells ($10-30)
- [ ] Race guide sponsored content
- [ ] B2B API access ($50/mo)

### Phase 5: Advanced (3+ Months)
- [ ] ML-based status classification
- [ ] Predictive "sell-out risk" scores
- [ ] Multi-source verification (Facebook, Twitter, etc)
- [ ] Mobile app (React Native)

---

## 📄 License

MIT License - see LICENSE file for details

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📧 Contact

Questions? Open an issue or reach out at [your-email@example.com]

---

**Built with ❤️ for runners who refuse to miss race day.**
