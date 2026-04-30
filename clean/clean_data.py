import pandas as pd
import re

# =========================
# LOAD DATA
# =========================

df = pd.read_csv("avito_data_clean.csv")  

print("BEFORE CLEAN:", df.shape)

# =========================
# CLEAN FUNCTIONS
# =========================

def clean_price(x):
    if pd.isna(x):
        return None
    try:
        return int(re.sub(r"\D", "", str(x)))
    except:
        return None


def clean_surface(x):
    if pd.isna(x):
        return None
    try:
        return int(re.sub(r"\D", "", str(x)))
    except:
        return None


def clean_rooms(x):
    if pd.isna(x):
        return None
    match = re.search(r"\d+", str(x))
    return int(match.group()) if match else None


def clean_baths(x):
    if pd.isna(x):
        return None
    match = re.search(r"\d+", str(x))
    return int(match.group()) if match else None


def split_location(loc):
    if pd.isna(loc):
        return None, None
    if "," in loc:
        parts = loc.split(",")
        return parts[0].strip(), parts[1].strip()
    return loc, None


# =========================
# APPLY CLEANING
# =========================

df["price"] = df["price"].apply(clean_price)
df["surface"] = df["surface"].apply(clean_surface)
df["rooms"] = df["rooms"].apply(clean_rooms)
df["baths"] = df["baths"].apply(clean_baths)

df[["city", "quartier"]] = df["location"].apply(
    lambda x: pd.Series(split_location(x))
)

# =========================
# HANDLE MISSING VALUES (SAFE)
# =========================

df = df[df["price"].notna()]   

# fill values
df["surface"] = df["surface"].fillna(df["surface"].median())
df["rooms"] = df["rooms"].fillna(1)
df["baths"] = df["baths"].fillna(1)

# =========================
# REMOVE DUPLICATES
# =========================

df = df.drop_duplicates(subset=["link"])

# =========================
# REMOVE OUTLIERS
# =========================

df = df[(df["price"] > 50000) & (df["price"] < 10000000)]
df = df[(df["surface"] > 20) & (df["surface"] < 500)]

# =========================
# FEATURE ENGINEERING
# =========================

df["price_m2"] = df["price"] / df["surface"]


def price_category(price):
    if pd.isna(price):
        return None
    if price < 500000:
        return "Low"
    elif price < 1000000:
        return "Medium"
    elif price < 2000000:
        return "High"
    else:
        return "Luxury"

df["price_category"] = df["price"].apply(price_category)

def extract_type(title):
    if pd.isna(title):
        return None
    match = re.search(r"(Appartement|Villa|Maison|Studio)", title, re.IGNORECASE)
    return match.group(1) if match else None

df["property_type"] = df["title"].apply(extract_type)


def is_new(desc):
    if pd.isna(desc):
        return False
    return bool(re.search(r"neuf|nouveau", desc, re.IGNORECASE))

df["is_new"] = df["title"].apply(is_new)


df["size_category"] = pd.cut(
    df["surface"],
    bins=[0, 60, 100, 200, 500],
    labels=["Small", "Medium", "Large", "Very Large"]
)

df["bath_room_ratio"] = df["baths"] / df["rooms"]

avg_price_m2 = df.groupby("city")["price_m2"].transform("mean")
df["is_good_deal"] = df["price_m2"] < avg_price_m2

# =========================
# FINAL CHECK
# =========================

print("AFTER CLEAN:", df.shape)
print(df.head())

# =========================
# SAVE CLEAN DATA
# =========================

df.to_csv("clean_data.csv", index=False)

print("✅ CLEAN DATA SAVED")