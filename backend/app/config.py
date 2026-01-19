"""
Environment Configuration for NTRIA
"""

import os
from functools import lru_cache

class Settings:
    def __init__(self):
        # AI Keys - check for both GOOGLE_API_KEY and GEMINI_API_KEY
        self.google_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or ""
        
        # Strip whitespace or quotes that might be added by environment managers
        self.google_api_key = self.google_api_key.strip().strip("'").strip('"')
        
        # Demo mode if API keys are missing or invalid
        self.demo_mode = (
            not self.google_api_key or 
            self.google_api_key == "demo_key_placeholder" or
            len(self.google_api_key) < 10
        )
        
        if not self.demo_mode:
            print(f"✅ AI API Key detected (length: {len(self.google_api_key)}) - Enabling RAG Mode")
        else:
            print(f"⚠️  No valid API Key found - Running in DEMO MODE")
        
        # Database
        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
        
        # API
        self.api_host = os.getenv("API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("PORT", "8000"))
        
        # CORS
        self.allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

@lru_cache()
def get_settings():
    return Settings()