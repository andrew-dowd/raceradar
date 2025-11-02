-- RaceRadar Database Schema
-- This schema defines the structure for tracking race series, events, and availability observations

-- ============================================================================
-- Table: race_series
-- Represents recurring race series (e.g., "London Marathon", "Berlin Marathon")
-- ============================================================================
CREATE TABLE IF NOT EXISTS race_series (
  series_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  city TEXT,
  country TEXT,
  distance_km NUMERIC,
  official_url TEXT,
  timezone TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE race_series IS 'Recurring race series with consistent branding and location';
COMMENT ON COLUMN race_series.series_id IS 'URL-safe slug identifier (e.g., "london-marathon")';
COMMENT ON COLUMN race_series.distance_km IS 'Standard distance in kilometers (e.g., 21.097 for half marathon)';
COMMENT ON COLUMN race_series.timezone IS 'IANA timezone (e.g., "Europe/London")';

-- ============================================================================
-- Table: race_event
-- Represents specific yearly instances of a race series
-- ============================================================================
CREATE TABLE IF NOT EXISTS race_event (
  event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  series_id TEXT NOT NULL REFERENCES race_series(series_id) ON DELETE CASCADE,
  year INTEGER NOT NULL,
  event_local_date DATE,
  event_timezone TEXT,
  reg_url TEXT,
  general_access_status TEXT DEFAULT 'unknown',
  status_confidence NUMERIC DEFAULT 0.5,
  status_source TEXT,
  last_checked_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(series_id, year),
  CONSTRAINT valid_status CHECK (
    general_access_status IN ('unknown', 'not_yet_open', 'open', 'waitlist', 'sold_out', 'closed')
  ),
  CONSTRAINT valid_confidence CHECK (
    status_confidence >= 0 AND status_confidence <= 1
  )
);

COMMENT ON TABLE race_event IS 'Yearly instances of race series with registration details';
COMMENT ON COLUMN race_event.general_access_status IS 'Current registration status for general public';
COMMENT ON COLUMN race_event.status_confidence IS 'Confidence score 0-1 for the parsed status';
COMMENT ON COLUMN race_event.status_source IS 'Source of status info (e.g., "official_site", "manual")';

-- ============================================================================
-- Table: status_observation
-- Raw observations from web scraping and other sources
-- ============================================================================
CREATE TABLE IF NOT EXISTS status_observation (
  observation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id UUID NOT NULL REFERENCES race_event(event_id) ON DELETE CASCADE,
  source TEXT NOT NULL,
  raw_excerpt TEXT,
  parsed_status TEXT,
  confidence NUMERIC,
  url TEXT,
  observed_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT valid_obs_confidence CHECK (
    confidence IS NULL OR (confidence >= 0 AND confidence <= 1)
  )
);

COMMENT ON TABLE status_observation IS 'Historical log of all status checks and their results';
COMMENT ON COLUMN status_observation.source IS 'Observation source (e.g., "official_site", "social_media")';
COMMENT ON COLUMN status_observation.raw_excerpt IS 'Text snippet that informed the classification';
COMMENT ON COLUMN status_observation.parsed_status IS 'Interpreted status from the excerpt';

-- ============================================================================
-- Indexes for performance
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_event_status ON race_event(general_access_status);
CREATE INDEX IF NOT EXISTS idx_event_date ON race_event(event_local_date);
CREATE INDEX IF NOT EXISTS idx_event_series ON race_event(series_id);
CREATE INDEX IF NOT EXISTS idx_obs_event_time ON status_observation(event_id, observed_at DESC);
CREATE INDEX IF NOT EXISTS idx_obs_time ON status_observation(observed_at DESC);

-- ============================================================================
-- Views for common queries
-- ============================================================================

-- View: Upcoming races with open registration
CREATE OR REPLACE VIEW open_races AS
SELECT
  rs.name,
  rs.city,
  rs.country,
  rs.distance_km,
  re.year,
  re.event_local_date,
  re.reg_url,
  re.status_confidence,
  re.last_checked_at
FROM race_event re
JOIN race_series rs ON re.series_id = rs.series_id
WHERE re.general_access_status = 'open'
  AND (re.event_local_date IS NULL OR re.event_local_date >= CURRENT_DATE)
ORDER BY re.event_local_date NULLS LAST;

-- View: Recently sold out races (helpful for waitlist alerts)
CREATE OR REPLACE VIEW recently_sold_out AS
SELECT
  rs.name,
  rs.city,
  rs.country,
  re.event_local_date,
  re.reg_url,
  re.last_checked_at,
  re.status_confidence
FROM race_event re
JOIN race_series rs ON re.series_id = rs.series_id
WHERE re.general_access_status = 'sold_out'
  AND re.last_checked_at >= NOW() - INTERVAL '7 days'
ORDER BY re.last_checked_at DESC;

-- ============================================================================
-- Row-Level Security (RLS) - Optional, configure based on your needs
-- ============================================================================
-- ALTER TABLE race_series ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE race_event ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE status_observation ENABLE ROW LEVEL SECURITY;

-- Example: Public read access, service key for writes
-- CREATE POLICY "Public read access" ON race_series FOR SELECT USING (true);
-- CREATE POLICY "Service writes only" ON race_series FOR INSERT USING (auth.role() = 'service_role');
