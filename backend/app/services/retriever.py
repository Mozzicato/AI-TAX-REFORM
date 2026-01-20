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
from app.config import get_settings
settings = get_settings()
if settings.google_api_key:
    genai.configure(api_key=settings.google_api_key)
MODEL = "gemma-3-27b-it"
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
        self.db_type = os.getenv("VECTOR_DB_TYPE", "json").lower()
        self.adapter = self._init_adapter()
    
    def _init_adapter(self):
        """Initialize vector database adapter"""
        if self.db_type == "pinecone":
            try:
                import pinecone
                # ... existing pinecone init ...
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
            print("⚠️  Chroma support has been removed from this codebase. Use 'json' or 'pinecone' as VECTOR_DB_TYPE.")
            return None
        
        elif self.db_type == "json":
            try:
                # Add local JSON adapter support
                from scripts.generate_embeddings import JSONGraphAdapter
                adapter = JSONGraphAdapter()
                return adapter
            except Exception as e:
                print(f"⚠️  JSON Adapter error: {str(e)}")
                return None
        
        return None

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search vector database for similar documents
        """
        if not self.adapter:
            return []
        
        if self.db_type == "json":
            # Local JSON adapter uses raw text for keyword search
            return self.adapter.search(query, top_k=top_k)
        
        # Other adapters use embeddings
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
                        "text": match.metadata.get("text") or match.metadata.get("text_preview") or ""
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
        self.model = MODEL

    def _refine_and_extract(self, query: str, history: List[Dict] = None) -> Dict:
        """
        Refines the query and extracts entities in a single AI call to save RPM.
        """
        history_str = ""
        if history:
            for msg in history[-3:]:
                role = "User" if msg.get("role") == "user" else "Assistant"
                history_str += f"{role}: {msg.get('content')}\n"

        prompt = f"""
        Analyze the following conversation and follow-up question.
        1. REPHRASE the question into a standalone tax search query.
        2. EXTRACT tax-related entities (Tax names, Agencies, Income types).

        Conversation History:
        {history_str}
        
        Follow-up Question: {query}

        Return ONLY a JSON object:
        {{
          "standalone_query": "the rephrased question",
          "entities": [
            {{"name": "entity_name", "type": "Tax|Agency|etc"}}
          ]
        }}
        """
        
        try:
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(temperature=0.1))
            result = json.loads(response.text.replace("```json", "").replace("```", "").strip())
            print(f"🔄 Integrated Analysis: {result['standalone_query']}")
            return result
        except Exception as e:
            print(f"⚠️  Analysis error: {str(e)}")
            return {"standalone_query": query, "entities": []}

    def retrieve(self, query: str, top_k: int = 5, history: List[Dict] = None) -> Dict:
        """
        Perform hybrid retrieval with optimized API calls.
        """
        # OPTIMIZATION: Skip AI refinement for very short/simple queries to save quota
        if len(query.strip().split()) <= 3 and (not history or len(history) == 0):
            search_query = query
            analysis = {"standalone_query": query, "entities": []}
        else:
            # Single AI call for both refinement and entities
            analysis = self._refine_and_extract(query, history)
            search_query = analysis.get("standalone_query", query)
        
        print(f"\n🔍 Searching for: '{search_query}'")
        
        context = {
            "query": query,
            "search_query": search_query,
            "graph_results": [],
            "vector_results": [],
            "fused_results": []
        }
        
        # Graph-based retrieval using extracted entities
        entities = analysis.get("entities", [])
        if entities:
            print(f"  → Found {len(entities)} entities")
            for entity in entities:
                results = self.graph_retriever.search_by_entity(entity.get("name"))
                context["graph_results"].extend(results)
        
        # Vector-based retrieval
        print("  → Performing semantic search...")
        vector_results = self.vector_retriever.search(search_query, top_k)
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
