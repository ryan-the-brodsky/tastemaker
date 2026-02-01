# TasteMaker Dockerfile
# Multi-stage build: Frontend build -> Python runtime

# =============================================================================
# Stage 1: Build Frontend
# =============================================================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Install dependencies
COPY frontend/package*.json ./
RUN npm ci

# Build frontend
COPY frontend/ ./
RUN npm run build

# =============================================================================
# Stage 2: Python Runtime
# =============================================================================
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/src/ ./src/
COPY backend/migrations/ ./migrations/
COPY backend/alembic.ini ./

# Copy frontend build from stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create data directory for SQLite
RUN mkdir -p /app/data

# Set environment variables
ENV PYTHONPATH=/app/src
ENV DATABASE_URL=sqlite:////app/data/tastemaker.db
ENV SINGLE_USER_MODE=true
ENV ENABLE_BACKGROUND_JOBS=false

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run migrations and start server
CMD cd /app && \
    alembic upgrade head && \
    cd /app/src && \
    uvicorn main:app --host 0.0.0.0 --port 8000
