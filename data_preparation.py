import pandas as pd

# CSV loading functions will go here
import sqlite3
import pandas as pd
from pathlib import Path

# ✅ Paths
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database" / "food_wastage.db"
DATA_DIR = BASE_DIR / "data"

# ✅ Connect DB
conn = sqlite3.connect(DB_PATH)

# ---------- Load Providers ----------
providers_csv = DATA_DIR / "providers_data.csv"
if providers_csv.exists():
    df_providers = pd.read_csv(providers_csv)
    df_providers.to_sql("providers", conn, if_exists="replace", index=False)
    print("✅ Providers data loaded successfully")
else:
    print("⚠️ providers_data.csv not found")

# ---------- Load Receivers ----------
receivers_csv = DATA_DIR / "receivers_data.csv"
if receivers_csv.exists():
    df_receivers = pd.read_csv(receivers_csv)
    df_receivers.to_sql("receivers", conn, if_exists="replace", index=False)
    print("✅ Receivers data loaded successfully")
else:
    print("⚠️ receivers_data.csv not found")

# ---------- Load Food Listings ----------
food_listings_csv = DATA_DIR / "food_listings_data.csv"
if food_listings_csv.exists():
    df_food = pd.read_csv(food_listings_csv)
    df_food.to_sql("food_listings", conn, if_exists="replace", index=False)
    print("✅ Food listings data loaded successfully")
else:
    print("⚠️ food_listings_data.csv not found")

# ---------- Load Claims ----------
claims_csv = DATA_DIR / "claims_data.csv"
if claims_csv.exists():
    df_claims = pd.read_csv(claims_csv)
    df_claims.to_sql("claims", conn, if_exists="replace", index=False)
    print("✅ Claims data loaded successfully")
else:
    print("⚠️ claims_data.csv not found")

conn.close()
print("🎯 All available datasets loaded into database!")
