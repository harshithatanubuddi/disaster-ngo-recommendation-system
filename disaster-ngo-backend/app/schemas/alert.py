from pydantic import BaseModel

class AlertRequest(BaseModel):
    alert_text: str
    lat: float | None = None
    lon: float | None = None
    source: str = "GDACS"

