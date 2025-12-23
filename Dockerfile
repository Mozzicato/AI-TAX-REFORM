FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install google-generativeai

# Copy backend code
COPY backend/app ./app

# Create data directory
RUN mkdir -p /app/data && chmod 777 /app/data

# Expose default port (for documentation)
EXPOSE 8000

# Health check uses the container's $PORT (falls back to 8000)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Run FastAPI app and bind to the provided $PORT (Render provides $PORT at runtime)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
