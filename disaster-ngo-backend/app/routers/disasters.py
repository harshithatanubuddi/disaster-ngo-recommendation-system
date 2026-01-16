from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.deps import get_db
import json

router = APIRouter(prefix="/disasters", tags=["disasters"])

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
    """)).fetchall()

    features = []

    for r in rows:
        features.append({
            "type": "Feature",
            "geometry": json.loads(r.geom),
            "properties": {
                "id": r.id,
                "title": r.title,
                "disaster_type": r.disaster_type,
                "severity": r.severity
            }
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }
