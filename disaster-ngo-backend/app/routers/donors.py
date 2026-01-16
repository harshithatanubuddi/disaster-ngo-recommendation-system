from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.deps import get_db
import json

router = APIRouter(prefix="/recommend", tags=["recommendations"])


@router.get("/donors/{disaster_id}")
def recommend_for_donors(disaster_id: int, db: Session = Depends(get_db)):

    query = text("""
        SELECT
            n.id AS ngo_id,
            n.name AS ngo_name,
            n.cause AS ngo_cause,
            ST_AsGeoJSON(n.service_area) AS ngo_geom,

            d.id AS disaster_id,
            d.title AS disaster_title,
            d.severity AS disaster_severity,
            ST_AsGeoJSON(d.geom) AS disaster_geom,

            ST_Distance(
                ST_Centroid(n.service_area)::geography,
                ST_Centroid(d.geom)::geography
            ) AS distance_m,

            CASE
                WHEN d.severity = 'high' THEN 1.5
                WHEN d.severity = 'medium' THEN 1.2
                ELSE 1.0
            END AS severity_factor,

            CASE
                WHEN n.cause IN ('rescue', 'medical') THEN 1.5
                WHEN n.cause IN ('food', 'logistics') THEN 1.2
                ELSE 1.0
            END AS cause_factor

        FROM ngos n
        JOIN disasters d
        ON ST_Intersects(n.service_area, d.geom)
        WHERE d.id = :disaster_id
    """)

    rows = db.execute(query, {"disaster_id": disaster_id}).fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="No NGOs found")

    # ---- Disaster Info ----
    disaster_info = {
        "id": rows[0].disaster_id,
        "title": rows[0].disaster_title,
        "severity": rows[0].disaster_severity
    }

    # ---- NGO Scoring ----
    ngos = []
    for r in rows:
        donor_priority_score = (
            float(r.distance_m)
            / float(r.severity_factor)
            / float(r.cause_factor)
        )

        ngos.append({
            "id": r.ngo_id,
            "name": r.ngo_name,
            "cause": r.ngo_cause,
            "distance_m": round(r.distance_m, 2),
            "priority_score": round(donor_priority_score, 2),
            "priority_reason": (
                f"Severity={r.disaster_severity}, "
                f"Cause={r.ngo_cause}, "
                f"Distance-based ranking"
            )
        })

    ngos.sort(key=lambda x: x["priority_score"])

    return {
        "disaster": disaster_info,
        "recommended_ngos_for_donors": ngos
    }
