"""
QA Service Module - AI-powered Question Answering for Nigerian Tax Law

This module provides functions for generating and verifying answers to tax-related
questions using Groq and Gemini APIs with retrieval-augmented generation (RAG).
"""

import os
import json
import logging
import requests
from typing import Tuple, Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# API Configuration
GROQ_API_URL = os.getenv("GROQ_API_URL") or "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API") or os.getenv("GROQ_API_TOKEN") or os.getenv("GROQ_KEY")
GROK_API_URL = os.getenv("GROK_API_URL")  # Backwards compatibility
GROK_API_KEY = os.getenv("GROK_API_KEY")  # Backwards compatibility
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# System prompts
TAX_ASSISTANT_PROMPT = """You are an expert Nigerian tax consultant assistant with deep knowledge of the Nigeria Tax Act 2025 and related tax legislation.

Your role is to:
1. Provide accurate, helpful answers about Nigerian tax law
2. Cite specific sources and sections when available
3. Be clear about limitations and when to consult a professional
4. Use Nigerian Naira (₦) for currency references
5. Format responses for readability using markdown

Guidelines:
- Base your answers ONLY on the provided context
- If the context doesn't contain enough information, say so clearly
- Never make up tax rates, thresholds, or legal requirements
- Recommend consulting FIRS or a tax professional for complex cases
"""

VERIFICATION_PROMPT = """You are a tax law fact-checker. Your task is to verify if an answer about Nigerian tax law is accurate and well-supported by the provided context.

Evaluate the answer based on:
1. Factual accuracy compared to the source documents
2. Completeness of the response
3. Proper citation of sources
4. Absence of hallucinated information

Return a JSON object with:
- score: float between 0 and 1 (1 = fully accurate)
- accurate: boolean (true if score >= 0.7)
- confidence_reason: string explaining your assessment
- issues: array of strings listing any inaccuracies or concerns (empty if none)
"""


class APIError(Exception):
    """Custom exception for API errors."""
    pass


def call_groq(
    prompt: str,
    system_prompt: Optional[str] = None,
    timeout: int = 25,
    model: str = "llama-3.3-70b-versatile",
    max_tokens: int = 800,
    temperature: float = 0.3
) -> str:
    """
    Call Groq API (OpenAI-compatible) for text generation.
    
    Args:
        prompt: User message/prompt
        system_prompt: Optional system message for context
        timeout: Request timeout in seconds (default: 25)
        model: Model identifier
        max_tokens: Maximum tokens in response (default: 800)
        temperature: Sampling temperature (0-1)
    
    Returns:
        Generated text response
    
    Raises:
        APIError: If API call fails
    """
    url = GROQ_API_URL or GROK_API_URL
    key = GROQ_API_KEY or GROK_API_KEY
    
    if not key:
        raise APIError("Groq API key not configured. Set GROQ_API_KEY environment variable.")
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": 0.95,
    }
    
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
        
        if resp.status_code == 401:
            raise APIError("Groq API authentication failed. Check your API key.")
        elif resp.status_code == 429:
            raise APIError("Groq API rate limit exceeded. Please try again later.")
        elif resp.status_code != 200:
            raise APIError(f"Groq API error ({resp.status_code})")
        
        data = resp.json()
        
        if isinstance(data, dict) and "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"]
        
        raise APIError("Unexpected response format from Groq API")
        
    except requests.Timeout:
        raise APIError("Groq API request timed out")
    except requests.RequestException as e:
        raise APIError(f"Network error calling Groq API: {str(e)}")


# Alias for backwards compatibility
call_grok = call_groq


def call_gemini(
    prompt: str,
    model: str = "gemini-pro",
    timeout: int = 25,
    max_output_tokens: int = 800
) -> str:
    """
    Call Google Gemini API for text generation.
    
    Args:
        prompt: User prompt
        model: Gemini model identifier
        timeout: Request timeout in seconds (default: 25)
        max_output_tokens: Maximum tokens in response (default: 800)
    
    Returns:
        Generated text response
    
    Raises:
        APIError: If API call fails
    """
    if not GEMINI_API_KEY:
        raise APIError("Gemini API key not configured. Set GEMINI_API_KEY environment variable.")
    
    url = f"https://generativelanguage.googleapis.com/v1/models/{model}:generateContent?key={GEMINI_API_KEY}"
    
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": max_output_tokens,
            "temperature": 0.3,
        }
    }
    
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
        
        if resp.status_code == 401:
            raise APIError("Gemini API authentication failed. Check your API key.")
        elif resp.status_code == 429:
            raise APIError("Gemini API rate limit exceeded. Please try again later.")
        elif resp.status_code != 200:
            raise APIError(f"Gemini API error ({resp.status_code})")
        
        data = resp.json()
        
        # Extract text from Gemini response
        if isinstance(data, dict):
            candidates = data.get("candidates", [])
            if candidates:
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                if parts:
                    return parts[0].get("text", "")
        
        raise APIError("Unexpected response format from Gemini API")
        
    except requests.Timeout:
        raise APIError("Gemini API request timed out")
    except requests.RequestException as e:
        raise APIError(f"Network error calling Gemini API: {str(e)}")


def format_context(contexts: List[Dict[str, Any]]) -> str:
    """Format context documents for the prompt."""
    formatted = []
    for i, ctx in enumerate(contexts, 1):
        page = ctx.get('page', 'N/A')
        chunk_id = ctx.get('chunk_id', '')
        text = ctx.get('text', '').strip()
        formatted.append(f"[Source {i} | Page {page}]\n{text}")
    return "\n\n---\n\n".join(formatted)


def generate_answer(
    query: str,
    contexts: List[Dict[str, Any]],
    prefer_grok: bool = True,
    timeout: int = 25
) -> Tuple[str, str, str]:
    """
    Generate an answer using RAG with the provided contexts.
    
    Args:
        query: User's question
        contexts: List of context documents with 'text', 'page', etc.
        prefer_grok: Try Groq/Grok first if True
        timeout: Timeout for API calls in seconds
    
    Returns:
        Tuple of (answer_text, model_used, raw_response)
    
    Raises:
        APIError: If all API calls fail
    """
    if not contexts:
        return (
            "I couldn't find relevant information to answer your question. "
            "Please try rephrasing or ask about a different topic.",
            "none",
            ""
        )
    
    context_text = format_context(contexts)
    
    prompt = f"""Based on the following excerpts from the Nigeria Tax Act 2025, please answer the question.

CONTEXT:
{context_text}

QUESTION: {query}

Please provide a clear, accurate answer based ONLY on the information provided above. 
If the context doesn't contain enough information, clearly state that.
List the source numbers you used at the end of your response."""

    errors = []
    
    # Try Groq first if preferred
    if prefer_grok:
        try:
            response = call_groq(prompt, system_prompt=TAX_ASSISTANT_PROMPT, timeout=timeout)
            return response, "groq", response
        except APIError as e:
            errors.append(f"Groq: {str(e)}")
            logger.warning(f"Groq API failed: {e}")
    
    # Try Gemini as fallback
    try:
        full_prompt = f"{TAX_ASSISTANT_PROMPT}\n\n{prompt}"
        response = call_gemini(full_prompt, timeout=timeout - 5)
        return response, "gemini", response
    except APIError as e:
        errors.append(f"Gemini: {str(e)}")
        logger.warning(f"Gemini API failed: {e}")
    
    # If not preferring Grok, try it now
    if not prefer_grok:
        try:
            response = call_groq(prompt, system_prompt=TAX_ASSISTANT_PROMPT, timeout=timeout)
            return response, "groq", response
        except APIError as e:
            errors.append(f"Groq: {str(e)}")
            logger.warning(f"Groq API failed: {e}")
    
    # All APIs failed
    error_summary = "; ".join(errors)
    raise APIError(f"All AI services unavailable. {error_summary}")


def verify_answer(
    answer: str,
    query: str,
    contexts: List[Dict[str, Any]],
    prefer_grok: bool = True
) -> Dict[str, Any]:
    """
    Verify an answer against the source contexts.
    
    Args:
        answer: The generated answer to verify
        query: Original question
        contexts: Source documents used for generation
        prefer_grok: Try Groq/Grok first if True
    
    Returns:
        Dictionary with verification results including score, accuracy, and issues
    """
    context_text = format_context(contexts)
    
    prompt = f"""Verify the following answer about Nigerian tax law.

CONTEXT DOCUMENTS:
{context_text}

QUESTION: {query}

ANSWER TO VERIFY:
{answer}

Analyze the answer and return ONLY a valid JSON object (no markdown, no explanation) with these exact fields:
{{
    "score": <float 0-1>,
    "accurate": <boolean>,
    "confidence_reason": "<string>",
    "issues": ["<string>", ...]
}}"""

    try:
        # Try Groq first
        if prefer_grok:
            try:
                response = call_groq(prompt, system_prompt=VERIFICATION_PROMPT, temperature=0.1)
            except APIError:
                response = call_gemini(f"{VERIFICATION_PROMPT}\n\n{prompt}")
        else:
            try:
                response = call_gemini(f"{VERIFICATION_PROMPT}\n\n{prompt}")
            except APIError:
                response = call_groq(prompt, system_prompt=VERIFICATION_PROMPT, temperature=0.1)
        
        # Parse JSON from response
        response = response.strip()
        
        # Handle markdown code blocks
        if response.startswith("```"):
            lines = response.split("\n")
            response = "\n".join(lines[1:-1])
        
        result = json.loads(response)
        
        # Ensure required fields
        return {
            "score": float(result.get("score", 0)),
            "accurate": bool(result.get("accurate", False)),
            "confidence_reason": str(result.get("confidence_reason", "")),
            "issues": list(result.get("issues", []))
        }
        
    except json.JSONDecodeError:
        logger.warning("Failed to parse verification response as JSON")
        return {
            "score": 0.5,
            "accurate": False,
            "confidence_reason": "Verification response could not be parsed",
            "issues": ["Verification format error"]
        }
    except APIError as e:
        logger.error(f"Verification API error: {e}")
        return {
            "score": 0,
            "accurate": False,
            "confidence_reason": f"Verification unavailable: {str(e)}",
            "issues": ["Verification service unavailable"]
        }
