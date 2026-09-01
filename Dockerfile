# ==========================================
# 🧬 Digital Twin AI — Multi-Service Dockerfile
# ==========================================

FROM python:3.11-slim as base

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system dependencies (build-essential, libpq for PostgreSQL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose default ports for FastAPI (8000) and Streamlit (8501)
EXPOSE 8000 8501

# Default command launches FastAPI backend
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
