# app/alerts/review.py

def human_review_required(type_conf: float, region_conf: float, severity_conf: float):
    """
    Decide whether alert requires human verification.
    Returns True if confidence is low.
    """
    if type_conf < 0.6 or region_conf < 0.6 or severity_conf < 0.6:
        return True
    return False
