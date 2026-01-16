from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.deps import get_db

from app.alerts.fetch_gdacs import fetch_gdacs_alerts
from app.services.process_alerts import process_live_alerts
from app.services.process_simulation import process_simulated_alerts

router = APIRouter(prefix="/alerts", tags=["alerts"])


# --------------------------------------------------
# LIVE ALERT PROCESSING (NO SIDE EFFECTS)
# --------------------------------------------------
@router.post("/process")
def process_alerts_api(db: Session = Depends(get_db)):
    """
    LIVE MODE:
    - Fetch GDACS alerts
    - Interpret alerts
    - Recommend NGOs
    - ❌ NO file writes
    """
    return process_live_alerts(db)


# --------------------------------------------------
# DEMO / SIMULATION MODE (SAFE, STATIC)
# --------------------------------------------------
@router.post("/simulate")
def simulate_alerts_api(db: Session = Depends(get_db)):
    """
    DEMO MODE:
    - Uses simulated alerts
    - Same logic as live
    - No external calls
    """
    return process_simulated_alerts(db)


# --------------------------------------------------
# OPTIONAL: ADMIN SNAPSHOT (NOT USED BY UI)
# --------------------------------------------------
@router.post("/fetch-live")
def fetch_live_alerts_snapshot():
    """
    ADMIN / RESEARCH ONLY:
    - Fetch alerts
    - Save snapshot to CSV
    - ❌ DO NOT CALL FROM UI
    """
    alerts = fetch_gdacs_alerts()

    if not alerts:
        return {
            "status": "no_alerts",
            "message": "No live alerts available at this time."
        }

    # ⛔ Intentionally NOT imported in live path
    from app.alerts.snapshot import save_snapshot
    snapshot_file = save_snapshot(alerts)

    return {
        "status": "success",
        "count": len(alerts),
        "snapshot": snapshot_file
    }
