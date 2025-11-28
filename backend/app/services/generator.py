"""
LLM Response Generator Module
Generates human-readable responses from Graph RAG context
"""

import json
import os
from typing import Dict, List, Tuple
from dotenv import load_dotenv
import openai

load_dotenv()

# Initialize OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

# ============================================================================
# PROMPT TEMPLATES
# ============================================================================

SYSTEM_PROMPT = """
You are NTRIA (Nigeria Tax Reform Intelligence Assistant), an expert tax advisor specializing 
in the 2025 Nigerian Tax Reform Act.

Your role is to help Nigerian citizens, students, NYSC participants, and entrepreneurs 
understand their tax obligations and navigate the tax system.

Guidelines:
1. ALWAYS base your answers on the provided context from official tax documents
2. If uncertain or if the context doesn't contain relevant information, clearly state 
   "I don't have complete information on this" rather than speculating
3. Explain tax concepts in simple, plain language
4. Provide actionable next steps when appropriate
5. Always cite the source of your information
6. Use bullet points for clarity when listing multiple items
7. Break down complex processes into steps
8. Acknowledge if a question is outside the scope of tax reform

IMPORTANT: Never provide personal financial or legal advice. Always recommend consulting 
with tax professionals for individual situations.
"""

RESPONSE_TEMPLATE = """
Context from official tax documents:
{context}

User Question:
{query}

Please provide a clear, helpful response based on the above context.
Include citations from the source documents.
"""

# ============================================================================
# RESPONSE GENERATOR
# ============================================================================

class ResponseGenerator:
    """Generates LLM responses from retrieved context"""
    
    def __init__(self):
        self.model = MODEL
        self.system_prompt = SYSTEM_PROMPT
    
    def format_context(self, retrieval_context: Dict) -> str:
        """
        Format retrieved context for LLM
        
        Args:
            retrieval_context: Output from hybrid retriever
            
        Returns:
            Formatted context string
        """
        
        context_parts = []
        
        # Add graph results
        if retrieval_context.get("graph_results"):
            context_parts.append("=== Graph Knowledge ===")
            for result in retrieval_context["graph_results"][:3]:  # Top 3
                context_parts.append(json.dumps(result, indent=2)[:500])  # Truncate
        
        # Add vector results
        if retrieval_context.get("vector_results"):
            context_parts.append("\n=== Relevant Documents ===")
            for result in retrieval_context["vector_results"][:5]:  # Top 5
                text = result.get("text", "")
                if text:
                    context_parts.append(f"• {text[:300]}...")
                
                metadata = result.get("metadata", {})
                source = metadata.get("source")
                page = metadata.get("page")
                if source or page:
                    source_str = f"(Source: {source}"
                    if page:
                        source_str += f", Page {page}"
                    source_str += ")"
                    context_parts.append(source_str)
        
        return "\n".join(context_parts)
    
    def generate_response(self, query: str, retrieval_context: Dict) -> Dict:
        """
        Generate LLM response from context
        
        Args:
            query: User question
            retrieval_context: Output from hybrid retriever
            
        Returns:
            Dictionary with response, sources, confidence, etc.
        """
        
        # Format context
        formatted_context = self.format_context(retrieval_context)
        
        # Build prompt
        prompt = RESPONSE_TEMPLATE.format(
            context=formatted_context,
            query=query
        )
        
        try:
            print("  → Generating response with LLM...")
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1500
            )
            
            response_text = response.choices[0].message.content
            
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
