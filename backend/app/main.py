"""
FastAPI Backend for NTRIA - Nigeria Tax Reform Intelligence Assistant
Graph RAG Pipeline for Tax Guidance
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat_routes
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="NTRIA API",
    description="Nigeria Tax Reform Intelligence Assistant - Graph RAG Backend",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS Configuration
# Allow all origins for now to ensure Vercel deployment works
ALLOWED_ORIGINS = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    from datetime import datetime
    return {
        "status": "healthy",
        "service": "NTRIA API",
        "version": "1.0.1",
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to NTRIA - Nigeria Tax Reform Intelligence Assistant",
        "docs": "/api/docs",
        "endpoints": {
            "health": "/health",
            "chat": "/api/v1/chat",
            "entities": "/api/v1/entities",
            "graph_search": "/api/v1/graph/search"
        }
    }

# ============================================================================
# ROUTES
# ============================================================================

# TODO: Import and include route blueprints
# from app.routes import chat_routes, graph_routes, analytics_routes
# app.include_router(chat_routes.router)
# app.include_router(graph_routes.router)
# app.include_router(analytics_routes.router)

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return {
        "error": str(exc),
        "status": "error"
    }

# ============================================================================
# STARTUP & SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup"""
    print("🚀 NTRIA API Starting...")
    print("✅ NTRIA API Ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """Close connections on shutdown"""
    print("🛑 NTRIA API Shutting down...")
    print("✅ NTRIA API Closed!")

# ============================================================================
# INCLUDE ROUTES
# ============================================================================

# Register chat routes
app.include_router(chat_routes.router)

# ============================================================================
# RUN DEVELOPMENT SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("BACKEND_PORT", 8000))
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "true").lower() == "true"
    )
