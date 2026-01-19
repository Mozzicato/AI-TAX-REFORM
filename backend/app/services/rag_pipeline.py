"""
Graph RAG Pipeline
Orchestrates the retrieval and generation process
"""

from app.services.retriever import HybridRetriever
from app.services.generator import ResponseGenerator
from app.services.tools import TaxCalculator, UniversalSearch
from typing import Dict, List, Optional
import re

class GraphRAGPipeline:
    def __init__(self):
        self.retriever = HybridRetriever()
        self.generator = ResponseGenerator()
        self.calculator = TaxCalculator()
        self.searcher = UniversalSearch()

    def _should_calculate(self, query: str) -> bool:
        """Check if the query involves mathematical calculation"""
        math_keywords = ["calculate", "sum", "total", "tax on", "how much is", "plus", "minus", "*", "/"]
        return any(kw in query.lower() for kw in math_keywords)

    def answer_query(self, query: str, history: List[Dict] = None) -> Dict:
        """
        Process a user query through the RAG pipeline with search and calc fallback
        """
        # OPTIMIZATION: Don't search for simple greetings to save Serper quota
        is_basic_query = self.generator.is_greeting(query)
        
        # 1. Retrieve local context
        retrieval_context = self.retriever.retrieve(query, history=history)
        
        # 2. Check for knowledge gap - Fallback to Web Search ONLY if local RAG has nothing
        # and it's not a basic greeting.
        if not is_basic_query and not retrieval_context.get("vector_results") and not retrieval_context.get("graph_results"):
            print(f"🔍 No local context for '{query}'. Attempting external search to be sharp...")
            external_info = self.searcher.search(query)
            if external_info:
                retrieval_context["external_knowledge"] = external_info

        # 3. Handle Precise Calculation if needed
        # If query looks like math, we can ask the LLM to provide a formula or we inject context
        if self._should_calculate(query):
             retrieval_context["math_tool_status"] = "enabled"

        # 4. Generate answer
        result = self.generator.generate_response(query, retrieval_context, history=history)
        answer = result["response"]

        # 5. Post-process for math execution
        # Look for [[CALC: expr]] in the response and replace with result
        if "[[CALC:" in answer:
            matches = re.findall(r"\[\[CALC:\s*(.*?)\s*\]\]", answer)
            for expr in matches:
                calc_result = self.calculator.calculate(expr)
                answer = answer.replace(f"[[CALC: {expr}]]", calc_result)
                answer = answer.replace(f"[[CALC:{expr}]]", calc_result)
        
        # 6. Format result for API
        return {
            "answer": answer,
            "sources": result.get("sources", []),
            "confidence": result.get("confidence", 0.0),
            "retrieval_stats": {
                "graph_nodes": len(retrieval_context.get("graph_results", [])),
                "vector_docs": len(retrieval_context.get("vector_results", [])),
                "external_search": "external_knowledge" in retrieval_context
            }
        }

_pipeline_instance = None

def get_rag_pipeline():
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = GraphRAGPipeline()
    return _pipeline_instance
