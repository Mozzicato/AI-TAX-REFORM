"""
Environment Configuration for NTRIA
"""

import os
from functools import lru_cache

class Settings:
    def __init__(self):
        # API Keys
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "")
        
        # Demo mode if API keys are missing
        self.demo_mode = (
            not self.google_api_key or 
            self.google_api_key == "demo_key_placeholder"
        )
        
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