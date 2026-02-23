def calculate_offer(arv: float, repairs: float, investor_discount: float = 0.70) -> dict:
    """
    Simple wholesale underwriting:
      MAO = (ARV * investor_discount) - repairs
      Offer = MAO (or slightly under if you want)
    """
    mao = (arv * investor_discount) - repairs
    offer = mao
    return {"mao": round(mao, 2), "offer": round(offer, 2)}
