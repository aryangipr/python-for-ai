FROM python:3.11-slim

WORKDIR /app

# Install system deps for building wheels and common image libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libfreetype6-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install first (cache)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . /app

ENV PYTHONUNBUFFERED=1

EXPOSE 5000

# Run with gunicorn referencing the Flask app in index.py
CMD ["gunicorn", "app.index:app", "-b", "0.0.0.0:5000", "--workers", "2"]
