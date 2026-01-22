#!/usr/bin/env python
"""Ingest PDF, chunk text, build FAISS index and save metadata using HF Inference API.
Usage: python scripts/ingest_pdf.py --pdf data/raw/Nigeria-Tax-Act-2025.pdf
"""
import argparse
import os
import pickle
from pathlib import Path

from dotenv import load_dotenv, dotenv_values
load_dotenv()

import faiss
import numpy as np
import requests
from PyPDF2 import PdfReader
from tqdm import tqdm


def chunk_text(text, chunk_size=500, overlap=100):
    """Chunk text with overlap."""
    start = 0
    length = len(text)
    while start < length:
        end = min(start + chunk_size, length)
        yield text[start:end]
        start = end - overlap if end < length else end


def embed_text_hf(texts, model_id="nvidia/llama-embed-nemotron-8b", api_token=None):
    """Call HF Inference API to embed texts."""
    if api_token is None:
        raise Exception("HF_TOKEN not found. Please set HF_TOKEN in your .env or environment variables.")
    api_url = f"https://router.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {api_token}"}
    
    payload = {"inputs": texts}
    response = requests.post(api_url, json=payload, headers=headers, timeout=60)
    
    if response.status_code != 200:
        # Provide clearer error for 401 Unauthorized
        if response.status_code == 401:
            raise Exception("HF API error 401: Unauthorized. Check your HF_TOKEN and model access permissions.")
        raise Exception(f"HF API error {response.status_code}: {response.text}")
    
    embeddings = response.json()
    if isinstance(embeddings, dict) and "error" in embeddings:
        raise Exception(f"HF API error: {embeddings['error']}")
    
    return np.array(embeddings, dtype=np.float32)


# Local embedder using sentence-transformers
def embed_text_local(texts, model_name="sentence-transformers/all-mpnet-base-v2"):
    """Embed texts locally using sentence-transformers."""
    try:
        from sentence_transformers import SentenceTransformer
    except Exception as e:
        raise Exception("Local sentence-transformers not installed. Install it with `pip install sentence-transformers`.")
    model = SentenceTransformer(model_name)
    embs = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return np.array(embs, dtype=np.float32)


def main(pdf_path, persist_dir="vectorstore", model_id="sentence-transformers/all-mpnet-base-v2", batch_size=8, api_token=None):
    pdf_path = Path(pdf_path)
    assert pdf_path.exists(), f"PDF not found: {pdf_path}"
    persist_dir = Path(persist_dir)
    persist_dir.mkdir(parents=True, exist_ok=True)

    # Allow explicit token via argument, otherwise use env or .env
    if api_token is None:
        env_vars = dotenv_values()
        api_token = os.getenv("HF_TOKEN") or env_vars.get("HF_TOKEN")

    reader = PdfReader(str(pdf_path))
    pages = [p.extract_text() or "" for p in reader.pages]

    docs = []
    for i, page_text in enumerate(pages, start=1):
        for j, chunk in enumerate(chunk_text(page_text)):
            docs.append({
                "text": chunk.strip(),
                "source": pdf_path.name,
                "page": i,
                "chunk_id": f"p{i}_c{j}",
            })

    if not docs:
        print("No text extracted from PDF.")
        return

    texts = [d["text"] for d in docs]
    print(f"Creating embeddings for {len(texts)} chunks using {model_id}...")

    # Embed in batches to avoid timeout
    embeddings_list = []
    for batch_start in tqdm(range(0, len(texts), batch_size)):
        batch_end = min(batch_start + batch_size, len(texts))
        batch_texts = texts[batch_start:batch_end]
            # Use local sentence-transformers if model_id points to sentence-transformers namespace
        if model_id.startswith("sentence-transformers/"):
            batch_embs = embed_text_local(batch_texts, model_id)
        else:
            batch_embs = embed_text_hf(batch_texts, model_id, api_token)
        embeddings_list.append(batch_embs)

    embeddings = np.vstack(embeddings_list)

    # Normalize for cosine-similarity via inner product
    norms = (embeddings**2).sum(axis=1, keepdims=True) ** 0.5
    norms[norms == 0] = 1.0
    embeddings = embeddings / norms

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    faiss.write_index(index, str(persist_dir / "faiss_index.bin"))

    with open(persist_dir / "metadata.pkl", "wb") as f:
        pickle.dump(docs, f)

    print("Vectorstore saved to:", persist_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True, help="Path to PDF to ingest")
    parser.add_argument("--persist_dir", default="vectorstore")
    parser.add_argument("--model", default="nvidia/llama-embed-nemotron-8b")
    parser.add_argument("--batch_size", type=int, default=8)
    parser.add_argument("--hf_token", default=None, help="Hugging Face token (overrides HF_TOKEN env/.env)")
    args = parser.parse_args()
    main(args.pdf, args.persist_dir, args.model, args.batch_size, api_token=args.hf_token)
