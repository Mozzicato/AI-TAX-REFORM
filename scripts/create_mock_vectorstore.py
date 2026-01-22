#!/usr/bin/env python
"""Create a mock vectorstore for quick testing without waiting for HF API.
Useful for dev/demo while waiting for reliable embeddings.
"""
import pickle
import numpy as np
import faiss
from pathlib import Path

def create_mock_vectorstore(persist_dir="vectorstore", num_chunks=10):
    """Create a mock vectorstore with random embeddings for testing."""
    persist_dir = Path(persist_dir)
    persist_dir.mkdir(parents=True, exist_ok=True)
    
    # Create mock docs
    docs = [
        {"text": "Personal income tax threshold for 2025 is 300,000 naira per annum.", "source": "Nigeria-Tax-Act-2025.pdf", "page": 1, "chunk_id": "p1_c0"},
        {"text": "Tax rate for income above threshold: 7% for first 300,000 to 600,000 naira.", "source": "Nigeria-Tax-Act-2025.pdf", "page": 2, "chunk_id": "p2_c0"},
        {"text": "Tax rate for 600,000 to 1,000,000: 11%.", "source": "Nigeria-Tax-Act-2025.pdf", "page": 2, "chunk_id": "p2_c1"},
        {"text": "Tax rate above 1,000,000: 15%.", "source": "Nigeria-Tax-Act-2025.pdf", "page": 3, "chunk_id": "p3_c0"},
        {"text": "Self-employed individuals must register with FIRS and file annual returns.", "source": "Nigeria-Tax-Act-2025.pdf", "page": 4, "chunk_id": "p4_c0"},
        {"text": "Capital gains tax is 10% on real property disposals.", "source": "Nigeria-Tax-Act-2025.pdf", "page": 5, "chunk_id": "p5_c0"},
        {"text": "Monthly tax deposits required if income exceeds 500,000 naira.", "source": "Nigeria-Tax-Act-2025.pdf", "page": 6, "chunk_id": "p6_c0"},
        {"text": "Penalties for late filing: minimum 5% of assessed tax or 50,000 naira.", "source": "Nigeria-Tax-Act-2025.pdf", "page": 7, "chunk_id": "p7_c0"},
        {"text": "Tax exemptions: government officials, diplomats, and certain non-profits.", "source": "Nigeria-Tax-Act-2025.pdf", "page": 8, "chunk_id": "p8_c0"},
        {"text": "Appeals process: taxpayers have 30 days to file objections to FIRS assessments.", "source": "Nigeria-Tax-Act-2025.pdf", "page": 9, "chunk_id": "p9_c0"},
    ]
    
    # Create random mock embeddings (768-dim, typical for Nemotron)
    dim = 768
    embeddings = np.random.randn(len(docs), dim).astype(np.float32)
    
    # Normalize for cosine similarity
    norms = (embeddings**2).sum(axis=1, keepdims=True) ** 0.5
    norms[norms == 0] = 1.0
    embeddings = embeddings / norms
    
    # Build FAISS index
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    
    # Save
    faiss.write_index(index, str(persist_dir / "faiss_index.bin"))
    with open(persist_dir / "metadata.pkl", "wb") as f:
        pickle.dump(docs, f)
    
    print(f"Mock vectorstore created with {len(docs)} test chunks in {persist_dir}")

if __name__ == "__main__":
    create_mock_vectorstore()
