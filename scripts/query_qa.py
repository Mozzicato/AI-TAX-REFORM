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


def embed_text_hf(texts, model_id="nvidia/llama-embed-nemotron-8b", api_token=None, timeout=10):
    """Call HF Inference API to embed texts with timeout."""
    if api_token is None:
        raise Exception("HF_TOKEN not found. Please set HF_TOKEN in your .env or environment variables.")
    api_url = f"https://router.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {api_token}"}
    
    payload = {"inputs": texts}
    response = requests.post(api_url, json=payload, headers=headers, timeout=timeout)
    
    if response.status_code != 200:
        if response.status_code == 401:
            raise Exception("HF API error 401: Unauthorized. Check your HF_TOKEN and model access permissions.")
        raise Exception(f"HF API error {response.status_code}: {response.text}")
    
    embeddings = response.json()
    if isinstance(embeddings, dict) and "error" in embeddings:
        raise Exception(f"HF API error: {embeddings['error']}")
    
    return np.array(embeddings, dtype=np.float32)


def embed_text_local(texts, model_name="sentence-transformers/all-mpnet-base-v2"):
    """Embed texts locally using sentence-transformers with model caching."""
    global _sentence_model_cache
    try:
        from sentence_transformers import SentenceTransformer
    except Exception as e:
        raise Exception("Local sentence-transformers not installed. Install it with `pip install sentence-transformers`.")
    
    # Cache the model to avoid reloading
    if '_sentence_model_cache' not in globals() or _sentence_model_cache is None:
        _sentence_model_cache = {}
    
    if model_name not in _sentence_model_cache:
        _sentence_model_cache[model_name] = SentenceTransformer(model_name)
    
    model = _sentence_model_cache[model_name]
    embs = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return np.array(embs, dtype=np.float32)

# Model cache
_sentence_model_cache = None


def load_vectorstore(persist_dir="vectorstore"):
    persist_dir = Path(persist_dir)
    index = faiss.read_index(str(persist_dir / "faiss_index.bin"))
    with open(persist_dir / "metadata.pkl", "rb") as f:
        docs = pickle.load(f)
    return index, docs


def query(index, docs, q, model_id="sentence-transformers/all-mpnet-base-v2", top_k=5, api_token=None):
    if api_token is None:
        env_vars = dotenv_values()
        api_token = os.getenv("HF_TOKEN") or env_vars.get("HF_TOKEN")
    if model_id.startswith("sentence-transformers/"):
        emb = embed_text_local([q], model_id)
    else:
        emb = embed_text_hf([q], model_id, api_token)
    emb = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-12)
    D, I = index.search(emb, top_k)
    results = []
    for score, idx in zip(D[0], I[0]):
        if idx < 0:
            continue
        meta = docs[idx]
        results.append({"score": float(score), "text": meta["text"], "source": meta["source"], "page": meta["page"], "chunk_id": meta["chunk_id"]})
    return results


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
