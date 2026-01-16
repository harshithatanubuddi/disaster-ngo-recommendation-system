from fastapi import APIRouter

from app.schemas.override import OverrideRequest
from app.services.override import apply_override

from app.services.audit_logger import log_event
from app.services.versioning import create_version

router = APIRouter(prefix="/override", tags=["Human Review"])


@router.post("/apply")
def human_override(request: OverrideRequest):
    # 1️⃣ APPLY OVERRIDE
    result = apply_override(request)

    # 2️⃣ CREATE VERSION
    version = create_version(2, "human")

    # 3️⃣ AUDIT LOG
    log_event(
        event_type="HUMAN_OVERRIDE",
        payload={
            "version": version,
            "alert_text": request.alert_text,
            "original_prediction": request.original_prediction,
            "overridden_prediction": request.overridden_prediction,
            "overridden_severity": request.overridden_severity,
            "overridden_ngos": request.overridden_ngos,
            "reviewer": request.reviewer_name,
            "reason": request.reason
        }
    )

    # 4️⃣ RETURN FINAL DECISION
    return {
        "decision_version": version,
        **result
    }
