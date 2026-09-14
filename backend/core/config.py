import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "EcoSnap AI"
    API_V1_STR: str = "/api/v1"
    
    # Generative AI API Key (e.g., OpenAI, Stability AI, or HuggingFace)
    GENAI_API_KEY: str = os.getenv("GENAI_API_KEY", "your-api-key-here")
    
    # CORS Origins for frontend communication
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:8000", "http://127.0.0.1:5500", "*"]

    class Config:
        case_sensitive = True

settings = Settings()