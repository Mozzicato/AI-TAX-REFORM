"""
AI Tax Reform API - Backend Service

A comprehensive Flask API for Nigerian tax calculations and AI-powered Q&A
about Nigerian tax law based on the Nigeria Tax Act 2025.
"""

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from pathlib import Path
import os
import time
import logging
import re
from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# ============================================================================
# App Configuration
# ============================================================================

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1MB max request size

# CORS Configuration - Secure defaults
allowed_origins = os.getenv("CORS_ORIGINS", "").strip()
if allowed_origins:
    origins = [o.strip() for o in allowed_origins.split(",") if o.strip()]
else:
    origins = ["http://localhost:3000", "http://localhost:7860"]

CORS(app, origins=origins, supports_credentials=True)

# Rate Limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# ============================================================================
# Imports (after app initialization)
# ============================================================================

from src.tax_calculator import calculate_tax, get_tax_summary, TaxCalculationError
from scripts.query_qa import load_vectorstore, query
from scripts.qa_service import generate_answer, verify_answer
import threading

# ============================================================================
# Vectorstore Cache
# ============================================================================

_vectorstore_cache: Optional[Tuple[Any, Any]] = None
_vectorstore_loading = False
_vectorstore_lock = threading.Lock()


def preload_vectorstore():
    """Preload vectorstore in background thread."""
    global _vectorstore_cache, _vectorstore_loading
    with _vectorstore_lock:
        if _vectorstore_cache is None and not _vectorstore_loading:
            _vectorstore_loading = True
    
    if _vectorstore_loading and _vectorstore_cache is None:
        try:
            logger.info("Background loading vectorstore...")
            _vectorstore_cache = load_vectorstore()
            logger.info("Vectorstore preloaded successfully")
        except Exception as e:
            logger.error(f"Background vectorstore load failed: {e}")
        finally:
            _vectorstore_loading = False


def get_vectorstore() -> Tuple[Any, Any]:
    """Load and cache vectorstore with thread-safe initialization."""
    global _vectorstore_cache
    if _vectorstore_cache is None:
        logger.info("Loading vectorstore...")
        try:
            _vectorstore_cache = load_vectorstore()
            logger.info("Vectorstore loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load vectorstore: {e}")
            raise
    return _vectorstore_cache


# ============================================================================
# Input Validation & Security
# ============================================================================

def sanitize_string(text: str, max_length: int = 2000) -> str:
    """Sanitize user input string."""
    if not isinstance(text, str):
        return ""
    # Remove null bytes and control characters (except newlines/tabs)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    # Limit length
    return text[:max_length].strip()


def validate_numeric(value: Any, field_name: str, min_val: float = 0, max_val: float = 1e15) -> float:
    """Validate and convert numeric input."""
    if value is None:
        raise ValueError(f"'{field_name}' is required")
    try:
        num = float(value)
        if num < min_val or num > max_val:
            raise ValueError(f"'{field_name}' must be between {min_val:,.0f} and {max_val:,.0f}")
        return num
    except (TypeError, ValueError):
        raise ValueError(f"'{field_name}' must be a valid number")


def validate_positive_int(value: Any, field_name: str, min_val: int = 1, max_val: int = 20) -> int:
    """Validate positive integer input."""
    try:
        num = int(value)
        if num < min_val or num > max_val:
            raise ValueError(f"'{field_name}' must be between {min_val} and {max_val}")
        return num
    except (TypeError, ValueError):
        raise ValueError(f"'{field_name}' must be a valid integer")


# ============================================================================
# Error Handlers
# ============================================================================

class APIError(Exception):
    """Custom API exception with status code."""
    def __init__(self, message: str, status_code: int = 400, details: Optional[str] = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


@app.errorhandler(APIError)
def handle_api_error(error: APIError):
    """Handle custom API errors."""
    response = {"error": error.message}
    if error.details and app.debug:
        response["details"] = error.details
    return jsonify(response), error.status_code


@app.errorhandler(429)
def handle_rate_limit(e):
    """Handle rate limit exceeded."""
    return jsonify({
        "error": "Rate limit exceeded",
        "message": "Too many requests. Please try again later."
    }), 429


@app.errorhandler(413)
def handle_large_request(e):
    """Handle request too large."""
    return jsonify({
        "error": "Request too large",
        "message": "The request payload exceeds the maximum allowed size."
    }), 413


@app.errorhandler(404)
def handle_not_found(e):
    """Handle page not found errors."""
    return jsonify({
        "error": "Endpoint not found",
        "message": "The requested endpoint does not exist. Check the API documentation at the root endpoint.",
        "available_endpoints": ["/health", "/calculate", "/retrieve", "/qa", "/aqa"]
    }), 404


@app.errorhandler(500)
def handle_internal_error(e):
    """Handle internal server errors."""
    logger.exception("Internal server error")
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred. Please try again later."
    }), 500


@app.errorhandler(Exception)
def handle_unexpected_error(e):
    """Catch-all handler for any unhandled exceptions."""
    logger.exception(f"Unhandled exception: {e}")
    return jsonify({
        "error": "An unexpected error occurred",
        "message": str(e) if app.debug else "Please try again later."
    }), 500


# ============================================================================
# Request Logging Middleware
# ============================================================================

@app.before_request
def before_request():
    """Log request and set start time."""
    g.start_time = time.time()


@app.after_request
def after_request(response):
    """Log response time."""
    if hasattr(g, 'start_time'):
        elapsed = (time.time() - g.start_time) * 1000
        logger.info(f"{request.method} {request.path} - {response.status_code} - {elapsed:.2f}ms")
    return response


# ============================================================================
# API Routes
# ============================================================================

@app.route("/health", methods=["GET"])
@limiter.exempt
def health():
    """Health check endpoint for monitoring."""
    return jsonify({
        "status": "healthy",
        "service": "AI Tax Reform API",
        "version": "2.0.0",
        "timestamp": time.time()
    }), 200


@app.route("/calculate", methods=["POST"])
@limiter.limit("30 per minute")
def calculate_endpoint():
    """
    Calculate Nigerian personal income tax.
    
    Request JSON:
        - income (float, required): Gross annual income in NGN
        - allowances (float, optional): Non-taxable allowances
        - reliefs (float, optional): Tax reliefs
        - pension (float, optional): Pension contribution
        - include_cra (bool, optional): Include Consolidated Relief Allowance (default: true)
    
    Returns:
        JSON with tax calculation breakdown
    """
    try:
        data = request.get_json() or {}
        
        # Validate inputs
        income = validate_numeric(data.get("income"), "income")
        allowances = validate_numeric(data.get("allowances", 0), "allowances", min_val=0)
        reliefs = validate_numeric(data.get("reliefs", 0), "reliefs", min_val=0)
        pension = validate_numeric(data.get("pension", 0), "pension", min_val=0)
        include_cra = bool(data.get("include_cra", True))
        
        # Calculate tax using the improved calculator
        result = calculate_tax(
            annual_income=income,
            allowances=allowances,
            reliefs=reliefs,
            pension_contribution=pension,
            include_cra=include_cra
        )
        
        return jsonify(get_tax_summary(result)), 200
        
    except ValueError as e:
        raise APIError(str(e), 400)
    except TaxCalculationError as e:
        raise APIError(str(e), 400)
    except Exception as e:
        logger.exception("Tax calculation failed")
        raise APIError("Tax calculation failed", 500)


@app.route("/retrieve", methods=["POST"])
@limiter.limit("20 per minute")
def retrieve():
    """
    Retrieve relevant document chunks from the tax law knowledge base.
    
    Request JSON:
        - query (string, required): Search query
        - top_k (int, optional): Number of results to return (1-20, default: 5)
    
    Returns:
        JSON with matching document chunks
    """
    try:
        payload = request.get_json() or {}
        
        query_text = sanitize_string(payload.get("query", ""))
        if not query_text or len(query_text) < 2:
            raise APIError("Query must be at least 2 characters", 400)
        
        top_k = validate_positive_int(payload.get("top_k", 5), "top_k", min_val=1, max_val=20)
        
        index, docs = get_vectorstore()
        results = query(index, docs, query_text, top_k=top_k)
        
        return jsonify({
            "query": query_text,
            "count": len(results),
            "results": results
        }), 200
        
    except APIError:
        raise
    except Exception as e:
        logger.exception("Retrieval failed")
        raise APIError("Document retrieval failed", 500)


@app.route("/qa", methods=["POST"])
@limiter.limit("15 per minute")
def qa():
    """
    Answer questions about Nigerian tax law using RAG (Retrieval-Augmented Generation).
    
    Request JSON:
        - query (string, required): Question to answer
        - top_k (int, optional): Number of context documents (1-8, default: 3)
        - prefer_grok (bool, optional): Prefer Groq/Grok model (default: true)
        - fast_mode (bool, optional): Return sources without LLM generation (default: false)
    
    Returns:
        JSON with AI-generated answer and source documents
    """
    try:
        payload = request.get_json() or {}
        
        query_text = sanitize_string(payload.get("query", ""))
        if not query_text or len(query_text) < 2:
            raise APIError("Query must be at least 2 characters", 400)
        
        # Default to 3 docs instead of 5 for faster response
        top_k = validate_positive_int(payload.get("top_k", 3), "top_k", min_val=1, max_val=8)
        prefer_grok = bool(payload.get("prefer_grok", True))
        fast_mode = bool(payload.get("fast_mode", False))
        
        # Retrieve relevant context with timeout handling
        try:
            index, docs = get_vectorstore()
            results = query(index, docs, query_text, top_k=top_k)
        except Exception as ve:
            logger.error(f"Vectorstore query failed: {ve}")
            raise APIError("Search service temporarily unavailable", 503)
        
        if not results:
            return jsonify({
                "answer": "I couldn't find relevant information about this topic in the tax documentation. Please try rephrasing your question.",
                "model": "none",
                "sources": []
            }), 200
        
        # Fast mode: return sources with excerpt instead of calling slow LLM
        if fast_mode:
            top_text = results[0].get("text", "")[:800]
            return jsonify({
                "query": query_text,
                "answer": f"**From the Nigeria Tax Act 2025:**\n\n{top_text}\n\n---\n*[Fast mode - showing direct excerpt from source documents]*",
                "model": "fast",
                "sources": results
            }), 200
        
        # Generate answer with shorter timeout
        try:
            answer, model_used, _ = generate_answer(query_text, results, prefer_grok=prefer_grok, timeout=20)
        except Exception as ge:
            logger.error(f"Answer generation failed: {ge}")
            # Return sources even if generation fails
            return jsonify({
                "answer": "I found relevant documents but couldn't generate a complete answer. Here are the key sections from the tax law that may help:",
                "model": "fallback",
                "sources": results
            }), 200
        
        return jsonify({
            "query": query_text,
            "answer": answer,
            "model": model_used,
            "sources": results
        }), 200
        
    except APIError:
        raise
    except Exception as e:
        logger.exception("QA processing failed")
        raise APIError("Question answering failed. Please try again.", 500)


@app.route("/aqa", methods=["POST"])
@limiter.limit("10 per minute")
def aqa():
    """
    Answer questions with verification (Assured QA).
    
    Same as /qa but includes answer verification step for higher accuracy.
    
    Request JSON:
        - query (string, required): Question to answer
        - top_k (int, optional): Number of context documents (1-10, default: 5)
        - prefer_grok (bool, optional): Prefer Groq/Grok model (default: true)
    
    Returns:
        JSON with AI-generated answer, verification result, and source documents
    """
    try:
        payload = request.get_json() or {}
        
        query_text = sanitize_string(payload.get("query", ""))
        if not query_text or len(query_text) < 2:
            raise APIError("Query must be at least 2 characters", 400)
        
        top_k = validate_positive_int(payload.get("top_k", 5), "top_k", min_val=1, max_val=10)
        prefer_grok = bool(payload.get("prefer_grok", True))
        
        # Retrieve relevant context
        index, docs = get_vectorstore()
        results = query(index, docs, query_text, top_k=top_k)
        
        if not results:
            return jsonify({
                "answer": "I couldn't find relevant information about this topic in the tax documentation.",
                "model": "none",
                "verification": {"score": 0, "reason": "No relevant documents found"},
                "verified": False,
                "sources": []
            }), 200
        
        # Generate answer
        answer, model_used, _ = generate_answer(query_text, results, prefer_grok=prefer_grok)
        
        # Verify answer
        try:
            verification = verify_answer(answer, query_text, results, prefer_grok=prefer_grok)
            
            # Parse verification result
            verified = False
            if isinstance(verification, dict):
                score = verification.get("score", 0)
                verified = score >= 0.7 if isinstance(score, (int, float)) else False
            elif isinstance(verification, str):
                # Try to extract score from string response
                import json
                try:
                    verification = json.loads(verification)
                    score = verification.get("score", 0)
                    verified = score >= 0.7 if isinstance(score, (int, float)) else False
                except json.JSONDecodeError:
                    verification = {"raw": verification, "score": 0}
                    verified = "accurate" in verification.get("raw", "").lower()
        except Exception as ve:
            logger.warning(f"Verification failed: {ve}")
            verification = {"error": "Verification unavailable"}
            verified = False
        
        return jsonify({
            "query": query_text,
            "answer": answer,
            "model": model_used,
            "verification": verification,
            "verified": verified,
            "sources": results
        }), 200
        
    except APIError:
        raise
    except Exception as e:
        logger.exception("AQA processing failed")
        raise APIError("Verified question answering failed. Please try again.", 500)


# ============================================================================
# API Documentation Endpoint
# ============================================================================

@app.route("/", methods=["GET"])
@limiter.exempt
def api_docs():
    """Return API documentation."""
    return jsonify({
        "name": "AI Tax Reform API",
        "version": "2.0.0",
        "description": "AI-powered Nigerian tax calculator and Q&A service",
        "endpoints": {
            "GET /health": "Health check",
            "POST /calculate": "Calculate personal income tax",
            "POST /retrieve": "Retrieve relevant tax documents",
            "POST /qa": "Ask questions about tax law",
            "POST /aqa": "Ask questions with answer verification"
        },
        "documentation": "https://github.com/your-repo/AI-TAX-REFORM#readme"
    }), 200


# ============================================================================
# Application Startup
# ============================================================================

def start_background_tasks():
    """Start background tasks after app is ready."""
    # Preload vectorstore in background after 2 seconds
    def delayed_preload():
        import time
        time.sleep(2)
        preload_vectorstore()
    
    thread = threading.Thread(target=delayed_preload, daemon=True)
    thread.start()


if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    debug = os.getenv("FLASK_ENV") == "development"
    
    logger.info(f"Starting AI Tax Reform API v2.0.0 on port {port}")
    logger.info(f"Allowed origins: {origins}")
    
    # Start background preloading
    start_background_tasks()
    
    app.run(host="0.0.0.0", port=port, debug=debug)
