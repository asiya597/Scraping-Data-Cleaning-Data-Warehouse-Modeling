import pandas as pd
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5433/avito_dw"
engine = create_engine(DATABASE_URL)

CSV_FILE = "clean_data.csv"


def load_clean_table():
    df = pd.read_csv(CSV_FILE)

    df["district"] = df["district"].fillna("Non renseigne")

    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE clean.cleaned_listings RESTART IDENTITY CASCADE"))

    df.to_sql(
        "cleaned_listings",
        con=engine,
        schema="clean",
        if_exists="append",
        index=False
    )

    print("clean.cleaned_listings loaded successfully")


def populate_bi_schema():
    with engine.begin() as conn:
        conn.execute(text("""
            TRUNCATE TABLE
                bi_schema.fact_listing,
                bi_schema.dim_time,
                bi_schema.dim_location,
                bi_schema.dim_characteristics
            RESTART IDENTITY CASCADE
        """))

        conn.execute(text("""
            INSERT INTO bi_schema.dim_time (time_key, full_date, year, quarter, month, day)
            SELECT DISTINCT
                CAST(TO_CHAR(CAST(extracted_at AS DATE), 'YYYYMMDD') AS INTEGER),
                CAST(extracted_at AS DATE),
                EXTRACT(YEAR FROM extracted_at)::INT,
                EXTRACT(QUARTER FROM extracted_at)::INT,
                EXTRACT(MONTH FROM extracted_at)::INT,
                EXTRACT(DAY FROM extracted_at)::INT
            FROM clean.cleaned_listings
        """))

        conn.execute(text("""
            INSERT INTO bi_schema.dim_location (city, district)
            SELECT DISTINCT
                city,
                COALESCE(district, 'Non renseigne')
            FROM clean.cleaned_listings
        """))

        conn.execute(text("""
            INSERT INTO bi_schema.dim_characteristics (
                bedrooms,
                bathrooms,
                floor_no,
                construction_year,
                estimated_age
            )
            SELECT DISTINCT
                bedrooms,
                bathrooms,
                floor_no,
                construction_year,
                estimated_age
            FROM clean.cleaned_listings
        """))

        conn.execute(text("""
            INSERT INTO bi_schema.fact_listing (
                listing_sk,
                time_key,
                location_key,
                characteristics_key,
                price_mad,
                area_m2,
                price_per_m2,
                title,
                source_url
            )
            SELECT
                c.listing_sk,
                CAST(TO_CHAR(CAST(c.extracted_at AS DATE), 'YYYYMMDD') AS INTEGER),
                dl.location_key,
                dc.characteristics_key,
                c.price_mad,
                c.area_m2,
                c.price_per_m2,
                c.title,
                c.source_url
            FROM clean.cleaned_listings c
            JOIN bi_schema.dim_location dl
                ON dl.city = c.city
                AND dl.district = COALESCE(c.district, 'Non renseigne')
            JOIN bi_schema.dim_characteristics dc
                ON dc.bedrooms IS NOT DISTINCT FROM c.bedrooms
                AND dc.bathrooms IS NOT DISTINCT FROM c.bathrooms
                AND dc.floor_no IS NOT DISTINCT FROM c.floor_no
                AND dc.construction_year IS NOT DISTINCT FROM c.construction_year
                AND dc.estimated_age IS NOT DISTINCT FROM c.estimated_age
        """))

    print("bi_schema loaded successfully")


def populate_ml_schema():
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE ml_schema.listings_features"))

        conn.execute(text("""
            INSERT INTO ml_schema.listings_features (
                listing_sk,
                source_url,
                title,
                city,
                district,
                price_mad,
                area_m2,
                bedrooms,
                bathrooms,
                floor_no,
                construction_year,
                estimated_age,
                price_per_m2,
                extracted_at,
                data_quality_status
            )
            SELECT
                listing_sk,
                source_url,
                title,
                city,
                district,
                price_mad,
                area_m2,
                bedrooms,
                bathrooms,
                floor_no,
                construction_year,
                estimated_age,
                price_per_m2,
                extracted_at,
                data_quality_status
            FROM clean.cleaned_listings
        """))

    print("ml_schema loaded successfully")


def validate_counts():
    with engine.begin() as conn:
        clean_count = conn.execute(text("SELECT COUNT(*) FROM clean.cleaned_listings")).scalar()
        bi_count = conn.execute(text("SELECT COUNT(*) FROM bi_schema.fact_listing")).scalar()
        ml_count = conn.execute(text("SELECT COUNT(*) FROM ml_schema.listings_features")).scalar()

    print("clean.cleaned_listings:", clean_count)
    print("bi_schema.fact_listing:", bi_count)
    print("ml_schema.listings_features:", ml_count)

    if clean_count != bi_count or clean_count != ml_count:
        raise ValueError("Validation failed: row counts do not match")


def validate_quality():
    with engine.begin() as conn:
        missing_important = conn.execute(text("""
            SELECT COUNT(*)
            FROM clean.cleaned_listings
            WHERE source_url IS NULL
               OR price_mad IS NULL
               OR city IS NULL
        """)).scalar()

    print("Rows with missing important values:", missing_important)


def validate_relations():
    with engine.begin() as conn:
        orphan_count = conn.execute(text("""
            SELECT COUNT(*)
            FROM bi_schema.fact_listing f
            LEFT JOIN bi_schema.dim_time t ON f.time_key = t.time_key
            LEFT JOIN bi_schema.dim_location l ON f.location_key = l.location_key
            LEFT JOIN bi_schema.dim_characteristics c
                ON f.characteristics_key = c.characteristics_key
            WHERE t.time_key IS NULL
               OR l.location_key IS NULL
               OR c.characteristics_key IS NULL
        """)).scalar()

    print("Broken BI relations:", orphan_count)


def clear_staging():
    try:
        with engine.begin() as conn:
            conn.execute(text("TRUNCATE TABLE staging.raw_listings RESTART IDENTITY"))
        print("staging cleaned successfully")
    except Exception:
        print("No staging table found or staging not used")


def main():
    load_clean_table()
    populate_bi_schema()
    populate_ml_schema()
    validate_counts()
    validate_quality()
    validate_relations()
    clear_staging()
    print("Warehouse loading finished successfully")


if __name__ == "__main__":
    main()
