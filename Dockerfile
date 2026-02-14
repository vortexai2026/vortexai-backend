FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# RUN_MODE=api (default) or RUN_MODE=worker
CMD ["sh", "-c", "if [ \"$RUN_MODE\" = \"worker\" ]; then python -m app.worker.automation_worker; else uvicorn app.main:app --host 0.0.0.0 --port ${PORT}; fi"]
