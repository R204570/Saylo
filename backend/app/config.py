"""
Configuration management for the application.
Loads settings from environment variables.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Environment
    env: str = Field(default="development", alias="ENV")
    
    # Database
    database_url: str = Field(alias="DATABASE_URL")
    
    # Redis (optional)
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    
    # Ollama
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_llm_model: str = Field(default="llama3.1:8b-instruct-q4_K_M", alias="OLLAMA_LLM_MODEL")
    ollama_embedding_model: str = Field(default="nomic-embed-text", alias="OLLAMA_EMBEDDING_MODEL")
    ollama_vision_model: str = Field(default="llava:7b-q4", alias="OLLAMA_VISION_MODEL")
    
    # ChromaDB
    chromadb_path: str = Field(default="../data/chromadb", alias="CHROMADB_PATH")
    
    # File Storage
    upload_dir: str = Field(default="../data/uploads", alias="UPLOAD_DIR")
    recording_dir: str = Field(default="../data/recordings", alias="RECORDING_DIR")
    max_upload_size: int = Field(default=52428800, alias="MAX_UPLOAD_SIZE")  # 50MB
    
    # LiveKit
    livekit_url: str = Field(default="ws://localhost:7880", alias="LIVEKIT_URL")
    livekit_api_key: str = Field(default="devkey", alias="LIVEKIT_API_KEY")
    livekit_api_secret: str = Field(default="secret", alias="LIVEKIT_API_SECRET")
    
    # Speech Services
    whisper_model: str = Field(default="small", alias="WHISPER_MODEL")
    whisper_device: str = Field(default="cpu", alias="WHISPER_DEVICE")
    piper_voice: str = Field(default="en_US-lessac-medium", alias="PIPER_VOICE")
    
    # Performance Settings
    max_context_tokens: int = Field(default=2000, alias="MAX_CONTEXT_TOKENS")
    chunk_size: int = Field(default=500, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=100, alias="CHUNK_OVERLAP")
    max_retrieved_chunks: int = Field(default=3, alias="MAX_RETRIEVED_CHUNKS")
    
    # Vision Processing
    vision_frame_interval: int = Field(default=5, alias="VISION_FRAME_INTERVAL")
    vision_enabled: bool = Field(default=True, alias="VISION_ENABLED")
    
    # Session Settings
    default_session_duration: int = Field(default=3600, alias="DEFAULT_SESSION_DURATION")
    question_count: int = Field(default=8, alias="QUESTION_COUNT")
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
