from app.database import execute

def learn_adjustment(deal_id, decision, scores):
    execute("""
        INSERT INTO learning_events (id, deal_id, event_type, metadata)
        VALUES (gen_random_uuid(), %s, %s, %s::jsonb)
    """, (
        deal_id,
        decision,
        str(scores).replace("'", '"')
    ))
