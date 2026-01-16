from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.deps import get_db
import json
from fastapi.responses import StreamingResponse
import csv
import io

router = APIRouter(prefix="/recommend", tags=["recommendations"])

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
SEVERITY_RADIUS_KM = {
    "Low": 20,
    "Medium": 50,
    "High": 100,
    "Extreme": 150
}

MIN_RESULTS = 5

# --------------------------------------------------
# SECTOR NORMALIZATION
# --------------------------------------------------
CAUSE_MAP = {
    "food": "food",
    "nutrition": "food",
    "food processing": "food",

    "drinking water": "water",
    "water": "water",

    "health": "health",
    "medical": "health",
    "hiv": "health",

    "disaster management": "disaster",
    "rescue": "disaster",
    "relief": "disaster",

    "children": "children",
    "aged": "elderly",
    "elderly": "elderly",

    "women": "women",

    "housing": "shelter",
    "urban development": "shelter",
    "rural development": "shelter"
}

# Human-readable labels (REQUIRED for UI / paper)
DISPLAY_MAP = {
    "disaster": "Disaster Management",
    "food": "Food Relief",
    "water": "Drinking Water",
    "health": "Health",
    "children": "Children",
    "elderly": "Elderly",
    "women": "Women",
    "shelter": "Shelter"
}

DISASTER_CAPABILITY = {
    "Flood": {"disaster", "food", "water", "health"},
    "Cyclone": {"disaster", "food", "water", "health"},
    "Heatwave": {"health", "water", "elderly", "children"},
    "Earthquake": {"disaster", "health", "shelter"}
}


def normalize_sectors(sectors):
    out = set()
    for s in sectors or []:
        sl = s.lower()
        for k, v in CAUSE_MAP.items():
            if k in sl:
                out.add(v)
    return out


# --------------------------------------------------
# MAIN ENDPOINT
# --------------------------------------------------
@router.get("/ngos/{disaster_id}")
def recommend_ngos(disaster_id: int, db: Session = Depends(get_db)):

    # 1️⃣ Fetch disaster + centroid
    disaster = db.execute(text("""
        SELECT
            d.id,
            d.title,
            d.disaster_type,
            d.severity,
            ST_AsGeoJSON(d.geom) AS geom,
            dist.name_2 AS district,
            ST_Y(ST_Centroid(d.geom)) AS disaster_lat,
            ST_X(ST_Centroid(d.geom)) AS disaster_lon
        FROM disasters d
        LEFT JOIN districts dist
          ON ST_Contains(dist.geom, ST_Centroid(d.geom))
        WHERE d.id = :id
    """), {"id": disaster_id}).fetchone()

    if not disaster:
        raise HTTPException(404, "Disaster not found")

    dtype = disaster.disaster_type.capitalize()
    if dtype not in DISASTER_CAPABILITY:
        raise HTTPException(400, "Unsupported disaster type")

    radius_km = SEVERITY_RADIUS_KM.get(disaster.severity, 50)
    required_caps = DISASTER_CAPABILITY[dtype]

    # 2️⃣ NGO query
    rows = db.execute(
        text("""
            SELECT
                n.id,
                n.name,
                n.primary_sectors,
                n.secondary_sectors,
                n.base_district,
                n.darpan_id,
                ST_AsGeoJSON(
                  COALESCE(
                    n.base_geom,
                    (SELECT ST_Centroid(geom)
                     FROM districts
                     WHERE LOWER(name_2) = LOWER(n.base_district)
                     LIMIT 1)
                  )
                ) AS geom,
                ST_Distance(
                  COALESCE(
                    n.base_geom,
                    (SELECT ST_Centroid(geom)
                     FROM districts
                     WHERE LOWER(name_2) = LOWER(n.base_district)
                     LIMIT 1)
                  )::geography,
                  ST_SetSRID(
                    ST_MakePoint(:lon, :lat),
                    4326
                  )::geography
                ) AS distance_m
            FROM ngos n
            WHERE
              COALESCE(
                n.base_geom,
                (SELECT ST_Centroid(geom)
                 FROM districts
                 WHERE LOWER(name_2) = LOWER(n.base_district)
                 LIMIT 1)
              ) IS NOT NULL
        """),
        {
            "lat": disaster.disaster_lat,
            "lon": disaster.disaster_lon
        }
    ).fetchall()

    strict_matches = []
    fallback_matches = []

    # 3️⃣ Ranking + sector explainability
    for r in rows:
        if not r.geom:
            continue

        all_sectors = []
        if r.primary_sectors:
            all_sectors.extend(r.primary_sectors)
        if r.secondary_sectors:
            all_sectors.extend(r.secondary_sectors)

        norm = normalize_sectors(all_sectors)
        matched = norm & required_caps
        matched_labels = [DISPLAY_MAP[m] for m in matched]

        distance_km = round((r.distance_m or 0) / 1000, 2)
        distance_score = max(0, 1 - (distance_km / radius_km))

        district_score = 1.0 if (
            disaster.district and
            r.base_district and
            r.base_district.lower() == disaster.district.lower()
        ) else 0.0

        score = round(
            (0.5 * district_score) +
            (0.3 * distance_score),
            3
        )

        item = {
            "type": "Feature",
            "geometry": json.loads(r.geom),
            "properties": {
                "id": r.id,
                "name": r.name,
                "district": r.base_district,
                "distance_km": distance_km,
                "score": score,
                "darpan_id": r.darpan_id,
                "matched_sectors": ", ".join(matched_labels) if matched_labels else "—"
            }
        }

        if matched:
            strict_matches.append(item)
        else:
            fallback_matches.append(item)

    # 4️⃣ Sort + guarantee top-5
    strict_matches.sort(
        key=lambda x: (-x["properties"]["score"], x["properties"]["distance_km"])
    )
    fallback_matches.sort(
        key=lambda x: x["properties"]["distance_km"]
    )

    final_results = strict_matches[:MIN_RESULTS]
    if len(final_results) < MIN_RESULTS:
        final_results.extend(
            fallback_matches[:MIN_RESULTS - len(final_results)]
        )

    return {
        "disaster": {
            "title": disaster.title,
            "type": dtype,
            "severity": disaster.severity,
            "district": disaster.district
        },
        "ngos": {
            "type": "FeatureCollection",
            "features": final_results
        }
    }

@router.get("/ngos/{disaster_id}/export")
def export_ngos(disaster_id: int, db: Session = Depends(get_db)):

    # Reuse the same recommendation logic
    result = recommend_ngos(disaster_id, db)

    ngos = result["ngos"]["features"]

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Rank",
        "NGO Name",
        "Matched Sectors",
        "District",
        "Distance (km)",
        "Score",
        "Darpan ID"
    ])

    for i, f in enumerate(ngos, start=1):
        p = f["properties"]
        writer.writerow([
            i,
            p.get("name"),
            p.get("matched_sectors"),
            p.get("district"),
            p.get("distance_km"),
            p.get("score"),
            p.get("darpan_id")
        ])

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={
            "Content-Disposition":
            f"attachment; filename=ngo_recommendations_{disaster_id}.csv"
        }
    )

# --------------------------------------------------
# LIVE COORDINATE-BASED RECOMMENDATION (FOR MAP)
# --------------------------------------------------
@router.post("/ngos/live")
def recommend_ngos_live(payload: dict, db: Session = Depends(get_db)):
    lat = payload.get("lat")
    lon = payload.get("lon")

    if lat is None or lon is None:
        raise HTTPException(
            status_code=400,
            detail="Coordinates required"
        )

    rows = db.execute(text("""
        SELECT
            n.name,
            n.base_district,
            n.darpan_id,
            ST_AsGeoJSON(
              COALESCE(
                n.base_geom,
                (SELECT ST_Centroid(geom)
                 FROM districts
                 WHERE LOWER(name_2) = LOWER(n.base_district)
                 LIMIT 1)
              )
            ) AS geom,
            ST_Distance(
              COALESCE(
                n.base_geom,
                (SELECT ST_Centroid(geom)
                 FROM districts
                 WHERE LOWER(name_2) = LOWER(n.base_district)
                 LIMIT 1)
              )::geography,
              ST_SetSRID(
                ST_MakePoint(:lon, :lat),
                4326
              )::geography
            ) AS distance_m
        FROM ngos n
        WHERE
          COALESCE(
            n.base_geom,
            (SELECT ST_Centroid(geom)
             FROM districts
             WHERE LOWER(name_2) = LOWER(n.base_district)
             LIMIT 1)
          ) IS NOT NULL
        ORDER BY distance_m
        LIMIT 5
    """), {"lat": lat, "lon": lon}).fetchall()

    features = []
    for i, r in enumerate(rows):
        features.append({
            "type": "Feature",
            "geometry": json.loads(r.geom),
            "properties": {
                "name": r.name,
                "district": r.base_district,
                "distance_km": round((r.distance_m or 0) / 1000, 2),
                "score": round(1 - (i * 0.1), 2),
                "darpan_id": r.darpan_id
            }
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }
