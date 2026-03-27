-- Property scraper database schema

-- Properties table (source-agnostic)
CREATE TABLE IF NOT EXISTS properties (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    source_url TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    
    display_address TEXT,
    property_type TEXT,
    bedrooms INTEGER,
    bathrooms INTEGER,
    size_sqft INTEGER,
    floor_level TEXT,
    furnished TEXT,
    
    price_pcm INTEGER,
    price_pw INTEGER,
    original_price_pcm INTEGER,
    price_reduction_count INTEGER DEFAULT 0,
    
    latitude REAL,
    longitude REAL,
    postcode TEXT,
    postcode_outcode TEXT,
    postcode_incode TEXT,
    
    description TEXT,
    key_features TEXT,
    images TEXT,
    
    epc_rating TEXT,
    council_tax_band TEXT,
    
    agent_name TEXT,
    agent_address TEXT,
    
    listing_update_reason TEXT,
    available_date TEXT,
    
    scraped_at TEXT NOT NULL,
    first_seen_at TEXT,
    updated_at TEXT,
    
    raw_data TEXT
);

CREATE INDEX IF NOT EXISTS idx_properties_source ON properties(source);
CREATE INDEX IF NOT EXISTS idx_properties_postcode ON properties(postcode);
CREATE INDEX IF NOT EXISTS idx_properties_postcode_outcode ON properties(postcode_outcode);
CREATE INDEX IF NOT EXISTS idx_properties_bedrooms ON properties(bedrooms);
CREATE INDEX IF NOT EXISTS idx_properties_price_pcm ON properties(price_pcm);
CREATE INDEX IF NOT EXISTS idx_properties_scraped_at ON properties(scraped_at);
CREATE INDEX IF NOT EXISTS idx_properties_first_seen ON properties(first_seen_at);
CREATE INDEX IF NOT EXISTS idx_properties_status ON properties(status);

-- Watchlist table
CREATE TABLE IF NOT EXISTS watchlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    source TEXT NOT NULL,
    criteria TEXT NOT NULL,
    scrape_interval_hours INTEGER DEFAULT 4,
    enabled INTEGER DEFAULT 1,
    created_at TEXT,
    updated_at TEXT,
    last_scraped_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_watchlist_source ON watchlist(source);
CREATE INDEX IF NOT EXISTS idx_watchlist_enabled ON watchlist(enabled);
