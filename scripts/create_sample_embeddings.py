"""
Sample Embeddings Generator
Creates mock embeddings for testing without OpenAI API
"""

import json
import hashlib
from pathlib import Path
from typing import List, Dict

def generate_mock_embedding(text: str) -> List[float]:
    """
    Generate a deterministic mock embedding (for testing)
    
    Args:
        text: Text to embed
        
    Returns:
        List of floats representing embedding
    """
    # Use hash to create deterministic but varied vectors
    hash_obj = hashlib.md5(text.encode())
    hash_hex = hash_obj.hexdigest()
    
    # Generate 1536-dimensional vector (standard for text-embedding-3-small)
    embedding = []
    for i in range(1536):
        # Use hash to generate pseudo-random values between -1 and 1
        char_index = i % len(hash_hex)
        char_val = int(hash_hex[char_index], 16)
        value = (char_val - 7.5) / 7.5  # Scale to roughly -1 to 1
        embedding.append(value)
    
    return embedding


def create_sample_embeddings(chunks_file: str, output_file: str):
    """
    Create sample embeddings for chunks
    
    Args:
        chunks_file: Path to chunks JSON
        output_file: Path to output embeddings JSON
    """
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print(f"📊 Creating embeddings for {len(chunks)} chunks...")
    
    embeddings_data = {
        "model": "text-embedding-3-small (mock)",
        "embedding_dimension": 1536,
        "chunks_embedded": len(chunks),
        "embeddings": []
    }
    
    for i, chunk in enumerate(chunks):
        if i % 100 == 0:
            print(f"✓ Processed {i} chunks...")
        
        embedding_record = {
            "chunk_id": chunk['chunk_id'],
            "page": chunk['page'],
            "text_length": len(chunk['text']),
            "text_preview": chunk['text'][:100] + "..." if len(chunk['text']) > 100 else chunk['text'],
            "embedding": generate_mock_embedding(chunk['text']),
            "metadata": {
                "source": "Nigeria-Tax-Act-2025",
                "page": chunk['page'],
                "chunk_index": chunk['chunk_id']
            }
        }
        
        embeddings_data['embeddings'].append(embedding_record)
    
    # Save embeddings
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(embeddings_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Created {len(embeddings_data['embeddings'])} embeddings")
    return embeddings_data


def create_vector_index_config(embeddings_file: str, output_file: str):
    """
    Create Pinecone/Chroma configuration for embeddings
    
    Args:
        embeddings_file: Path to embeddings JSON
        output_file: Path to output config
    """
    with open(embeddings_file, 'r', encoding='utf-8') as f:
        embeddings = json.load(f)
    
    config = {
        "vector_db": "pinecone_or_chroma",
        "index_name": "ntria-tax-knowledge",
        "dimension": 1536,
        "metric": "cosine",
        "total_vectors": len(embeddings['embeddings']),
        "pinecone_config": {
            "index_name": "ntria-tax-knowledge",
            "dimension": 1536,
            "metric": "cosine",
            "environment": "us-west2-az1",
            "pod_type": "p1"
        },
        "chroma_config": {
            "collection_name": "tax-documents",
            "metadata_schema": {
                "source": "text",
                "page": "int",
                "chunk_index": "int"
            }
        },
        "sample_queries": [
            {
                "query": "What is VAT?",
                "embedding_dimension": 1536,
                "expected_results": "VAT entity descriptions"
            },
            {
                "query": "PAYE registration process",
                "embedding_dimension": 1536,
                "expected_results": "PAYE process descriptions"
            }
        ]
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Created vector index configuration: {output_file}")


def main():
    chunks_file = 'data/extracted/chunks.json'
    embeddings_output = 'data/embedded/sample_embeddings.json'
    config_output = 'data/embedded/vector_db_config.json'
    
    # Create output directory
    Path('data/embedded').mkdir(parents=True, exist_ok=True)
    
    print("📝 Generating sample embeddings...\n")
    
    # Create embeddings
    embeddings_data = create_sample_embeddings(chunks_file, embeddings_output)
    
    print(f"\n📋 Creating vector DB configuration...\n")
    
    # Create configuration
    create_vector_index_config(embeddings_output, config_output)
    
    print("\n✅ Embedding preparation complete!")
    print(f"\nFiles created:")
    print(f"  - {embeddings_output}")
    print(f"  - {config_output}")
    print(f"\nNext steps:")
    print(f"1. Connect to Pinecone or Chroma")
    print(f"2. Upload embeddings using the configuration")
    print(f"3. Test similarity search queries")


if __name__ == "__main__":
    main()
