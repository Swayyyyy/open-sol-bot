FROM --platform=linux/amd64 ubuntu:22.04 as builder

# Set environment variables to avoid interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive
ENV DOCKERMODE=true
ENV PYTHONUNBUFFERED=1 \
  PYTHONPATH=/app/src \
  PDM_USE_VENV=false \
  PDM_INSTALL_PATH=/app

# Install necessary packages for Xvfb and pyvirtualdisplay
RUN apt-get update && \
    apt-get install -y \
        python3 \
        python3-pip \
        wget \
        gnupg \
        ca-certificates \
        libx11-xcb1 \
        libxcomposite1 \
        libxdamage1 \
        libxrandr2 \
        libxss1 \
        libxtst6 \
        libnss3 \
        libatk-bridge2.0-0 \
        libgtk-3-0 \
        x11-apps \
        fonts-liberation \
        libappindicator3-1 \
        libu2f-udev \
        libvulkan1 \
        libdrm2 \
        xdg-utils \
        xvfb \
        build-essential \
        curl \
        git \
        libssl-dev \
        pkg-config \
        && rm -rf /var/lib/apt/lists/*

# Add Google Chrome repository and install Google Chrome
RUN wget -q -O /usr/share/keyrings/google-chrome.gpg https://dl.google.com/linux/linux_signing_key.pub && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update --allow-insecure-repositories && \
    apt-get install -y --allow-unauthenticated google-chrome-stable


RUN apt install python3.10-venv -y

# Install PDM
RUN curl -sSL https://pdm.fming.dev/install-pdm.py | python3 - && \
  ln -s /root/.local/bin/pdm /usr/bin/pdm

WORKDIR /app

RUN mkdir -p /app/libs /app/logs

# Build final image
FROM builder as final

# Install dependencies
COPY ./libs /app/libs
COPY ./app/gmgn/pyproject.toml /app/
RUN pdm config python.use_venv false && \
    pdm install -G local

# Expose the port for remote debugging
EXPOSE 9222

# Expose the port for the FastAPI server
EXPOSE 8000
ENTRYPOINT [ "pdm", "run", "python", "-m" ]