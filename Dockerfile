# -----------------------------------------------------------------------------
# Stage 1: Build React 19 Frontend Web Studio
# -----------------------------------------------------------------------------
FROM node:20-alpine AS frontend-builder
WORKDIR /app/apps/web

COPY apps/web/package*.json ./
RUN npm ci || npm install

COPY apps/web/ ./
RUN npm run build

# -----------------------------------------------------------------------------
# Stage 2: Python 3.11 Backend & Unified Production Server
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS production

# Install system dependencies (FFmpeg for video compositing, curl for healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Astral UV for blazing fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy dependency manifests
COPY pyproject.toml uv.lock ./

# Install python dependencies (including boto3 for AWS S3 and Bedrock)
RUN uv sync --no-dev

# Copy application source code
COPY rivet/ ./rivet/
COPY services/ ./services/
COPY cli/ ./cli/
COPY fixtures/ ./fixtures/

# Copy built frontend assets into the container
COPY --from=frontend-builder /app/apps/web/dist /app/apps/web/dist

# Default environment configuration
ENV HOST=0.0.0.0
ENV PORT=8000
ENV PYTHONUNBUFFERED=1
ENV RIVET_ENV=production

EXPOSE 8000

# Health check probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

# Launch FastAPI application serving both API and static frontend UI
CMD ["uv", "run", "uvicorn", "services.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
