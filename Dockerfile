FROM python:3.11-slim

# Install wkhtmltopdf + dependencies
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    libxrender1 \
    libxext6 \
    libfontconfig1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY db_schema.sql ./db_schema.sql

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
