import pandas as pd
import numpy as np
import re
from datetime import datetime

# =========================
# LOAD DATA
# =========================
def load_csv_file(path):
    encodings = ["utf-8", "utf-8-sig", "cp1252", "latin1"]

    for enc in encodings:
        try:
            df = pd.read_csv(path, encoding=enc)
            print(f"File loaded with encoding: {enc}")
            return df
        except Exception:
            pass

    raise ValueError("Impossible de lire le fichier CSV avec les encodings testés")


df = load_csv_file("avito_data_clean.csv")
print("Before cleaning:", df.shape)

# =========================
# CLEAN FUNCTIONS
# =========================
def clean_numeric(value):
    if pd.isna(value):
        return np.nan

    numbers = re.findall(r"\d+(?:[.,]\d+)?", str(value).replace(" ", ""))
    if not numbers:
        return np.nan

    return float(numbers[0].replace(",", "."))


def clean_integer(value):
    number = clean_numeric(value)
    if pd.isna(number):
        return np.nan
    return int(number)


def standardize_city(city):
    if pd.isna(city):
        return np.nan

    city = str(city).strip().lower()

    city_map = {
        "casa": "Casablanca",
        "casablanca": "Casablanca",
        "rabat": "Rabat",
        "marrakech": "Marrakech",
        "tanger": "Tanger",
        "tangier": "Tanger",
        "agadir": "Agadir",
        "fes": "Fes",
        "fès": "Fes",
        "oujda": "Oujda",
        "tamaris": "Tamaris",
    }

    return city_map.get(city, city.title())


def extract_city_from_text(text):
    if pd.isna(text):
        return np.nan

    text = str(text).lower()

    known_cities = [
        "casablanca",
        "rabat",
        "marrakech",
        "tanger",
        "agadir",
        "fes",
        "oujda",
        "tamaris",
    ]

    for city in known_cities:
        if city in text:
            return standardize_city(city)

    return np.nan

def split_location(location):
    if pd.isna(location):
        return pd.Series([np.nan, "Non renseigne"])

    location_str = str(location).strip()
    parts = [part.strip() for part in location_str.split(",") if part.strip()]

    if len(parts) >= 2:
        city_part = parts[0].replace("Appartements dans", "").strip()
        city = standardize_city(city_part)
        district = parts[1].title()
        return pd.Series([city, district])

    city_part = location_str.replace("Appartements dans", "").strip()
    city = standardize_city(city_part)
    return pd.Series([city, "Non renseigne"])



def extract_district_from_title(title):
    if pd.isna(title):
        return np.nan

    title_str = str(title).lower()

    known_districts = [
        "almaz",
        "hivernage",
        "bourgogne",
        "maarif",
        "mers sultan",
        "hay mohammadi",
        "sidi bernoussi",
        "roches noires",
        "val fleuri",
        "tanja balia",
        "boustane",
    ]

    for district in known_districts:
        if district in title_str:
            return district.title()

    return np.nan


def quality_status(row):
    if pd.isna(row["source_url"]) or pd.isna(row["price_mad"]) or pd.isna(row["city"]):
        return "REVIEW"
    return "VALID"


# =========================
# BASIC CLEANING
# =========================
df = df.drop_duplicates(subset=["link"]).copy()

df["title"] = df["title"].fillna("Annonce sans titre")
df["source_url"] = df["link"]

df["price_mad"] = df["price"].apply(clean_numeric)
df["area_m2"] = df["surface"].apply(clean_numeric)
df["bedrooms"] = df["rooms"].apply(clean_integer)
df["bathrooms"] = df["baths"].apply(clean_integer)

df[["city", "district"]] = df["location"].apply(split_location)

missing_city = df["city"].isna()
df.loc[missing_city, "city"] = df.loc[missing_city, "title"].apply(extract_city_from_text)

missing_district = df["district"].isna() | (df["district"] == "Non renseigne")
df["district"] = df["district"].astype("object")

for idx in df[missing_district].index:
    new_value = extract_district_from_title(df.loc[idx, "title"])
    if pd.notna(new_value):
        df.loc[idx, "district"] = new_value

df["district"] = df["district"].fillna("Non renseigne")

# =========================
# HANDLE MISSING VALUES
# =========================
df = df[df["source_url"].notna()]
df = df[df["price_mad"].notna()]
df = df[df["city"].notna()]

# =========================
# OUTLIERS
# =========================
df = df[df["area_m2"].notna()]
df = df[(df["area_m2"] >= 10) & (df["area_m2"] <= 500)]

# =========================
# FEATURE ENGINEERING
# =========================
df["price_per_m2"] = df["price_mad"] / df["area_m2"].replace(0, np.nan)

df["construction_year"] = np.nan
df["floor_no"] = np.nan

current_year = datetime.now().year
df["estimated_age"] = df["construction_year"].apply(
    lambda x: current_year - x if pd.notna(x) else np.nan
)

df["extracted_at"] = pd.Timestamp.now()
df["data_quality_status"] = df.apply(quality_status, axis=1)

# =========================
# FINAL DATASET
# =========================
clean_df = df[
    [
        "source_url",
        "title",
        "city",
        "district",
        "price_mad",
        "area_m2",
        "bedrooms",
        "bathrooms",
        "floor_no",
        "construction_year",
        "estimated_age",
        "price_per_m2",
        "extracted_at",
        "data_quality_status",
    ]
].copy()

print("After cleaning:", clean_df.shape)

clean_df.to_csv("clean_data.csv", index=False, encoding="utf-8-sig")
print("clean_data.csv saved successfully")
