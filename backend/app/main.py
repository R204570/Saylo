"""
Main FastAPI application for the AI Interview Platform.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from loguru import logger
import sys
import os

from app.config import settings
from app.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.log_level
)


# Database setup
engine = create_engine(settings.database_url, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting AI Interview Platform...")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
    
    # Create upload directories
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.recording_dir, exist_ok=True)
    logger.info("Upload directories created/verified")
    
    # Check Ollama health
    from app.services.ollama_service import ollama_service
    is_healthy = await ollama_service.check_health()
    if is_healthy:
        logger.info("✓ Ollama service is healthy")
    else:
        logger.warning("✗ Ollama service is not responding")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Interview Platform...")


# Create FastAPI app
app = FastAPI(
    title="AI Interview Platform",
    description="Local AI-powered interview preparation platform",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency for database session
def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    from app.services.ollama_service import ollama_service
    
    ollama_healthy = await ollama_service.check_health()
    
    return {
        "status": "healthy" if ollama_healthy else "degraded",
        "services": {
            "ollama": "healthy" if ollama_healthy else "unhealthy",
            "database": "healthy",
            "api": "healthy"
        }
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Interview Platform API",
        "version": "0.1.0",
        "docs": "/docs"
    }


# Import and include routers
from app.api import session, upload, interview

app.include_router(session.router, prefix="/api/sessions", tags=["Sessions"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(interview.router, prefix="/api/interview", tags=["Interview"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    )
