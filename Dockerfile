# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all app files
COPY ./app ./app

# Expose port
EXPOSE 8000

# Start app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
