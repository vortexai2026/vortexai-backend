# app/config/money_rules.py

DEAL_TYPES = {
    "real_estate": {
        "min_price": 30000,
        "max_price": 200000,
        "keywords": [
            "foreclosure",
            "must sell",
            "inherited",
            "divorce",
            "cash only",
            "urgent",
            "moving"
        ]
    },
    "cars": {
        "min_price": 1000,
        "max_price": 5000,
        "keywords": [
            "moving",
            "need gone",
            "no time",
            "as-is",
            "urgent"
        ]
    },
    "business": {
        "min_price": 10000,
        "max_price": 250000,
        "keywords": [
            "retiring",
            "must sell",
            "owner retiring",
            "urgent",
            "health reasons"
        ]
    }
}

SCORING_THRESHOLDS = {
    "min_profit": 60,
    "min_urgency": 60,
    "max_risk": 40
}
