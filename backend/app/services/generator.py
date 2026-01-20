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
from app.services.rag_pipeline import GraphRAGPipeline
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
1. GREETINGS: For general greetings (e.g., "hi", "hello"), respond briefly and naturally as a professional assistant. Do NOT use the detailed structured format for simple greetings.
2. ACCURATE MATH: If you need to perform any calculation (tax amounts, percentages, totals), DO NOT do the math yourself. Instead, wrap the mathematical expression in a calculation tag like this: [[CALC: 5000000 * 0.24]]. I will execute it and provide the result to the user.
3. KNOWLEDGE FALLBACK: If "External Knowledge" is provided in the context, use it to supplement your answer when local data is missing, but prioritize local official documents.
4. DATA & NUMBERS: Use tax rates (%), income bands (₦), and deadlines from the context for tax queries. 
5. CITATIONS: You MUST mention the document name and page number for every major claim in tax-related answers.
6. NO LEGAL ADVICE: Remind users to consult FIRS and professionals for official filings.
"""

RESPONSE_TEMPLATE = """
Context from official documents:
{context}

External Knowledge (Fallback):
{external_knowledge}

Conversation History:
{history}

User Question: {query}

Instructions:
- If this is a simple greeting or non-tax question, be brief and conversational.
- For tax calculations, use the [[CALC: expression]] format for accuracy.
- If this is a technical tax question, provide a detailed data-driven response:
  1. Summary Answer
  2. Technical Breakdown (using numbers/percentages from context)
  3. Actionable Next Steps
  4. Sources: [List of Citations]
"""

GREETING_TEMPLATE = """
Conversation History:
{history}

User Question: {query}

Instructions:
- This is a greeting or general introductory message.
- Respond warmly, briefly, and naturally as NTRIA.
- Briefly mention that you can help with Nigerian Tax Reform questions if appropriate.
- Do NOT use any structured numerical sections or citations.
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
    
    def is_greeting(self, query: str) -> bool:
        """Check if query is a simple greeting"""
        greetings = ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening", "what's up", "howdy"]
        words = query.lower().strip().split()
        if not words:
            return False
        # If query is short and starts with a greeting, or is just a greeting
        return len(words) <= 3 and any(g in query.lower() for g in greetings)

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
        
        # Format context and history
        formatted_history = self.format_history(history)
        external_context = retrieval_context.get("external_knowledge", "No external knowledge found.")
        
        # Decision: Use different template for greetings
        if self.is_greeting(query):
            prompt = GREETING_TEMPLATE.format(
                history=formatted_history,
                query=query
            )
        else:
            formatted_context = self.format_context(retrieval_context)
            prompt = RESPONSE_TEMPLATE.format(
                context=formatted_context,
                external_knowledge=external_context,
                history=formatted_history,
                query=query
            )
        
        try:
            print(f"  → Generating {'greeting' if self.is_greeting(query) else 'tax'} response...")
            
            model = genai.GenerativeModel(self.model)
            full_prompt = f"{self.system_prompt}\n\n{prompt}"
            
            response = model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7 if self.is_greeting(query) else 0.3,
                    max_output_tokens=1500
                )
            )
            
            # Handle cases where Gemini blocks the response
            try:
                response_text = response.text
            except ValueError:
                # If the response was blocked, use the fallback parts
                response_text = "I'm sorry, I cannot provide a detailed tax analysis for that specific input due to safety or formatting constraints. Could you please rephrase your request?"
            
            # Extract sources (only for non-greetings)
            sources = []
            if not self.is_greeting(query):
                sources = self._extract_sources(retrieval_context)
            
            # Calculate confidence
            try:
                confidence = 1.0 if self.is_greeting(query) else self._calculate_confidence(retrieval_context)
            except:
                confidence = 0.5
            
            # Map usage metadata correctly for Gemini
            prompt_tokens = 0
            completion_tokens = 0
            if hasattr(response, 'usage_metadata'):
                prompt_tokens = response.usage_metadata.prompt_token_count
                completion_tokens = response.usage_metadata.candidates_token_count
            
            return {
                "response": response_text,
                "sources": sources,
                "confidence": confidence,
                "model": self.model,
                "input_tokens": prompt_tokens,
                "output_tokens": completion_tokens
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
            scores = [r.get("score") for r in vector_results if r.get("score") is not None]
            if scores:
                avg_score = sum(scores) / len(scores)
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
