import os
import time
import requests

APP_URL = os.getenv("APP_URL", "http://localhost:8080")
LOOP_SECONDS = int(os.getenv("AI_LOOP_SECONDS", "600"))  # every 10 minutes

def post(path: str):
    url = f"{APP_URL}{path}"
    r = requests.post(url, timeout=30)
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, {"raw": r.text}

def run_loop():
    """
    Level 7 = autonomous loop
    - Score deals
    - Make decision
    - Execute actions
    """
    print("[AI] Level 7 Orchestrator started")

    while True:
        try:
            # 1) run actions (emails, pdf triggers, etc.)
            code, data = post("/ai/action/run-once")
            print("[AI] Actions:", code, data)

        except Exception as e:
            print("[AI] ERROR:", str(e))

        time.sleep(LOOP_SECONDS)

if __name__ == "__main__":
    run_loop()
