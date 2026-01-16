# app/services/process_simulation.py

from sqlalchemy import text
from app.alerts.interpret_alert import interpret_alert
from app.services.recommendation_engine import recommend_ngos as recommend_ngos_engine


def process_simulated_alerts(db):
    """
    Use pre-created demo disaster records (e.g., Andhra Pradesh)
    for system demonstration when no live alerts are available.
    """

    demo_disasters = db.execute(
        text("""
            SELECT
                id,
                title,
                disaster_type,
                severity,
                district
            FROM disasters
            WHERE is_demo = TRUE
        """)
    ).fetchall()

    results = []

    for d in demo_disasters:
        interpretation = interpret_alert(d.title)

        if interpretation["human_review_required"]:
            ngos = []
        else:
            ngos = recommend_ngos_engine(
                db=db,
                region=interpretation["region"],
                disaster_type=interpretation["disaster_type"],
                severity=interpretation["severity"]
            )

        results.append({
            "source": "demo",
            "alert_text": d.title,
            "interpretation": interpretation,
            "recommended_ngos": ngos
        })

    return {
        "mode": "simulation",
        "status": "success",
        "results": results
    }
