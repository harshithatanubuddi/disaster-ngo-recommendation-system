from pydantic import BaseModel
from typing import List, Optional

class OverrideRequest(BaseModel):
    alert_text: str
    original_prediction: str
    overridden_prediction: str
    overridden_severity: Optional[str] = None
    overridden_ngos: Optional[List[str]] = None
    reviewer_name: str
    reason: str
