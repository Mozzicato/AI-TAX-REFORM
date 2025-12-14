"""
Embedding Generation & Vector Database Population
Generates embeddings for document chunks and stores in vector database
"""

import json
import os
from typing import List, Dict
from dotenv import load_dotenv
import openai

load_dotenv()

# Initialize OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

# ============================================================================
# EMBEDDING GENERATION
# ============================================================================

def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for text using OpenAI API
    
    Args:
        text: Text to embed
        
    Returns:
        Embedding vector (list of floats)
    """
    try:
        response = openai.Embedding.create(
            input=text,
            model=EMBEDDING_MODEL
        )
        return response["data"][0]["embedding"]
    except Exception as e:
        print(f"❌ Error generating embedding: {str(e)}")
        return None

def generate_embeddings_batch(chunks: List[Dict]) -> List[Dict]:
    """
    Generate embeddings for multiple chunks
    
    Args:
        chunks: List of document chunks
        
    Returns:
        List of chunks with embeddings added
    """
    
    print(f"\n🔄 Generating embeddings for {len(chunks)} chunks...")
    
    chunks_with_embeddings = []
    
    for i, chunk in enumerate(chunks, 1):
        text = chunk.get("text", "")
        
        if not text:
            print(f"⚠️  Chunk {i}: Empty text, skipping")
            continue
        
        # Generate embedding
        embedding = generate_embedding(text)
        
        if embedding:
            chunk_with_embedding = {
                **chunk,
                "embedding": embedding,
                "embedding_model": EMBEDDING_MODEL
            }
            chunks_with_embeddings.append(chunk_with_embedding)
            
            if i % 5 == 0:
                print(f"  ✅ [{i}/{len(chunks)}] Generated embedding")
        else:
            print(f"  ⚠️  [{i}/{len(chunks)}] Failed to generate embedding")
    
    print(f"\n✅ Generated {len(chunks_with_embeddings)} embeddings")
    return chunks_with_embeddings

# ============================================================================
# VECTOR DATABASE ADAPTERS
# ============================================================================

class VectorDBAdapter:
    """Abstract base class for vector database adapters"""
    
    def add_chunks(self, chunks: List[Dict]) -> bool:
        """Add chunks to vector database"""
        raise NotImplementedError
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """Search vector database"""
        raise NotImplementedError

class JSONGraphAdapter(VectorDBAdapter):
    """JSON-based graph storage - no external vector DB needed"""
    
    def __init__(self):
        self.graph_file = "/workspaces/AI-TAX-REFORM/data/knowledge_graph.json"
        os.makedirs(os.path.dirname(self.graph_file), exist_ok=True)
        print("✅ Using local JSON graph storage")

    def add_chunks(self, chunks: List[Dict]) -> bool:
        """Add chunks to JSON graph file"""
        try:
            # Load existing graph or create new
            if os.path.exists(self.graph_file):
                with open(self.graph_file, 'r') as f:
                    graph = json.load(f)
            else:
                graph = {"chunks": [], "metadata": {"total_chunks": 0}}
            
            # Add new chunks
            graph["chunks"].extend(chunks)
            graph["metadata"]["total_chunks"] = len(graph["chunks"])
            
            # Save updated graph
            with open(self.graph_file, 'w') as f:
                json.dump(graph, f, indent=2)
            
            print(f"✅ Saved {len(chunks)} chunks to JSON graph")
            return True
            
        except Exception as e:
            print(f"❌ Error saving chunks to JSON graph: {str(e)}")
            return False

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """Basic text search in JSON graph (no embedding search)"""
        if not os.path.exists(self.graph_file):
            return []
        
        try:
            with open(self.graph_file, 'r') as f:
                graph = json.load(f)
            
            chunks = graph.get("chunks", [])
            # Simple keyword matching instead of vector similarity
            query_words = set(str(query_embedding).lower().split())
            
            scored_chunks = []
            for chunk in chunks:
                text = chunk.get("text", "").lower()
                # Simple scoring based on keyword overlap
                score = len(set(text.split()) & query_words) / max(len(query_words), 1)
                if score > 0:
                    scored_chunks.append({
                        "score": score,
                        "text": chunk.get("text", ""),
                        "metadata": chunk.get("metadata", {})
                    })
            
            # Sort by score and return top_k
            scored_chunks.sort(key=lambda x: x["score"], reverse=True)
            return scored_chunks[:top_k]
            
        except Exception as e:
            print(f"❌ Error searching JSON graph: {str(e)}")
            return []

class PineconeAdapter(VectorDBAdapter):
    """Pinecone vector database adapter"""
    
    def __init__(self):
        try:
            import pinecone
            self.pinecone = pinecone
            
            # Initialize Pinecone
            api_key = os.getenv("PINECONE_API_KEY")
            environment = os.getenv("PINECONE_ENVIRONMENT")
            index_name = os.getenv("PINECONE_INDEX_NAME", "ntria-tax-documents")
            
            self.pinecone.init(api_key=api_key, environment=environment)
            self.index = self.pinecone.Index(index_name)
            
            print("✅ Connected to Pinecone")
        except Exception as e:
            print(f"❌ Error initializing Pinecone: {str(e)}")
            self.index = None
    
    def add_chunks(self, chunks: List[Dict]) -> bool:
        """Add chunks to Pinecone"""
        if not self.index:
            return False
        
        try:
            vectors_to_insert = []
            
            for chunk in chunks:
                chunk_id = chunk.get("chunk_id")
                embedding = chunk.get("embedding")
                
                if not chunk_id or not embedding:
                    continue
                
                # Prepare metadata (exclude embedding for storage)
                metadata = {
                    "source": chunk.get("metadata", {}).get("source", "unknown"),
                    "page": chunk.get("metadata", {}).get("page", 0),
                    "text_preview": chunk.get("text", "")[:200]
                }
                
                vectors_to_insert.append({
                    "id": chunk_id,
                    "values": embedding,
                    "metadata": metadata
                })
            
            # Batch insert
            self.index.upsert(vectors=vectors_to_insert)
            print(f"✅ Inserted {len(vectors_to_insert)} vectors to Pinecone")
            return True
            
        except Exception as e:
            print(f"❌ Error adding chunks to Pinecone: {str(e)}")
            return False
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """Search Pinecone"""
        if not self.index:
            return []
        
        try:
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            return [
                {
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata
                }
                for match in results.matches
            ]
        except Exception as e:
            print(f"❌ Error searching Pinecone: {str(e)}")
            return []

class ChromaAdapter(VectorDBAdapter):
    """Chroma vector database adapter (local)"""
    
    def __init__(self):
        try:
            import chromadb
            self.client = chromadb.Client()
            self.collection = self.client.get_or_create_collection(
                name="ntria-tax-documents",
                metadata={"hnsw:space": "cosine"}
            )
            print("✅ Connected to Chroma")
        except Exception as e:
            print(f"❌ Error initializing Chroma: {str(e)}")
            self.collection = None
    
    def add_chunks(self, chunks: List[Dict]) -> bool:
        """Add chunks to Chroma"""
        if not self.collection:
            return False
        
        try:
            ids = []
            embeddings = []
            documents = []
            metadatas = []
            
            for chunk in chunks:
                ids.append(chunk.get("chunk_id"))
                embeddings.append(chunk.get("embedding"))
                documents.append(chunk.get("text"))
                metadatas.append({
                    "source": chunk.get("metadata", {}).get("source", "unknown"),
                    "page": str(chunk.get("metadata", {}).get("page", 0))
                })
            
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            
            print(f"✅ Added {len(ids)} chunks to Chroma")
            return True
            
        except Exception as e:
            print(f"❌ Error adding chunks to Chroma: {str(e)}")
            return False

# ============================================================================
# PIPELINE
# ============================================================================

def get_vector_db_adapter() -> VectorDBAdapter:
    """Get appropriate vector database adapter based on config"""
    
    db_type = os.getenv("VECTOR_DB_TYPE", "json").lower()
    
    if db_type == "json":
        return JSONGraphAdapter()
    elif db_type == "chroma":
        return ChromaAdapter()
    else:
        print(f"⚠️  Using JSON adapter as fallback for: {db_type}")
        return JSONGraphAdapter()

def load_chunks(input_dir: str = "data/chunked") -> List[Dict]:
    """Load document chunks from files"""
    
    chunks = []
    chunks_file = os.path.join(input_dir, "chunks.json")
    
    if os.path.exists(chunks_file):
        with open(chunks_file, "r") as f:
            chunks = json.load(f)
        print(f"✅ Loaded {len(chunks)} chunks")
    else:
        print(f"⚠️  Chunks file not found: {chunks_file}")
    
    return chunks

def save_chunks_with_embeddings(chunks: List[Dict], output_dir: str = "data/embedded"):
    """Save chunks with embeddings to file"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, "chunks_with_embeddings.json")
    
    with open(output_file, "w") as f:
        json.dump(chunks, f, indent=2)
    
    print(f"✅ Saved chunks with embeddings to {output_file}")

def populate_vector_db(chunks: List[Dict]):
    """Main pipeline to generate embeddings and populate vector database"""
    
    print("\n🚀 Starting embedding & vector DB population...")
    
    # Get vector DB adapter
    db_adapter = get_vector_db_adapter()
    if not db_adapter:
        print("❌ Failed to initialize vector database")
        return
    
    # Generate embeddings
    chunks_with_embeddings = generate_embeddings_batch(chunks)
    
    if not chunks_with_embeddings:
        print("❌ No chunks with embeddings")
        return
    
    # Add to vector database
    success = db_adapter.add_chunks(chunks_with_embeddings)
    
    if success:
        # Save locally as backup
        save_chunks_with_embeddings(chunks_with_embeddings)
        print("\n✅ Vector database population completed successfully!")
    else:
        print("\n❌ Failed to populate vector database")

# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import sys
    
    input_dir = sys.argv[1] if len(sys.argv) > 1 else "data/chunked"
    
    print(f"📂 Loading chunks from: {input_dir}")
    chunks = load_chunks(input_dir)
    
    if chunks:
        populate_vector_db(chunks)
    else:
        print("❌ No chunks loaded")
