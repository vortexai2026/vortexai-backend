execute(
    """
    INSERT INTO deals (
        id,
        source,
        external_id,
        asset_type,
        title,
        description,
        location,
        url,
        price,
        currency,
        profit_score,
        urgency_score,
        risk_score,
        ai_score,
        decision,
        next_action,
        status
    )
    VALUES (
        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
        %s,%s,%s,%s,%s,%s,%s
    )
    """,
    (
        deal_id,
        deal.get("source"),
        deal.get("external_id"),
        deal.get("asset_type"),
        deal.get("title"),
        deal.get("description"),
        deal.get("location"),
        deal.get("url"),
        deal.get("price"),
        deal.get("currency"),
        scores.get("profit_score", 0),
        scores.get("urgency_score", 0),
        scores.get("risk_score", 0),
        scores.get("ai_score", 0),
        decision,
        json.dumps(next_action),   # 🔥 THIS IS THE FIX
        "new"
    )
)
