#!/usr/bin/env python
"""Query the local FAISS vectorstore and return top-k chunks using HF Inference API.
Usage: python scripts/query_qa.py --query "what is the personal income tax threshold" --top_k 5
"""
import argparse
import json
import os
import pickle
from pathlib import Path

from dotenv import load_dotenv, dotenv_values
load_dotenv()

import faiss
import numpy as np
import requests


def embed_text_hf(texts, model_id="sentence-transformers/all-mpnet-base-v2", api_token=None, timeout=15):
    """Call HF Inference API to embed texts with timeout."""
    if api_token is None:
        raise Exception("HF_TOKEN not found. Please set HF_TOKEN in your .env or environment variables.")
    
    # Use the new router endpoint (api-inference is deprecated)
    api_url = f"https://router.huggingface.co/hf-inference/models/{model_id}"
    headers = {"Authorization": f"Bearer {api_token}"}
    
    payload = {"inputs": texts, "options": {"wait_for_model": True}}
    response = requests.post(api_url, json=payload, headers=headers, timeout=timeout)
    
    if response.status_code != 200:
        if response.status_code == 401:
            raise Exception("HF API error 401: Unauthorized. Check your HF_TOKEN and model access permissions.")
        if response.status_code == 503:
            raise Exception("HF API: Model is loading, please retry in a moment.")
        raise Exception(f"HF API error {response.status_code}: {response.text}")
    
    embeddings = response.json()
    if isinstance(embeddings, dict) and "error" in embeddings:
        raise Exception(f"HF API error: {embeddings['error']}")
    
    # HF returns list of embeddings, need to handle the format
    # For feature-extraction, it returns token-level embeddings, we need to mean pool
    emb_array = np.array(embeddings, dtype=np.float32)
    if len(emb_array.shape) == 3:
        # Mean pooling over tokens
        emb_array = emb_array.mean(axis=1)
    
    return emb_array


def load_vectorstore(persist_dir="vectorstore"):
    persist_dir = Path(persist_dir)
    index = faiss.read_index(str(persist_dir / "faiss_index.bin"))
    with open(persist_dir / "metadata.pkl", "rb") as f:
        docs = pickle.load(f)
    return index, docs


def query(index, docs, q, model_id="sentence-transformers/all-mpnet-base-v2", top_k=5, api_token=None):
    """Query the vectorstore using local sentence-transformers model."""
    import logging
    logger = logging.getLogger(__name__)
    
    # Use local model - HF API doesn't support direct embeddings for sentence-transformers
    from sentence_transformers import SentenceTransformer
    
    # Cache model in module-level variable
    global _st_model
    if '_st_model' not in globals() or _st_model is None:
        logger.info(f"Loading SentenceTransformer model: {model_id}")
        try:
            # Set HF token for model download if available
            hf_token = api_token or os.getenv("HF_TOKEN")
            if hf_token:
                os.environ["HF_TOKEN"] = hf_token
            
            # Use cache folder if set (Docker builds pre-download here)
            cache_folder = os.getenv("SENTENCE_TRANSFORMERS_HOME")
            if cache_folder:
                _st_model = SentenceTransformer(model_id, cache_folder=cache_folder)
            else:
                _st_model = SentenceTransformer(model_id)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    emb = _st_model.encode([q], show_progress_bar=False, convert_to_numpy=True)
    emb = np.array(emb, dtype=np.float32)
    emb = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-12)
    
    D, I = index.search(emb, top_k)
    results = []
    for score, idx in zip(D[0], I[0]):
        if idx < 0:
            continue
        meta = docs[idx]
        results.append({"score": float(score), "text": meta["text"], "source": meta["source"], "page": meta["page"], "chunk_id": meta["chunk_id"]})
    return results

# Model cache
_st_model = None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    parser.add_argument("--persist_dir", default="vectorstore")
    parser.add_argument("--model", default="nvidia/llama-embed-nemotron-8b")
    parser.add_argument("--top_k", type=int, default=5)
    parser.add_argument("--hf_token", default=None, help="Hugging Face token (overrides HF_TOKEN env/.env)")
    args = parser.parse_args()

    index, docs = load_vectorstore(args.persist_dir)
    res = query(index, docs, args.query, args.model, args.top_k, api_token=args.hf_token)
    print(json.dumps(res, indent=2))
