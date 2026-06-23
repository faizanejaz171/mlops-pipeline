# ── CV Data Curation Pipeline ──
# Lightweight base (~150MB vs 1.4GB CUDA image)
# GPU is used by the host directly — Docker handles GCP/SSH/curation logic only
FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg libgl1-mesa-glx libglib2.0-0 \
    openssh-client curl git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy pipeline source
COPY src/ ./src/
COPY configs/config.template.yaml ./configs/

# GCP credentials mounted at runtime (never baked into image)
# Usage: docker run -v /path/to/service-account.json:/app/service-account.json ...
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/service-account.json

# Datasets volume mount point
VOLUME ["/app/datasets", "/app/configs"]

CMD ["python3", "src/pipeline/main.py"]
