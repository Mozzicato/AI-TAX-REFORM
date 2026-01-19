"""
Graph RAG Pipeline
Orchestrates the retrieval and generation process
"""

from app.services.retriever import HybridRetriever
from app.services.generator import ResponseGenerator
from typing import Dict, List, Optional

class GraphRAGPipeline:
    def __init__(self):
        self.retriever = HybridRetriever()
        self.generator = ResponseGenerator()

    def answer_query(self, query: str, history: List[Dict] = None) -> Dict:
        """
        Process a user query through the RAG pipeline
        """
        # 1. Retrieve context
        # We pass history to retriever to help with query refinement/context
        retrieval_context = self.retriever.retrieve(query, history=history)
        
        # 2. Generate answer with history awareness
        result = self.generator.generate_response(query, retrieval_context, history=history)
        
        # 3. Format result for API
        return {
            "answer": result["response"],  # Map response to answer
            "sources": result.get("sources", []),
            "confidence": result.get("confidence", 0.0),
            "retrieval_stats": {
                "graph_nodes": len(retrieval_context.get("graph_results", [])),
                "vector_docs": len(retrieval_context.get("vector_results", []))
            }
        }

_pipeline_instance = None

def get_rag_pipeline():
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = GraphRAGPipeline()
    return _pipeline_instance
