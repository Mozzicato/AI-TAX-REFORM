"""
Pinecone Service for NTRIA
Uses Pinecone's Integrated Inference for embeddings (multilingual-e5-large)
No local embedding model needed!
"""

import os
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# Pinecone configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "ntria-tax")
PINECONE_HOST = os.getenv("PINECONE_HOST", "")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "multilingual-e5-large")


class PineconeService:
    """Service for Pinecone vector operations with integrated inference."""
    
    def __init__(self):
        """Initialize Pinecone client."""
        try:
            try:
                # Try newer SDK first
                from pinecone import Pinecone
            except ImportError:
                # Fall back to old SDK if needed
                from pinecone import Pinecone
            
            self.pc = Pinecone(api_key=PINECONE_API_KEY)
            self.index = self.pc.Index(PINECONE_INDEX_NAME)
            self.model = EMBEDDING_MODEL
            self.initialized = True
            print(f"✅ Pinecone initialized: index={PINECONE_INDEX_NAME}")
        except Exception as e:
            print(f"❌ Pinecone initialization failed: {e}")
            print(f"   API Key configured: {bool(PINECONE_API_KEY)}")
            print(f"   Index name: {PINECONE_INDEX_NAME}")
            print(f"   Host: {PINECONE_HOST}")
            self.initialized = False
            self.pc = None
            self.index = None
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embeddings using Pinecone's Inference API.
        Uses multilingual-e5-large model.
        """
        if not self.initialized:
            raise RuntimeError("Pinecone not initialized")
        
        try:
            # Use Pinecone's inference API
            embeddings = self.pc.inference.embed(
                model=self.model,
                inputs=[text],
                parameters={"input_type": "query"}
            )
            return embeddings[0].values
        except Exception as e:
            print(f"❌ Embedding error: {e}")
            raise
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents.
        """
        if not self.initialized:
            raise RuntimeError("Pinecone not initialized")
        
        try:
            embeddings = self.pc.inference.embed(
                model=self.model,
                inputs=texts,
                parameters={"input_type": "passage"}
            )
            return [e.values for e in embeddings]
        except Exception as e:
            print(f"❌ Batch embedding error: {e}")
            raise
    
    def upsert_documents(
        self, 
        documents: List[Dict[str, Any]], 
        namespace: str = "tax-docs"
    ) -> int:
        """
        Upsert documents to Pinecone with embeddings.
        
        Args:
            documents: List of dicts with 'id', 'text', 'metadata'
            namespace: Pinecone namespace
            
        Returns:
            Number of vectors upserted
        """
        if not self.initialized:
            raise RuntimeError("Pinecone not initialized")
        
        # Extract texts for embedding
        texts = [doc["text"] for doc in documents]
        
        # Generate embeddings
        embeddings = self.embed_documents(texts)
        
        # Prepare vectors for upsert
        vectors = []
        for doc, embedding in zip(documents, embeddings):
            vectors.append({
                "id": doc["id"],
                "values": embedding,
                "metadata": {
                    "text": doc["text"][:1000],  # Pinecone metadata limit
                    **doc.get("metadata", {})
                }
            })
        
        # Upsert in batches of 100
        batch_size = 100
        upserted = 0
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch, namespace=namespace)
            upserted += len(batch)
            print(f"  Upserted {upserted}/{len(vectors)} vectors...")
        
        return upserted
    
    def search(
        self, 
        query: str, 
        top_k: int = 5, 
        namespace: str = "tax-docs",
        filter: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query text
            top_k: Number of results
            namespace: Pinecone namespace
            filter: Metadata filter
            
        Returns:
            List of matching documents with scores
        """
        if not self.initialized:
            raise RuntimeError("Pinecone not initialized")
        
        # Generate query embedding
        query_embedding = self.embed_text(query)
        
        # Search
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            namespace=namespace,
            include_metadata=True,
            filter=filter
        )
        
        # Format results
        documents = []
        for match in results.matches:
            documents.append({
                "id": match.id,
                "score": match.score,
                "text": match.metadata.get("text", ""),
                "metadata": match.metadata
            })
        
        return documents
    
    def delete_namespace(self, namespace: str = "tax-docs"):
        """Delete all vectors in a namespace."""
        if not self.initialized:
            raise RuntimeError("Pinecone not initialized")
        
        self.index.delete(delete_all=True, namespace=namespace)
        print(f"✅ Deleted all vectors in namespace: {namespace}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        if not self.initialized:
            return {"error": "Pinecone not initialized"}
        
        stats = self.index.describe_index_stats()
        return {
            "total_vectors": stats.total_vector_count,
            "namespaces": dict(stats.namespaces) if stats.namespaces else {},
            "dimension": stats.dimension
        }


# Singleton instance
_pinecone_service = None

def get_pinecone_service() -> PineconeService:
    """Get or create Pinecone service instance."""
    global _pinecone_service
    if _pinecone_service is None:
        _pinecone_service = PineconeService()
    return _pinecone_service


# Quick test
if __name__ == "__main__":
    service = get_pinecone_service()
    
    if service.initialized:
        print("\n📊 Index Stats:")
        print(json.dumps(service.get_stats(), indent=2))
        
        print("\n🔍 Testing search...")
        results = service.search("What is VAT?", top_k=3)
        print(f"Found {len(results)} results")
        for r in results:
            print(f"  - {r['id']}: {r['score']:.3f}")
    else:
        print("❌ Service not initialized")
