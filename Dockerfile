FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port for HuggingFace Spaces
EXPOSE 7860

# Set environment variables - model will download on first request
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/tmp/huggingface
ENV TRANSFORMERS_CACHE=/tmp/huggingface
ENV SENTENCE_TRANSFORMERS_HOME=/tmp/huggingface

# Run with gunicorn bound to 0.0.0.0:7860 with long timeout for model download
CMD ["gunicorn", "-b", "0.0.0.0:7860", "-w", "1", "--timeout", "600", "app:app"]
