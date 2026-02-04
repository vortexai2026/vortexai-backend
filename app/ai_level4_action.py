def build_next_action(deal, decision):
    if decision != "contact_seller":
        return {}

    return {
        "type": "outreach",
        "channel": "manual",
        "message": (
            f"Hi, is this still available?\n\n"
            f"I’m a local buyer and can close fast if the price makes sense."
        )
    }
