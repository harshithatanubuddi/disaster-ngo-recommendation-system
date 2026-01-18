# app/utils/geo_filter.py

INDIA_BBOX = {
    "min_lat": 6.0,
    "max_lat": 37.0,
    "min_lon": 68.0,
    "max_lon": 97.0
}

BLOCK_TERMS = [
    "indian ocean",
    "sw indian",
    "western indian ridge",
    "antarctic",
    "mid-ocean ridge"
]

def is_india_relevant(text: str, lat: float | None, lon: float | None) -> bool:
    t = text.lower()

    # ❌ hard reject misleading geography
    for term in BLOCK_TERMS:
        if term in t:
            return False

    # ✅ coordinate-based check (PRIMARY)
    if lat is not None and lon is not None:
        return (
            INDIA_BBOX["min_lat"] <= lat <= INDIA_BBOX["max_lat"]
            and INDIA_BBOX["min_lon"] <= lon <= INDIA_BBOX["max_lon"]
        )

    # ⚠️ fallback (weak, last resort)
    return "india" in t
