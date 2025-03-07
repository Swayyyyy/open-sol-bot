#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
  echo -e "${GREEN}[+] $1${NC}"
}

print_error() {
  echo -e "${RED}[!] $1${NC}"
}

# Check if script is run as root
if [ "$EUID" -ne 0 ]; then
  print_error "Please run as root (use sudo)"
  exit 1
fi

# Update system packages
print_status "Updating system packages..."
apt update
apt upgrade -y

# Install basic dependencies
print_status "Installing basic dependencies..."
apt install -y \
  git \
  curl \
  wget \
  python3 \
  python3-venv \
  python3-dev \
  python3-pip \
  libssl-dev \
  pkg-config

# Install podman
print_status "Installing podman..."
apt install -y podman podman-compose
