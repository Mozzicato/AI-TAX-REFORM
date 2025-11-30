"""
Graph RAG Pipeline for NTRIA
Combines Pinecone vector search, JSON graph, and Gemini for answers.
"""

import os
import json
import re
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# Import our services
from .pinecone_service import get_pinecone_service
from .graph_service import get_graph_service

# Gemini configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


class GraphRAGPipeline:
    """
    Graph-enhanced RAG pipeline for tax questions.
    
    Flow:
    1. Search Pinecone for relevant document chunks
    2. Search JSON graph for related entities
    3. Combine context and generate answer with Gemini
    """
    
    def __init__(self):
        """Initialize the pipeline components."""
        self.pinecone = get_pinecone_service()
        self.graph = get_graph_service()
        self.gemini_model = None
        
        # Initialize Gemini
        self._init_gemini()
    
    def _init_gemini(self):
        """Initialize Google Gemini client."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            # Try to use the latest available model
            try:
                self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
            except Exception:
                # Fallback to gemini-1.5-pro if gemini-2.0-flash is not available
                self.gemini_model = genai.GenerativeModel('gemini-1.5-pro')
            print("✅ Gemini initialized")
        except Exception as e:
            print(f"❌ Gemini initialization failed: {e}")
            self.gemini_model = None

    def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribe audio file using Gemini.
        """
        try:
            import google.generativeai as genai
            
            # Upload the file
            # Note: In a real prod env, we should manage file lifecycle (delete after use)
            audio_file = genai.upload_file(path=audio_path)
            
            prompt = "Transcribe this audio message exactly. Do not add any commentary."
            
            response = self.gemini_model.generate_content([prompt, audio_file])
            return response.text.strip()
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return ""
    
    def rewrite_query(self, query: str, history: List[Dict]) -> str:
        """
        Rewrite query to be standalone based on history.
        """
        if not history or not self.gemini_model:
            return query
            
        try:
            history_text = "\n".join([f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in history[-4:]])
            prompt = f"""Given the following conversation history and a follow-up question, rephrase the follow-up question to be a standalone question that captures all necessary context.
            
History:
{history_text}

Follow-up: {query}

Standalone Question:"""
            
            response = self.gemini_model.generate_content(prompt)
            rewritten = response.text.strip()
            print(f"🔄 Rewrote query: '{query}' -> '{rewritten}'")
            return rewritten
        except Exception as e:
            print(f"⚠️ Query rewrite failed: {e}")
            return query

    def retrieve_from_pinecone(
        self, 
        query: str, 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents from Pinecone.
        
        Args:
            query: User question
            top_k: Number of results
            
        Returns:
            List of matching documents with scores
        """
        if not self.pinecone.initialized:
            return []
        
        try:
            results = self.pinecone.search(
                query=query,
                top_k=top_k,
                namespace="tax-docs"
            )
            return results
        except Exception as e:
            print(f"❌ Pinecone search error: {e}")
            return []
    
    def retrieve_from_graph(
        self, 
        query: str, 
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve related entities from knowledge graph.
        
        Args:
            query: User question
            max_results: Maximum entities to return
            
        Returns:
            List of relevant entities with their relationships
        """
        try:
            # Search for matching entities
            entities = self.graph.search_nodes(query)[:max_results]
            
            # Get related entities for each match
            enriched = []
            for entity in entities:
                related = self.graph.get_related_nodes(entity["id"])
                enriched.append({
                    "entity": entity,
                    "related": related[:5]  # Limit related entities
                })
            
            return enriched
        except Exception as e:
            print(f"❌ Graph search error: {e}")
            return []
    
    def generate_answer(
        self, 
        query: str, 
        context_docs: List[Dict], 
        context_entities: List[Dict],
        history: List[Dict] = None
    ) -> str:
        """
        Generate answer using Gemini with retrieved context and conversation history.
        
        Args:
            query: User question
            context_docs: Documents from Pinecone
            context_entities: Entities from knowledge graph
            history: List of previous messages [{"role": "user", "content": "..."}]
            
        Returns:
            Generated answer text
        """
        if not self.gemini_model:
            return "Sorry, I'm having trouble generating a response. Please try again later."
        
        # Build context from documents
        doc_context = ""
        for i, doc in enumerate(context_docs[:5], 1):
            text = doc.get("text", doc.get("metadata", {}).get("text", ""))
            doc_context += f"\n[Document {i}]: {text[:1000]}\n"
        
        # Build context from entities
        entity_context = ""
        for item in context_entities[:3]:
            entity = item.get("entity", {})
            related = item.get("related", [])
            entity_context += f"\n[Entity: {entity.get('name', 'Unknown')}]\n"
            entity_context += f"  Type: {entity.get('type', 'Unknown')}\n"
            if related:
                entity_context += f"  Related to: {', '.join([r.get('name', '') for r in related[:3]])}\n"
        
        # Build history context
        history_context = ""
        if history:
            history_context = "=== CONVERSATION HISTORY ===\n"
            # Take last 3 turns (6 messages)
            for msg in history[-6:]:
                role = msg.get("role", "unknown").upper()
                content = msg.get("content", "")
                history_context += f"{role}: {content}\n"
        
        # Compose prompt
        prompt = f"""You are NTRIA, the Nigeria Tax Reform Intelligence Assistant. 
You help users understand the Nigeria Tax Reform Act 2025.

Based on the following context and conversation history, answer the user's question accurately and helpfully.
If the context doesn't contain enough information to answer, say so honestly.
Always cite specific sections, articles, or rates when available.

{history_context}

=== DOCUMENT CONTEXT ===
{doc_context if doc_context else "No relevant documents found."}

=== KNOWLEDGE GRAPH CONTEXT ===
{entity_context if entity_context else "No related entities found."}

=== USER QUESTION ===
{query}

=== YOUR ANSWER ===
Provide a clear, accurate, and helpful response:
"""
        
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"❌ Gemini generation error: {e}")
            return f"I encountered an error generating a response: {str(e)}"
    
    def answer_query(
        self, 
        query: str,
        use_graph: bool = True,
        use_vector: bool = True,
        top_k: int = 5,
        history: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Main entry point - answer a user query using Graph RAG.
        
        Args:
            query: User question
            use_graph: Whether to use knowledge graph
            use_vector: Whether to use vector search
            top_k: Number of results per retrieval
            history: Conversation history
            
        Returns:
            Dict with answer, sources, confidence, and stats
        """
        # Retrieve context
        vector_results = []
        graph_results = []
        
        # Rewrite query if history exists
        search_query = query
        if history:
            search_query = self.rewrite_query(query, history)
        
        if use_vector:
            vector_results = self.retrieve_from_pinecone(search_query, top_k)
        
        if use_graph:
            graph_results = self.retrieve_from_graph(search_query, top_k)
        
        # Generate answer
        answer = self.generate_answer(query, vector_results, graph_results, history)
        
        # Build sources from retrieved documents
        sources = []
        for doc in vector_results[:3]:
            metadata = doc.get("metadata", {})
            text = doc.get("text", metadata.get("text", ""))
            
            # Try to extract section from text if missing in metadata
            section = metadata.get("section", metadata.get("chunk_id", ""))
            if not section or section == "":
                # Look for "144. " or "Section 144" pattern
                match = re.search(r'(?:^|\s)(\d+)\.\s+[A-Z]', text)
                if match:
                    section = f"Section {match.group(1)}"
            
            sources.append({
                "title": metadata.get("source", metadata.get("document_id", "Tax Document")),
                "section": section,
                "type": "document",
                "score": doc.get("score", 0)
            })
        
        # Calculate confidence based on retrieval scores
        if vector_results:
            avg_score = sum(d.get("score", 0) for d in vector_results) / len(vector_results)
            confidence = min(0.95, avg_score)
        else:
            confidence = 0.3 if graph_results else 0.1
        
        return {
            "query": query,
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
            "valid": True,
            "retrieval_stats": {
                "vector_results": len(vector_results),
                "graph_results": len(graph_results),
                "fused_results": len(vector_results) + len(graph_results)
            }
        }


# Singleton instance
_pipeline = None

def get_rag_pipeline() -> GraphRAGPipeline:
    """Get or create RAG pipeline instance."""
    global _pipeline
    if _pipeline is None:
        _pipeline = GraphRAGPipeline()
    return _pipeline


# Quick test
if __name__ == "__main__":
    pipeline = get_rag_pipeline()
    
    print("\n🧪 Testing RAG Pipeline...")
    result = pipeline.answer_query("What is the VAT rate in Nigeria?")
    
    print(f"\n📝 Query: {result['query']}")
    print(f"\n💬 Answer: {result['answer']}")
    print(f"\n📊 Confidence: {result['confidence']:.2f}")
    print(f"\n📚 Sources: {json.dumps(result['sources'], indent=2)}")
    print(f"\n📈 Stats: {result['retrieval_stats']}")
