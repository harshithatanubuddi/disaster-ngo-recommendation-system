from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.deps import get_db
import json

router = APIRouter(prefix="/recommend", tags=["recommendations"])


@router.get("/volunteers/{disaster_id}")
def recommend_volunteers(disaster_id: int, db: Session = Depends(get_db)):

    query = text("""
        SELECT
            v.id AS volunteer_id,
            v.name AS volunteer_name,
            v.skill AS volunteer_skill,
            ST_AsGeoJSON(v.location) AS volunteer_geom,

            d.id AS disaster_id,
            d.title AS disaster_title,
            d.disaster_type AS disaster_type,
            d.severity AS disaster_severity,
            ST_AsGeoJSON(d.geom) AS disaster_geom,

            ST_Distance(
                v.location::geography,
                ST_Centroid(d.geom)::geography
            ) AS distance_m,

            CASE
                WHEN (
                    (d.disaster_type = 'flood' AND v.skill IN ('rescue', 'medical')) OR
                    (d.disaster_type = 'cyclone' AND v.skill IN ('rescue', 'logistics')) OR
                    (d.disaster_type = 'heatwave' AND v.skill = 'medical') OR
                    (d.disaster_type = 'earthquake' AND v.skill IN ('rescue', 'medical'))
                )
                THEN 1.5
                ELSE 1.0
            END AS skill_factor,

            CASE
                WHEN d.severity = 'high' THEN 1.5
                WHEN d.severity = 'medium' THEN 1.2
                ELSE 1.0
            END AS severity_factor

        FROM volunteers v, disasters d
        WHERE d.id = :disaster_id
          AND v.available = TRUE
    """)

    rows = db.execute(query, {"disaster_id": disaster_id}).fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="No volunteers found")

    # ---- Disaster GeoJSON ----
    disaster_feature = {
        "type": "Feature",
        "geometry": json.loads(rows[0].disaster_geom),
        "properties": {
            "id": rows[0].disaster_id,
            "title": rows[0].disaster_title,
            "type": rows[0].disaster_type,
            "severity": rows[0].disaster_severity
        }
    }

    # ---- Volunteer Scoring ----
    volunteer_features = []
    for r in rows:
        priority_score = (
    float(r.distance_m)
    / float(r.severity_factor)
    / float(r.skill_factor)
)

        if priority_score < 500:
            priority = "high"
        elif priority_score < 2000:
            priority = "medium"
        else:
            priority = "low"

        volunteer_features.append({
            "type": "Feature",
            "geometry": json.loads(r.volunteer_geom),
            "properties": {
                "id": r.volunteer_id,
                "name": r.volunteer_name,
                "skill": r.volunteer_skill,
                "distance_m": round(r.distance_m, 2),
                "skill_match": r.skill_factor > 1.0,
                "priority_score": round(priority_score, 2),
                "priority": priority
            }
        })

    # ---- Sort by priority_score (lower = better) ----
    volunteer_features.sort(
        key=lambda x: x["properties"]["priority_score"]
    )

    return {
        "type": "FeatureCollection",
        "disaster": disaster_feature,
        "volunteers": {
            "type": "FeatureCollection",
            "features": volunteer_features
        }
    }
