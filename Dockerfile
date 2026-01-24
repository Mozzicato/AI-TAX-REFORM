FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including git-lfs
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    git-lfs \
    && rm -rf /var/lib/apt/lists/* \
    && git lfs install

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (LFS files are automatically handled by HF)
COPY . .

# Verify vectorstore files exist
RUN ls -la vectorstore/ && python -c "import faiss; idx = faiss.read_index('vectorstore/faiss_index.bin'); print(f'FAISS index loaded: {idx.ntotal} vectors')"

# Expose port for HuggingFace Spaces
EXPOSE 7860

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/tmp/huggingface
ENV TRANSFORMERS_CACHE=/tmp/huggingface
ENV SENTENCE_TRANSFORMERS_HOME=/tmp/huggingface

# Run with gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:7860", "-w", "1", "--timeout", "300", "app:app"]
