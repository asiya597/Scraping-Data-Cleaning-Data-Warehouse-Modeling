CREATE SCHEMA IF NOT EXISTS clean;
CREATE SCHEMA IF NOT EXISTS bi_schema;
CREATE SCHEMA IF NOT EXISTS ml_schema;

CREATE TABLE IF NOT EXISTS clean.cleaned_listings (
    listing_sk BIGSERIAL PRIMARY KEY,
    source_url TEXT NOT NULL UNIQUE,
    title TEXT,
    city TEXT,
    district TEXT,
    price_mad NUMERIC(14,2),
    area_m2 NUMERIC(10,2),
    bedrooms INTEGER,
    bathrooms INTEGER,
    floor_no INTEGER,
    construction_year INTEGER,
    estimated_age INTEGER,
    price_per_m2 NUMERIC(14,2),
    extracted_at TIMESTAMP,
    data_quality_status TEXT
);

CREATE TABLE IF NOT EXISTS bi_schema.dim_time (
    time_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS bi_schema.dim_location (
    location_key BIGSERIAL PRIMARY KEY,
    city TEXT NOT NULL,
    district TEXT NOT NULL,
    UNIQUE (city, district)
);

CREATE TABLE IF NOT EXISTS bi_schema.dim_characteristics (
    characteristics_key BIGSERIAL PRIMARY KEY,
    bedrooms INTEGER,
    bathrooms INTEGER,
    floor_no INTEGER,
    construction_year INTEGER,
    estimated_age INTEGER,
    UNIQUE (bedrooms, bathrooms, floor_no, construction_year, estimated_age)
);

CREATE TABLE IF NOT EXISTS bi_schema.fact_listing (
    fact_listing_key BIGSERIAL PRIMARY KEY,
    listing_sk BIGINT NOT NULL UNIQUE,
    time_key INTEGER NOT NULL REFERENCES bi_schema.dim_time(time_key),
    location_key BIGINT NOT NULL REFERENCES bi_schema.dim_location(location_key),
    characteristics_key BIGINT NOT NULL REFERENCES bi_schema.dim_characteristics(characteristics_key),
    price_mad NUMERIC(14,2),
    area_m2 NUMERIC(10,2),
    price_per_m2 NUMERIC(14,2),
    title TEXT,
    source_url TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS ml_schema.listings_features (
    listing_sk BIGINT PRIMARY KEY,
    source_url TEXT NOT NULL UNIQUE,
    title TEXT,
    city TEXT,
    district TEXT,
    price_mad NUMERIC(14,2),
    area_m2 NUMERIC(10,2),
    bedrooms INTEGER,
    bathrooms INTEGER,
    floor_no INTEGER,
    construction_year INTEGER,
    estimated_age INTEGER,
    price_per_m2 NUMERIC(14,2),
    extracted_at TIMESTAMP,
    data_quality_status TEXT
);

CREATE INDEX IF NOT EXISTS idx_fact_listing_time
ON bi_schema.fact_listing(time_key);

CREATE INDEX IF NOT EXISTS idx_fact_listing_location
ON bi_schema.fact_listing(location_key);

CREATE INDEX IF NOT EXISTS idx_fact_listing_characteristics
ON bi_schema.fact_listing(characteristics_key);

CREATE INDEX IF NOT EXISTS idx_ml_city_district
ON ml_schema.listings_features(city, district);
