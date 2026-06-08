FROM python:3.12-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install OpenHands and data science libraries
RUN pip install --no-cache-dir \
    openhands-ai \
    pandas>=2.0 \
    numpy>=1.24 \
    scipy \
    scikit-learn \
    matplotlib \
    seaborn \
    plotly

# Upgrade litellm for latest model support
RUN pip install --no-cache-dir --upgrade litellm

# Create directories
RUN mkdir -p /workspace /data /output /trajectories

WORKDIR /workspace

# Copy network isolation script
COPY network-lock.sh /opt/network-lock.sh
RUN chmod +x /opt/network-lock.sh

# Copy entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy OpenHands SDK wrapper
COPY openhands-sdk.py /opt/openhands-sdk.py

ENTRYPOINT ["/entrypoint.sh"]
