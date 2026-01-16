from pydantic import BaseModel

class AlertRequest(BaseModel):
    alert_text: str
