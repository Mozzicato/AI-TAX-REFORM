"""
Upload Tax Data to Pinecone
Uploads the extracted tax document chunks to Pinecone.
Uses Pinecone's integrated inference for embeddings.
"""

import os
import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from dotenv import load_dotenv
load_dotenv()

def load_chunks() -> list:
    """Load extracted text chunks."""
    chunks_path = Path("/workspaces/AI-TAX-REFORM/data/extracted/chunks.json")
    
    if not chunks_path.exists():
        # Try alternate path
        chunks_path = Path("/workspaces/AI-TAX-REFORM/data/chunked/Nigeria-Tax-Act-2025.json")
    
    if not chunks_path.exists():
        print("❌ No chunks file found!")
        return []
    
    with open(chunks_path, "r") as f:
        data = json.load(f)
    
    # Handle different formats
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and "chunks" in data:
        return data["chunks"]
    else:
        return [data]


def upload_to_pinecone():
    """Upload chunks to Pinecone using integrated inference."""
    from pinecone import Pinecone
    
    print("=" * 60)
    print("📤 UPLOADING TAX DATA TO PINECONE")
    print("=" * 60)
    
    # Initialize Pinecone
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME", "ntria-tax")
    
    pc = Pinecone(api_key=api_key)
    index = pc.Index(index_name)
    
    print(f"✅ Connected to Pinecone index: {index_name}")
    
    # Get current stats
    print("\n📊 Current index stats:")
    stats = index.describe_index_stats()
    print(f"   Total vectors: {stats.total_vector_count}")
    
    # Load chunks
    print("\n📂 Loading chunks...")
    chunks = load_chunks()
    print(f"   Loaded {len(chunks)} chunks")
    
    if not chunks:
        print("❌ No chunks to upload!")
        return
    
    # Prepare records for upsert
    print("\n🔧 Preparing records...")
    records = []
    
    for i, chunk in enumerate(chunks):
        # Handle different chunk formats
        if isinstance(chunk, str):
            text = chunk
            metadata = {"chunk_index": i}
        elif isinstance(chunk, dict):
            text = chunk.get("text", chunk.get("content", str(chunk)))
            metadata = {
                "chunk_index": i,
                "page": chunk.get("page", chunk.get("page_number", 0)),
                "section": chunk.get("section", ""),
                "source": chunk.get("source", "Nigeria-Tax-Act-2025")
            }
        else:
            continue
        
        # Skip empty chunks
        if not text or len(text.strip()) < 10:
            continue
        
        # For integrated indexes, we pass the text directly
        records.append({
            "_id": f"chunk_{i}",
            "text": text[:8000],  # Limit text length
            **metadata
        })
    
    print(f"   Prepared {len(records)} records")
    
    # Upload in batches using upsert_records for integrated index
    print("\n⬆️ Uploading to Pinecone...")
    batch_size = 50
    uploaded = 0
    
    try:
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            index.upsert_records(namespace="tax-docs", records=batch)
            uploaded += len(batch)
            print(f"   Uploaded {uploaded}/{len(records)} records...")
        
        print(f"\n✅ Successfully uploaded {uploaded} records!")
    except Exception as e:
        print(f"\n❌ Upload failed: {e}")
        print("   Trying alternative method...")
        
        # Fallback: use regular upsert with inference API for embeddings
        try:
            vectors = []
            for i, rec in enumerate(records[:100]):  # Limit for testing
                # Generate embedding using inference
                embedding = pc.inference.embed(
                    model="multilingual-e5-large",
                    inputs=[rec["text"]],
                    parameters={"input_type": "passage"}
                )
                vectors.append({
                    "id": rec["_id"],
                    "values": embedding[0].values,
                    "metadata": {"text": rec["text"][:500], **{k: v for k, v in rec.items() if k not in ["_id", "text"]}}
                })
            
            index.upsert(vectors=vectors, namespace="tax-docs")
            print(f"✅ Uploaded {len(vectors)} vectors using inference API")
        except Exception as e2:
            print(f"❌ Fallback also failed: {e2}")
            return
    
    # Verify
    print("\n📊 Updated index stats:")
    stats = index.describe_index_stats()
    print(f"   Total vectors: {stats.total_vector_count}")
    
    # Test search
    print("\n🔍 Testing search...")
    try:
        # For integrated index, search with text
        results = index.search(
            namespace="tax-docs",
            query={"text": "What is VAT?"},
            top_k=3,
            include_metadata=True
        )
        print(f"   Found {len(results.get('matches', []))} results")
        for match in results.get("matches", [])[:3]:
            print(f"   - Score: {match.get('score', 0):.3f}")
    except Exception as e:
        print(f"   Search test skipped: {e}")
    
    print("\n" + "=" * 60)
    print("✅ UPLOAD COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    upload_to_pinecone()
