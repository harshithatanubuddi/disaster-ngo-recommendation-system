from regions import extract_region

if __name__ == "__main__":
    alert = "Severe cyclone warning issued for Andhra Pradesh coast"

    region, confidence = extract_region(alert)

    print(region)
    print(confidence)
