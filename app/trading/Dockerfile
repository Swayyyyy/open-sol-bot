# Build base image first
FROM python:3.10-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PDM_USE_VENV=false \
    PDM_INSTALL_PATH=/app \
    PROJECT_ROOT=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libssl-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install PDM
RUN curl -sSL https://pdm.fming.dev/install-pdm.py | python3 - && \
    ln -s /root/.local/bin/pdm /usr/bin/pdm

WORKDIR /app

# Create necessary directories
RUN mkdir -p /app/libs /app/logs

# Build final image
FROM builder as final

# Install dependencies
COPY ./libs /app/libs
COPY ./app/trading/pyproject.toml /app/
RUN pdm config python.use_venv false && \
    pdm install -G local

ENTRYPOINT [ "pdm", "run", "python", "-m" ]
