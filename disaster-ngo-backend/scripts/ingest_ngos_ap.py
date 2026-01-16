import pandas as pd
from geopy.geocoders import Nominatim
from sqlalchemy import text
from app.database import engine

# ---- Config ----
CSV_PATH = "data/andhra_pradesh_ngos.csv"
SRID = 4326

# ---- Geocoder ----
geolocator = Nominatim(user_agent="disaster-ngo-research")

def geocode_district(district, state):
    query = f"{district}, {state}, India"
    location = geolocator.geocode(query, timeout=10)
    if location:
        return location.latitude, location.longitude
    return None, None


# ---- Load CSV ----
df = pd.read_csv(CSV_PATH)

with engine.begin() as conn:
    for _, row in df.iterrows():
        lat, lon = geocode_district(row["district"], row["state"])

        if lat is None or lon is None:
            print(f"[WARN] Geocoding failed for {row['district']} — skipping")
            continue

        sql = text("""
            INSERT INTO ngos (name, state, district, cause, service_area)
            VALUES (
                :name,
                :state,
                :district,
                :cause,
                ST_SetSRID(ST_MakePoint(:lon, :lat), :srid)
            )
        """)

        conn.execute(
            sql,
            {
                "name": row["name"],
                "state": row["state"],
                "district": row["district"],
                "cause": row["cause"],
                "lat": lat,
                "lon": lon,
                "srid": SRID,
            },
        )

        print(f"[OK] Inserted NGO: {row['name']} ({row['district']})")
