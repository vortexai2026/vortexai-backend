import re

def extract_price(text: str):
    match = re.search(r"\$([\d,]+)", text)
    if match:
        return float(match.group(1).replace(",", ""))
    return None

def extract_location(text: str):
    cities = [
        "Winnipeg", "Toronto", "Calgary", "Vancouver",
        "Dallas", "Houston", "Miami", "Orlando"
    ]
    for city in cities:
        if city.lower() in text.lower():
            return city
    return None
