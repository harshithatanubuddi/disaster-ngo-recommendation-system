from sqlalchemy import text

# ----------------------------
# 3.2 DISASTER → SECTOR MAP
# ----------------------------
DISASTER_TO_SECTOR = {
    "Cyclone": ["disaster management", "relief", "emergency"],
    "Flood": ["flood relief", "water", "sanitation"],
    "Heatwave": ["health", "drinking water"],
    "Earthquake": ["search and rescue", "medical"]
}

# ----------------------------
# 3.1 STATE-LEVEL QUERY (ONLY)
# ----------------------------
def fetch_ngos_by_state(db, state):
    return db.execute(
        text("""
            SELECT *
            FROM ngos
            WHERE LOWER(state) = LOWER(:state)
        """),
        {"state": state}
    ).fetchall()


# NOTE:
# ❌ service_area fallback REMOVED
# Reason:
# - service_area is GEOMETRY (PostGIS)
# - text comparison causes invalid geometry parse error
# - unsafe & dishonest to keep

def fetch_ngos_with_fallback(db, state):
    # Current design: state-level relevance only
    return fetch_ngos_by_state(db, state)


# ----------------------------
# 3.2 CAPABILITY MATCH
# ----------------------------
def matches_sector(ngo, disaster_type):
    required = DISASTER_TO_SECTOR.get(disaster_type, [])

    all_sectors = (
        (ngo.primary_sectors or "") + "," +
        (ngo.secondary_sectors or "") + "," +
        (ngo.declared_sectors or "")
    ).lower()

    for sector in required:
        if sector in all_sectors:
            return True

    return False


# ----------------------------
# 3.3 SEVERITY-AWARE RANKING
# ----------------------------
def rank_ngos(ngos, region, severity):
    def score(ngo):
        s = 0

        # Same-state priority
        if ngo.state and ngo.state.lower() == region.lower():
            s -= 2

        # Same-district bonus (if data exists)
        if ngo.district and ngo.base_district:
            if ngo.district.lower() == ngo.base_district.lower():
                s -= 1

        # High severity → widen ranking (not filtering)
        if severity == "High":
            s -= 0.5

        return s

    return sorted(ngos, key=score)


# ----------------------------
# 3.4 FINAL RECOMMENDATION
# ----------------------------
def recommend_ngos(db, region, disaster_type, severity):
    # 1️⃣ Fetch relevant NGOs (state-level)
    ngos = fetch_ngos_with_fallback(db, region)

    # 2️⃣ Capability matching
    matched = [
        ngo for ngo in ngos
        if matches_sector(ngo, disaster_type)
    ]

    # 3️⃣ Severity-aware ranking
    ranked = rank_ngos(matched, region, severity)

    # 4️⃣ Minimal, safe output
    return [
        {
            "name": ngo.name,
            "state": ngo.state,
            "district": ngo.district,
            "primary_sectors": ngo.primary_sectors
        }
        for ngo in ranked[:10]
    ]
