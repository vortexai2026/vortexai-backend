FROM python:3.11-slim

WORKDIR /app

# copy requirements from app folder
COPY app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copy app code
COPY app/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
