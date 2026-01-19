"""
LLM Response Generator Module
Generates human-readable responses from Graph RAG context
"""

import json
import os
from typing import Dict, List, Tuple
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Initialize Gemini
from app.config import get_settings
settings = get_settings()
if settings.google_api_key:
    genai.configure(api_key=settings.google_api_key)
MODEL = "gemma-3-27b-it"

# ============================================================================
# PROMPT TEMPLATES
# ============================================================================

SYSTEM_PROMPT = """
You are NTRIA (Nigeria Tax Reform Intelligence Assistant), a tax expert for the 2025 Nigerian Tax Reform.

Guidelines:
1. DATA & NUMBERS: Use tax rates (%), income bands (₦), and deadlines from the context. If a user provides income, estimate their tax using the tables in the context.
2. CITATIONS: You MUST mention the document name and page number for every major claim.
3. ADVICE: If specific detail is missing, apply the general principles of the 2025 Act (e.g., higher income usually means higher tax bands).
4. TONE: Professional and conversational.
5. NO LEGAL ADVICE: Remind users to consult FIRS and professionals for official filings.
"""

RESPONSE_TEMPLATE = """
Context from official documents:
{context}

Conversation History:
{history}

User Question: {query}

Please provide a detailed, data-driven response. 
Format:
1. Summary Answer
2. Technical Breakdown (using numbers/percentages from context)
3. Actionable Next Steps
4. Sources: [List of Citations]
"""

# ============================================================================
# RESPONSE GENERATOR
# ============================================================================

class ResponseGenerator:
    """Generates LLM responses from retrieved context"""
    
    def __init__(self):
        self.model = MODEL
        self.system_prompt = SYSTEM_PROMPT
    
    def format_history(self, history: List[Dict]) -> str:
        """Format conversation history for prompt"""
        if not history:
            return "No previous history."
        
        # Take last 10 messages to provide deep context within the session
        history_parts = []
        for msg in history[-10:]:
            role = "User" if msg.get("role") == "user" else "Assistant"
            content = msg.get("content", "")
            history_parts.append(f"{role}: {content}")
        
        return "\n".join(history_parts)
    
    def format_context(self, retrieval_context: Dict) -> str:
        """
        Format retrieved context for LLM with expanded length for better data capture.
        """
        context_parts = []
        
        # Add graph results (if any)
        if retrieval_context.get("graph_results"):
            context_parts.append("=== Graph Knowledge ===")
            for result in retrieval_context["graph_results"][:5]:
                context_parts.append(json.dumps(result, indent=2))
        
        # Add vector results (Expanded to 1500 chars to catch tables/lists)
        if retrieval_context.get("vector_results"):
            context_parts.append("\n=== Detailed Tax Documents ===")
            for i, result in enumerate(retrieval_context["vector_results"][:6]):
                text = result.get("text", "")
                metadata = result.get("metadata", {})
                source = metadata.get("source", "Unknown Document")
                page = metadata.get("page", "Unknown Page")
                
                if text:
                    # Capture much more text so tables/tax bands aren't cut off
                    context_parts.append(f"[Document {i+1}: {source} (Page {page})]\n{text[:1500]}")
        
        if not context_parts:
            return "No specific tax documents found for this query."
            
        return "\n\n".join(context_parts)
    
    def generate_response(self, query: str, retrieval_context: Dict, history: List[Dict] = None) -> Dict:
        """
        Generate LLM response from context
        
        Args:
            query: User question
            retrieval_context: Output from hybrid retriever
            history: Optional conversation history
            
        Returns:
            Dictionary with response, sources, confidence, etc.
        """
        
        # Format context
        formatted_context = self.format_context(retrieval_context)
        formatted_history = self.format_history(history)
        
        # Build prompt
        prompt = RESPONSE_TEMPLATE.format(
            context=formatted_context,
            history=formatted_history,
            query=query
        )
        
        try:
            print("  → Generating response with Gemini...")
            
            model = genai.GenerativeModel(self.model)
            full_prompt = f"{self.system_prompt}\n\n{prompt}"
            
            response = model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.5,
                    max_output_tokens=1500
                )
            )
            
            response_text = response.text
            
            # Extract sources
            sources = self._extract_sources(retrieval_context)
            
            # Calculate confidence
            confidence = self._calculate_confidence(retrieval_context)
            
            return {
                "response": response_text,
                "sources": sources,
                "confidence": confidence,
                "model": self.model,
                "input_tokens": response.usage.prompt_tokens if hasattr(response, 'usage') else 0,
                "output_tokens": response.usage.completion_tokens if hasattr(response, 'usage') else 0
            }
            
        except Exception as e:
            print(f"❌ Error generating response: {str(e)}")
            return {
                "response": f"I encountered an error: {str(e)}",
                "sources": [],
                "confidence": 0.0,
                "error": True
            }
    
    def _extract_sources(self, retrieval_context: Dict) -> List[Dict]:
        """Extract source information from context"""
        
        sources = []
        seen_sources = set()
        
        for result in retrieval_context.get("vector_results", []):
            metadata = result.get("metadata", {})
            source = metadata.get("source")
            page = metadata.get("page")
            
            if source:
                source_key = f"{source}_{page}"
                if source_key not in seen_sources:
                    sources.append({
                        "title": source,
                        "page": page,
                        "type": "document"
                    })
                    seen_sources.add(source_key)
        
        return sources
    
    def _calculate_confidence(self, retrieval_context: Dict) -> float:
        """
        Calculate confidence score based on retrieval results
        
        Args:
            retrieval_context: Retrieval output
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        
        # Base confidence
        confidence = 0.5
        
        # Boost if we have graph results
        if retrieval_context.get("graph_results"):
            confidence += 0.2
        
        # Boost based on vector scores
        vector_results = retrieval_context.get("vector_results", [])
        if vector_results:
            avg_score = sum(r.get("score", 0) for r in vector_results) / len(vector_results)
            confidence += min(avg_score, 0.3)  # Cap at +0.3
        
        return min(confidence, 1.0)  # Ensure max 1.0
    
    def validate_response(self, response_text: str, context: str) -> Tuple[bool, str]:
        """
        Validate response for hallucinations
        
        Args:
            response_text: Generated response
            context: Retrieved context
            
        Returns:
            Tuple of (is_valid, issue_description)
        """
        
        # Simple validation checks
        if not response_text:
            return False, "Empty response"
        
        if len(response_text) < 50:
            return False, "Response too short"
        
        # Check if response seems to be refusing to answer (negative indicator)
        if any(phrase in response_text.lower() for phrase in [
            "i cannot", "i cannot answer", "not available", "no information"
        ]):
            # This might be appropriate - not necessarily invalid
            pass
        
        # Check for obviously wrong statements
        if "i don't know" not in response_text.lower() and not context:
            return False, "No context but confident answer"
        
        return True, "Valid response"

# ============================================================================
# GRAPH RAG ORCHESTRATOR
# ============================================================================

class GraphRAGPipeline:
    """Orchestrates the complete Graph RAG pipeline"""
    
    def __init__(self):
        from backend.app.services.retriever import HybridRetriever
        self.retriever = HybridRetriever()
        self.generator = ResponseGenerator()
    
    def answer_query(self, query: str) -> Dict:
        """
        Complete pipeline: retrieve context → generate response → validate
        
        Args:
            query: User question
            
        Returns:
            Complete answer with context and metadata
        """
        
        print(f"\n🔄 Graph RAG Pipeline Processing...")
        print(f"   Query: {query}\n")
        
        # Step 1: Retrieve context
        print("1️⃣  Retrieving context...")
        retrieval_context = self.retriever.retrieve(query, top_k=5)
        
        # Step 2: Generate response
        print("2️⃣  Generating response...")
        response_data = self.generator.generate_response(query, retrieval_context)
        
        # Step 3: Validate response
        print("3️⃣  Validating response...")
        is_valid, validation_msg = self.generator.validate_response(
            response_data["response"],
            str(retrieval_context)
        )
        
        if not is_valid:
            print(f"   ⚠️  Validation warning: {validation_msg}")
        
        # Combine everything
        result = {
            "query": query,
            "answer": response_data["response"],
            "sources": response_data.get("sources", []),
            "confidence": response_data.get("confidence", 0.0),
            "valid": is_valid,
            "retrieval_stats": {
                "graph_results": len(retrieval_context.get("graph_results", [])),
                "vector_results": len(retrieval_context.get("vector_results", [])),
                "fused_results": len(retrieval_context.get("fused_results", []))
            }
        }
        
        print(f"\n✅ Pipeline completed")
        print(f"   Confidence: {result['confidence']:.2%}")
        print(f"   Sources: {len(result['sources'])}")
        
        return result
    
    def close(self):
        """Close all connections"""
        self.retriever.close()

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Initialize pipeline
    pipeline = GraphRAGPipeline()
    
    # Test queries
    test_queries = [
        "What are the tax obligations for a freelancer earning ₦2M annually?",
        "What is the VAT registration threshold?",
        "When do I need to file my annual tax return?"
    ]
    
    for query in test_queries:
        print("\n" + "="*70)
        result = pipeline.answer_query(query)
        
        print(f"\n📝 ANSWER:")
        print(result["answer"][:500])
        if len(result["answer"]) > 500:
            print("...")
        
        print(f"\n📚 SOURCES ({len(result['sources'])}):")
        for source in result["sources"]:
            print(f"   • {source['title']} (Page {source.get('page', 'N/A')})")
    
    pipeline.close()
