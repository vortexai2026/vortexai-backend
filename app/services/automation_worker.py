import time
from app.ai_level7_orchestrator import process_once

if __name__ == "__main__":
    while True:
        process_once()
        time.sleep(10)
