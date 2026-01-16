from fastapi import APIRouter
from pydantic import BaseModel
import joblib
import numpy as np

router = APIRouter(prefix="/predict", tags=["Prediction"])

# -------------------------------
# LOAD MODEL & VECTORIZER (ONCE)
# -------------------------------

model = joblib.load("app/ml/model.pkl")
vectorizer = joblib.load("app/ml/vectorizer.pkl")

CONFIDENCE_THRESHOLD = 0.6

# -------------------------------
# REQUEST / RESPONSE SCHEMAS
# -------------------------------

class AlertRequest(BaseModel):
    alert_text: str


class PredictionResponse(BaseModel):
    predicted_type: str | None
    confidence: float
    status: str


# -------------------------------
# PREDICTION ENDPOINT
# -------------------------------

@router.post("/disaster", response_model=PredictionResponse)
def predict_disaster(req: AlertRequest):

    text = req.alert_text.lower()

    # Vectorize
    X = vectorizer.transform([text])

    # Predict probabilities
    probs = model.predict_proba(X)[0]
    classes = model.classes_

    max_prob = float(np.max(probs))
    pred_class = classes[np.argmax(probs)]

    if max_prob >= CONFIDENCE_THRESHOLD:
        return PredictionResponse(
            predicted_type=pred_class,
            confidence=round(max_prob, 3),
            status="auto_classified"
        )
    else:
        return PredictionResponse(
            predicted_type=None,
            confidence=round(max_prob, 3),
            status="needs_human_review"
        )
