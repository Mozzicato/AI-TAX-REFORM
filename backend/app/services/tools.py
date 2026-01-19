"""
Advanced Tools for NTRIA - Calculation and Search
"""

import re
import os
import requests
from typing import Dict, Any, Optional

class TaxCalculator:
    """Accurate math for tax calculations using Pythonic evaluation"""
    
    def calculate(self, expression: str) -> str:
        """
        Safely evaluate a mathematical expression.
        Avoids LLM math hallucinations.
        """
        try:
            # Remove any non-math characters except numbers, operators, and parentheses
            sanitized = re.sub(r'[^0-9+\-*/().\s]', '', expression)
            # Evaluate safely (only basic math)
            result = eval(sanitized, {"__builtins__": None}, {})
            return f"{result:,.2f}"
        except Exception as e:
            return f"Error in calculation: {str(e)}"

class UniversalSearch:
    """Fallback search when local RAG doesn't have the answer"""
    
    def __init__(self):
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        self.serper_key = os.getenv("SERPER_API_KEY")
        self.google_cse_key = os.getenv("GOOGLE_SEARCH_KEY")
        self.google_cse_id = os.getenv("GOOGLE_SEARCH_ID")

    def search(self, query: str) -> Optional[str]:
        """Perform a web search as a fallback"""
        if self.serper_key:
            return self._search_serper(query)
        elif self.tavily_key:
            return self._search_tavily(query)
        elif self.google_cse_key and self.google_cse_id:
            return self._search_google(query)
        else:
            return None

    def _search_serper(self, query: str) -> Optional[str]:
        """Search via Serper (Google Search API)"""
        try:
            url = "https://google.serper.dev/search"
            headers = {
                'X-API-KEY': self.serper_key,
                'Content-Type': 'application/json'
            }
            payload = {"q": query}
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            data = response.json()
            
            # Combine snippets from multiple organic results
            snippets = [item.get('snippet', '') for item in data.get('organic', [])[:3]]
            return "\n".join(snippets) if snippets else None
        except:
            return None

    def _search_tavily(self, query: str) -> Optional[str]:
        try:
            url = "https://api.tavily.com/search"
            payload = {
                "api_key": self.tavily_key,
                "query": query,
                "search_depth": "advanced",
                "include_answer": True
            }
            response = requests.post(url, json=payload, timeout=10)
            data = response.json()
            return data.get("answer") or data.get("results", [{}])[0].get("content")
        except:
            return None

    def _search_google(self, query: str) -> Optional[str]:
        try:
            url = f"https://www.googleapis.com/customsearch/v1?key={self.google_cse_key}&cx={self.google_cse_id}&q={query}"
            response = requests.get(url, timeout=10)
            data = response.json()
            return data.get("items", [{}])[0].get("snippet")
        except:
            return None
