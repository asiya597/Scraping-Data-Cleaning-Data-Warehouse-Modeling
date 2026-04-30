import pandas as pd 

df = pd.read_csv("clean_data.csv")

# =========================
# ML TABLE
# =========================

ml_table = df[[
    "price",
    "surface",
    "rooms",
    "baths",
    "price_m2",
    "city",
    "quartier",
    "property_type",
    "size_category",
    "price_category",
    "is_new",
    "is_good_deal"
]]

# حذف أي NaN مهمين
ml_table = ml_table.dropna()

# save
