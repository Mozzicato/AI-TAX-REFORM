"""
Hybrid Retrieval Module
Combines JSON-based and vector-based retrieval for optimal results
"""

import json
import os
from typing import List, Dict, Tuple
from dotenv import load_dotenv
import google.generativeai as genai
from app.services.json_graph import JSONGraphDB

load_dotenv()

# Initialize connections
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL = "gemini-pro"
EMBEDDING_MODEL = "models/embedding-001"

# ============================================================================
# JSON GRAPH RETRIEVER (Replaces Neo4j)
# ============================================================================

class JsonGraphRetriever:
    """Retrieves information from JSON knowledge graph (no Neo4j needed)"""
    
    def __init__(self):
        self.db = JSONGraphDB()
    
    def extract_entities_from_query(self, query: str) -> Dict:
        """
        Extract tax entities from user query using GPT-4
        
        Args:
            query: User question
            
        Returns:
            Dictionary with extracted entities and their types
        """
        
        prompt = f"""
        Extract tax-related entities from this question:
        "{query}"
        
        Return JSON with:
        {{
          "entities": [
            {{"name": "entity_name", "type": "Tax | Taxpayer | Agency | etc"}}
          ]
        }}
        
        Only return entities that directly relate to Nigerian taxes.
        If no relevant entities found, return {{"entities": []}}
        """
        
        try:
            model = genai.GenerativeModel(MODEL)
            full_prompt = f"You are a tax expert. Extract entities and return only JSON.\n\n{prompt}"
            
            response = model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=500
                )
            )
            
            result_text = response.text
            # Clean up markdown code blocks if present
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
                
            return json.loads(result_text)
        except Exception as e:
            print(f"⚠️  Error extracting entities: {str(e)}")
            return {"entities": []}
    
    def search_by_entity(self, entity_name: str, depth: int = 2) -> List[Dict]:
        """
        Search graph starting from an entity
        
        Args:
            entity_name: Entity to search from
            depth: Relationship depth (1-3)
            
        Returns:
            List of related nodes
        """
        try:
            # Search for nodes matching the name
            nodes = self.db.search(entity_name)
            if not nodes:
                return []
            
            # Use the first match
            start_node = nodes[0]
            
            # Get related entities
            related = self.db.get_related_entities(start_node["id"], max_depth=depth)
            
            # Format results
            results = [{"node": start_node}]
            for item in related:
                results.append(item)
                
            return results
                
        except Exception as e:
            print(f"⚠️  Graph search error: {str(e)}")
            return []

    def get_context(self, entities: Dict) -> List[Dict]:
        """Get context for a list of entities"""
        context = []
        entity_list = entities.get("entities", [])
        
        for entity in entity_list:
            name = entity.get("name")
            if name:
                results = self.search_by_entity(name)
                context.extend(results)
        
        return context
    
    def get_tax_obligations(self, taxpayer_category: str) -> List[Dict]:
        """
        Get all taxes applicable to a taxpayer category
        
        Args:
            taxpayer_category: Type of taxpayer
            
        Returns:
            List of applicable taxes with details
        """
        
        if not self.driver:
            return []
        
        try:
            with self.driver.session(database=self.database) as session:
                query = """
                MATCH (tp:Taxpayer {category: $category})-[:liable_for]->(tax:Tax)
                OPTIONAL MATCH (tax)-[:has_deadline]->(deadline:Deadline)
                OPTIONAL MATCH (tax)-[:applies_to]->(penalty:Penalty)
                RETURN tax, deadline, penalty
                """
                
                results = session.run(query, {"category": taxpayer_category})
                return [record.data() for record in results]
                
        except Exception as e:
            print(f"⚠️  Error getting tax obligations: {str(e)}")
            return []
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()

# ============================================================================
# VECTOR RETRIEVER
# ============================================================================

class VectorRetriever:
    """Retrieves documents from vector database"""
    
    def __init__(self):
        self.db_type = os.getenv("VECTOR_DB_TYPE", "pinecone").lower()
        self.adapter = self._init_adapter()
    
    def _init_adapter(self):
        """Initialize vector database adapter"""
        if self.db_type == "pinecone":
            try:
                import pinecone
                api_key = os.getenv("PINECONE_API_KEY")
                environment = os.getenv("PINECONE_ENVIRONMENT")
                index_name = os.getenv("PINECONE_INDEX_NAME", "ntria-tax-documents")
                
                pinecone.init(api_key=api_key, environment=environment)
                index = pinecone.Index(index_name)
                print("✅ Connected to Pinecone for retrieval")
                return index
            except Exception as e:
                print(f"⚠️  Pinecone error: {str(e)}")
                return None
        
        elif self.db_type == "chroma":
            try:
                import chromadb
                client = chromadb.Client()
                collection = client.get_or_create_collection(
                    name="ntria-tax-documents"
                )
                print("✅ Connected to Chroma for retrieval")
                return collection
            except Exception as e:
                print(f"⚠️  Chroma error: {str(e)}")
                return None
        
        return None
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        try:
            result = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=text,
                task_type="retrieval_query"
            )
            return result['embedding']
        except Exception as e:
            print(f"⚠️  Embedding error: {str(e)}")
            return None
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search vector database for similar documents
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of relevant documents
        """
        
        if not self.adapter:
            return []
        
        # Generate query embedding
        query_embedding = self.generate_embedding(query)
        if not query_embedding:
            return []
        
        try:
            if self.db_type == "pinecone":
                results = self.adapter.query(
                    vector=query_embedding,
                    top_k=top_k,
                    include_metadata=True
                )
                
                return [
                    {
                        "id": match.id,
                        "score": match.score,
                        "metadata": match.metadata,
                        "text": match.metadata.get("text_preview", "")
                    }
                    for match in results.matches
                ]
            
            elif self.db_type == "chroma":
                results = self.adapter.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k
                )
                
                return [
                    {
                        "id": results["ids"][0][i],
                        "score": results["distances"][0][i],
                        "text": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i]
                    }
                    for i in range(len(results["ids"][0]))
                ]
        except Exception as e:
            print(f"⚠️  Vector search error: {str(e)}")
            return []

# ============================================================================
# HYBRID RETRIEVER
# ============================================================================

class HybridRetriever:
    """Combines graph and vector retrieval for optimal results"""
    
    def __init__(self):
        self.graph_retriever = JsonGraphRetriever()
        self.vector_retriever = VectorRetriever()
    
    def retrieve(self, query: str, top_k: int = 5) -> Dict:
        """
        Perform hybrid retrieval combining graph and vector search
        
        Args:
            query: User question
            top_k: Number of results
            
        Returns:
            Comprehensive context with graph and vector results
        """
        
        print(f"\n🔍 Retrieving context for: '{query}'")
        
        context = {
            "query": query,
            "graph_results": [],
            "vector_results": [],
            "fused_results": []
        }
        
        # Extract entities from query
        print("  → Extracting entities from query...")
        entities = self.graph_retriever.extract_entities_from_query(query)
        
        # Graph-based retrieval
        if entities.get("entities"):
            print(f"  → Found {len(entities['entities'])} entities, searching graph...")
            for entity in entities["entities"]:
                entity_name = entity.get("name")
                results = self.graph_retriever.search_by_entity(entity_name)
                context["graph_results"].extend(results)
        
        # Vector-based retrieval
        print("  → Performing semantic search...")
        vector_results = self.vector_retriever.search(query, top_k)
        context["vector_results"] = vector_results
        
        # Fuse results
        print("  → Fusing and ranking results...")
        fused = self._fuse_results(context["graph_results"], context["vector_results"])
        context["fused_results"] = fused[:top_k]
        
        print(f"✅ Retrieved {len(context['fused_results'])} results")
        
        return context
    
    def _fuse_results(self, graph_results: List, vector_results: List) -> List[Dict]:
        """
        Fuse graph and vector results with ranking
        
        Args:
            graph_results: Results from graph search
            vector_results: Results from vector search
            
        Returns:
            Ranked combined results
        """
        
        fused = []
        
        # Add vector results with confidence scores
        for vr in vector_results:
            fused.append({
                "source": "vector",
                "score": vr.get("score", 0),
                "content": vr.get("text", ""),
                "metadata": vr.get("metadata", {})
            })
        
        # Add graph results (lower priority)
        for i, gr in enumerate(graph_results):
            fused.append({
                "source": "graph",
                "score": 0.5 - (i * 0.05),  # Decreasing score
                "content": json.dumps(gr),
                "metadata": {}
            })
        
        # Sort by score (descending)
        fused.sort(key=lambda x: x["score"], reverse=True)
        
        # Remove duplicates based on content
        unique_results = []
        seen_content = set()
        
        for result in fused:
            content_hash = hash(result["content"][:100])
            if content_hash not in seen_content:
                unique_results.append(result)
                seen_content.add(content_hash)
        
        return unique_results
    
    def close(self):
        """Close all connections"""
        self.graph_retriever.close()

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Initialize hybrid retriever
    retriever = HybridRetriever()
    
    # Example queries
    test_queries = [
        "What are the tax obligations for a freelancer?",
        "What is the VAT registration threshold?",
        "When do I need to file my annual tax return?"
    ]
    
    for query in test_queries:
        context = retriever.retrieve(query, top_k=5)
        print(f"\n📊 Context for: {query}")
        print(f"   Graph results: {len(context['graph_results'])}")
        print(f"   Vector results: {len(context['vector_results'])}")
        print(f"   Fused results: {len(context['fused_results'])}")
    
    retriever.close()
