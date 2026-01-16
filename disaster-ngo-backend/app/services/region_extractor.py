INDIAN_STATES = [
    "Andhra Pradesh",
    "Odisha",
    "Tamil Nadu",
    "West Bengal",
    "Kerala",
    "Karnataka",
    "Maharashtra",
    "Gujarat",
    "Goa",
    "Assam",
    "Tripura",
    "Mizoram",
    "Manipur",
    "Meghalaya",
    "Nagaland",
    "Arunachal Pradesh",
    "Bihar",
    "Jharkhand",
    "Chhattisgarh",
    "Uttar Pradesh",
    "Madhya Pradesh",
    "Rajasthan",
    "Punjab",
    "Haryana",
    "Delhi"
]

def extract_regions(text: str):
    text_lower = text.lower()
    matched_states = []

    for state in INDIAN_STATES:
        if state.lower() in text_lower:
            matched_states.append(state)

    if matched_states:
        return matched_states

    # fallback coastal hints
    if "east coast" in text_lower:
        return ["East Coast (India)"]

    if "west coast" in text_lower:
        return ["West Coast (India)"]

    return ["Unknown"]
