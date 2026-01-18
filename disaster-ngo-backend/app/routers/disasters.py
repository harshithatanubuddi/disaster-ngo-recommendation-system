from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.deps import get_db
import json

router = APIRouter(prefix="/disasters", tags=["disasters"])

# ---------------------------
# DEMO DISASTERS ONLY
# ---------------------------
@router.get("")
def get_all_disasters(db: Session = Depends(get_db)):

    rows = db.execute(text("""
        SELECT
            id,
            title,
            disaster_type,
            severity,
            ST_AsGeoJSON(geom) AS geom
        FROM disasters
        WHERE
            source = 'demo'
            AND geom IS NOT NULL
            AND disaster_type IS NOT NULL
            AND severity IS NOT NULL
    """)).fetchall()

    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": json.loads(r.geom),
                "properties": {
                    "id": r.id,
                    "title": r.title,
                    "disaster_type": r.disaster_type,
                    "severity": r.severity
                }
            }
            for r in rows
        ]
    }


# ---------------------------
# LIVE DISASTERS ONLY
# ---------------------------
@router.get("/live")
def get_live_disasters(db: Session = Depends(get_db)):

    rows = db.execute(text("""
        SELECT
            id,
            title,
            disaster_type,
            severity,
            ST_AsGeoJSON(geom) AS geom
        FROM disasters
        WHERE
            source = 'live'
            AND is_active = TRUE
            AND geom IS NOT NULL
    """)).fetchall()

    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": json.loads(r.geom),
                "properties": {
                    "id": r.id,
                    "title": r.title,
                    "disaster_type": r.disaster_type,
                    "severity": r.severity
                }
            }
            for r in rows
        ]
    }
