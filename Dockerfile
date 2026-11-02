FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend source and dataset pack
COPY backend ./backend
COPY pharmacy_stockout_dataset_pack ./pharmacy_stockout_dataset_pack

# Pre-populate database during container build so startup is instant
RUN python backend/scripts/bootstrap_db.py

ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT}"]

