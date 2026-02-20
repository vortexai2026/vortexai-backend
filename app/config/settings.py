from pydantic import BaseModel
import os

class Settings(BaseModel):
    # Markets (lock to Dallas + Atlanta)
    MARKETS: list[str] = ["TX_DFW", "GA_ATL"]

    # Property comps provider (choose "rentcast" for now)
    PROPERTY_PROVIDER: str = os.getenv("PROPERTY_PROVIDER", "rentcast")
    RENTCAST_API_KEY: str | None = os.getenv("RENTCAST_API_KEY")

    # Profit thresholds
    GREEN_MIN_SPREAD: float = float(os.getenv("GREEN_MIN_SPREAD", "30000"))
    ORANGE_MIN_SPREAD: float = float(os.getenv("ORANGE_MIN_SPREAD", "18000"))
    MIN_CONFIDENCE_GREEN: int = int(os.getenv("MIN_CONFIDENCE_GREEN", "60"))

    # Email (daily report)
    REPORT_TO_EMAIL: str | None = os.getenv("REPORT_TO_EMAIL")
    SMTP_HOST: str | None = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str | None = os.getenv("SMTP_USER")
    SMTP_PASS: str | None = os.getenv("SMTP_PASS")
    SMTP_FROM: str | None = os.getenv("SMTP_FROM")

settings = Settings()
