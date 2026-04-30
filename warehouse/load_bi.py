import pandas as pd


df= pd.read_csv("clean_data.csv")

# =========================
# DIM LOCALISATION
# =========================
dim_location = df[["city", "quartier"]].drop_duplicates().reset_index(drop=True)
dim_location["location_id"] = dim_location.index + 1

# =========================
# DIM CARACTERISTIQUES
# =========================
dim_carac = df[["property_type", "size_category", "price_category"]].drop_duplicates().reset_index(drop=True)
dim_carac["carac_id"] = dim_carac.index + 1

# =========================
# DIM TEMPS
# =========================
# تأكد عندك colonne date
if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    dim_temps = df[["date"]].drop_duplicates().reset_index(drop=True)
    dim_temps["date_id"] = dim_temps.index + 1
    dim_temps["year"] = dim_temps["date"].dt.year
    dim_temps["month"] = dim_temps["date"].dt.month
else:
    dim_temps = None

# =========================
# FACT TABLE
# =========================

# merge location
fact = df.merge(dim_location, on=["city", "quartier"], how="left")

# merge carac
fact = fact.merge(dim_carac, on=["property_type", "size_category", "price_category"], how="left")

# merge temps (اختياري)
if dim_temps is not None:
    fact = fact.merge(dim_temps, on="date", how="left")

# select colonnes fact
fact_annonce = fact[[
    "price",
    "price_m2",
    "surface",
    "rooms",
    "baths",
    "is_new",
    "is_good_deal",
    "location_id",
    "carac_id"
] + (["date_id"] if dim_temps is not None else [])]


