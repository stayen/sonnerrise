FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy package definitions
COPY pyproject.toml .
COPY packages/ packages/

# Install all packages
RUN pip install --no-cache-dir -e packages/sonnerrise-core \
    && pip install --no-cache-dir -e packages/sonnerrise-personas \
    && pip install --no-cache-dir -e packages/sonnerrise-definitions \
    && pip install --no-cache-dir -e packages/sonnerrise-tracks \
    && pip install --no-cache-dir -e packages/sonnerrise-promo \
    && pip install --no-cache-dir -e packages/sonnerrise-calendar \
    && pip install --no-cache-dir -e packages/sonnerrise-tools \
    && pip install --no-cache-dir -e packages/sonnerrise-web

# Copy configuration
COPY config/ config/

EXPOSE 5000

CMD ["python", "-m", "sonnerrise_web.app"]
