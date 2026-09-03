# ==========================================
# STAGE 1: Build & Dependency Compilation
# ==========================================
FROM python:3.12-slim-bookworm AS builder

WORKDIR /app

# Prevent Python from writing byte-code and buffering output streams during compilation
ENV PYTHONTONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install essential system-level packages required to compile ChromaDB/pysqlite dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    sqlite3 \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy your dependencies configuration layer first to maximize Docker layer caching
COPY requirements.txt .

# Install dependencies into an isolated local user directory space inside the builder stage
RUN pip install --no-cache-dir --user -r requirements.txt

# ==========================================
# STAGE 2: Final Minimal Runtime Container
# ==========================================
FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONTONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy the pre-compiled isolated libraries straight into your production target layer
COPY --from=builder /root/.local /root/.local
COPY . .

# Explicitly ensure your runtime paths point to the newly imported package binaries
ENV PATH=/root/.local/bin:$PATH

# Expose the internal container network interface port
EXPOSE 8000

# Execute Uvicorn safely for production without reload tracking utilities overhead
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
