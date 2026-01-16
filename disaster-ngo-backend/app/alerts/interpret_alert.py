# app/alerts/interpret_alert.py

from app.alerts.classify_disaster import classify_disaster
from app.alerts.regions import extract_region
from app.alerts.severity import estimate_severity
from app.alerts.review import human_review_required


# --------------------------------------------------
# APPROXIMATE GEO REFERENCE (STATIC, EXPLAINABLE)
# --------------------------------------------------

APPROX_GEO_LOOKUP = {
    "cocos (keeling) islands": {
        "region": "Cocos (Keeling) Islands",
        "lat": -12.1642,
        "lon": 96.8710
    },
    "southeast indian ridge": {
        "region": "Southeast Indian Ridge",
        "lat": -25.0,
        "lon": 90.0
    },
    "sw indian ocean": {
        "region": "South-West Indian Ocean",
        "lat": -20.0,
        "lon": 60.0
    },
    "bay of bengal": {
        "region": "Bay of Bengal",
        "lat": 15.0,
        "lon": 88.0
    },
    "arabian sea": {
        "region": "Arabian Sea",
        "lat": 15.0,
        "lon": 65.0
    }
}


def resolve_geolocation(alert_text: str, extracted_region: str, region_conf: float):
    """
    Resolves geolocation with confidence-aware fallback.
    """

    text = alert_text.lower()

    # ---------------------------
    # LEVEL 1 — EXACT
    # ---------------------------
    if extracted_region and extracted_region.lower() != "unknown":
        return {
            "geo_level": "EXACT",
            "region": extracted_region,
            "lat": None,
            "lon": None,
            "confidence": region_conf
        }

    # ---------------------------
    # LEVEL 2 — APPROXIMATE
    # ---------------------------
    for key, geo in APPROX_GEO_LOOKUP.items():
        if key in text:
            return {
                "geo_level": "APPROXIMATE",
                "region": geo["region"],
                "lat": geo["lat"],
                "lon": geo["lon"],
                "confidence": 0.4
            }

    # ---------------------------
    # LEVEL 3 — UNKNOWN
    # ---------------------------
    return {
        "geo_level": "UNKNOWN",
        "region": "Unknown",
        "lat": None,
        "lon": None,
        "confidence": 0.0
    }


def interpret_alert(alert_text: str):
    """
    Unified alert interpretation pipeline.
    This is the CORE research artifact.
    """

    # Disaster type
    disaster, d_conf = classify_disaster(alert_text)

    # Region extraction (gazetteer)
    region, r_conf = extract_region(alert_text)

    # Severity estimation
    severity, s_conf = estimate_severity(alert_text)

    # Geolocation resolution (NEW, CORE FIX)
    geo = resolve_geolocation(alert_text, region, r_conf)

    # Human review gate (uses ORIGINAL confidences)
    review = human_review_required(d_conf, geo["confidence"], s_conf)

    return {
        "disaster_type": disaster,
        "severity": severity,

        # Geolocation
        "region": geo["region"],
        "geo_level": geo["geo_level"],
        "coordinates": {
            "lat": geo["lat"],
            "lon": geo["lon"]
        },

        # Confidence transparency
        "confidence": {
            "disaster": d_conf,
            "region": geo["confidence"],
            "severity": s_conf
        },

        # Governance
        "human_review_required": review
    }
