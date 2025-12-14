"""
FastAPI Chat Routes
Main API endpoints for the Graph RAG chatbot
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/api/v1", tags=["chat"])

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class Message(BaseModel):
    """Single chat message"""
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message text")
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    """Chat request payload"""
    message: str = Field(..., description="User query")
    session_id: Optional[str] = Field(None, description="User session ID")
    conversation_history: Optional[List[Message]] = Field(None, description="Previous messages")
    context: Optional[dict] = Field(None, description="Additional context")

class Source(BaseModel):
    """Citation source"""
    title: str
    page: Optional[int] = None
    section: Optional[str] = None
    type: str = "document"

class ChatResponse(BaseModel):
    """Chat response payload"""
    answer: str
    sources: List[Source] = []
    confidence: float = Field(..., ge=0.0, le=1.0)
    session_id: Optional[str] = None
    retrieval_stats: Optional[dict] = None
    valid: bool = True

# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint - Process user query through Graph RAG pipeline
    
    Args:
        request: Chat request with message and optional context
        
    Returns:
        Chat response with answer, sources, and confidence
    """
    
    try:
        if not request.message or len(request.message.strip()) < 2:
            raise HTTPException(
                status_code=400,
                detail="Message must be at least 2 characters"
            )
        
        # Check if we're in demo mode
        from app.config import get_settings
        settings = get_settings()
        
        if settings.demo_mode:
            # Use demo service
            from app.services.demo_service import DemoService
            demo = DemoService()
            result = demo.get_demo_response(request.message)
            
            # Convert sources
            sources = [
                Source(**source) for source in result.get("sources", [])
            ]
            
            return ChatResponse(
                answer=result["answer"],
                sources=sources,
                confidence=result["confidence"],
                session_id=request.session_id,
                retrieval_stats=result.get("retrieval_stats"),
                valid=result.get("valid", True)
            )
        
        # Use the demo service or RAG pipeline based on config  
        from app.config import get_settings
        settings = get_settings()
        
        if settings.demo_mode:
            # Use demo service when API keys are missing
            from app.services.demo_service import DemoService
            demo_service = DemoService()
            result = demo_service.get_demo_response(request.message)
        else:
            # Use the Graph RAG pipeline
            from app.services.rag_pipeline import get_rag_pipeline
            pipeline = get_rag_pipeline()
            
            # Convert Pydantic models to dicts for the pipeline
            history = []
            if request.conversation_history:
                history = [
                    {"role": msg.role, "content": msg.content} 
                    for msg in request.conversation_history
                ]
                
            result = pipeline.answer_query(
                query=request.message,
                history=history
            )
        
        # Convert sources
        sources = [
            Source(**source) for source in result.get("sources", [])
        ]
        
        return ChatResponse(
            answer=result["answer"],
            sources=sources,
            confidence=result["confidence"],
            session_id=request.session_id,
            retrieval_stats=result.get("retrieval_stats"),
            valid=result.get("valid", True)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )

@router.get("/entities")
async def get_entities(entity_type: Optional[str] = None) -> dict:
    """
    Get available tax entities from knowledge graph
    
    Args:
        entity_type: Optional filter by entity type
        
    Returns:
        Dictionary of entities grouped by type
    """
    
    try:
        # Use JSON graph for entity retrieval
        from app.services.json_graph import get_json_graph
        graph = get_json_graph()
        entities = graph.get_all_entities(entity_type)
        
        # Return mock if no entities found
        entities = {
            "Tax": ["VAT", "PAYE", "DST", "Capital Gains Tax"],
            "Taxpayer": ["Individual", "Freelancer", "SME", "Digital Service Provider"],
            "Agency": ["FIRS", "JTB", "State IRS"],
            "Process": ["VAT Registration", "PAYE Filing", "Annual Return"]
        }
        
        if entity_type and entity_type in entities:
            return {entity_type: entities[entity_type]}
        
        return entities
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching entities: {str(e)}"
        )

@router.post("/graph/search")
async def graph_search(query: dict) -> dict:
    """
    Search the knowledge graph with custom Cypher query
    
    Args:
        query: Dictionary with 'cypher' key containing Cypher query
        
    Returns:
        Query results
    """
    
    try:
        cypher = query.get("cypher")
        if not cypher:
            raise HTTPException(
                status_code=400,
                detail="Missing 'cypher' field in request body"
            )
        
        # TODO: Execute Cypher query
        # from app.services.retriever import GraphRetriever
        # retriever = GraphRetriever()
        # results = retriever.execute_query(cypher)
        
        # Temporary mock
        results = {"matches": []}
        
        return {"results": results}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error executing query: {str(e)}"
        )

@router.get("/analytics")
async def analytics(time_period: str = "day") -> dict:
    """
    Get analytics and usage statistics
    
    Args:
        time_period: 'hour', 'day', 'week', 'month'
        
    Returns:
        Analytics data
    """
    
    try:
        # TODO: Query analytics from database
        analytics_data = {
            "time_period": time_period,
            "total_queries": 0,
            "average_confidence": 0.0,
            "top_questions": [],
            "entity_frequency": {},
            "performance_metrics": {
                "avg_response_time": 0.0,
                "p95_response_time": 0.0,
                "error_rate": 0.0
            }
        }
        
        return analytics_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching analytics: {str(e)}"
        )

# ============================================================================
# HEALTH CHECK & INFO
# ============================================================================

@router.get("/status")
async def status() -> dict:
    """Get API status and component health"""
    
    from datetime import datetime
    
    status_info = {
        "api": "healthy",
        "components": {
            "json_graph": "ready",
            "vector_db": "ready",
            "openai": "ready"
        },
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return status_info

@router.get("/info")
async def info() -> dict:
    """Get API information"""
    
    return {
        "name": "NTRIA API",
        "description": "Nigeria Tax Reform Intelligence Assistant - Graph RAG Backend",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/v1/chat",
            "entities": "/api/v1/entities",
            "graph_search": "/api/v1/graph/search",
            "analytics": "/api/v1/analytics",
            "status": "/api/v1/status",
            "docs": "/api/docs",
            "redoc": "/api/redoc"
        },
        "models": {
            "language_model": os.getenv("OPENAI_MODEL", "gpt-4"),
            "embedding_model": os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        }
    }
