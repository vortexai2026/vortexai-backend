def calculate_mao(arv: float, repairs: float, assignment_fee: float = 15000):
    """
    MAO formula:
    (ARV × 70%) – Repairs – Assignment Fee
    """

    if not arv:
        return None

    arv_value = float(arv)
    repairs_value = float(repairs or 0)

    mao = (arv_value * 0.70) - repairs_value - assignment_fee
    return round(mao, 2)
