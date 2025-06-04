"""
DevSteward AI - FastAPI Backend

Main application module with API endpoints for project organization,
AI integration, and project bootstrapping.
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv
from core.project_analyzer import ProjectAnalyzer
from core.utils import validate_project_path

# Load environment variables
load_dotenv()

# Configure logging
def setup_logging():
    """Configure structured logging to file and console."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_file = os.getenv("LOG_FILE", "devsteward_ai.log")
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level))
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler for development
    if os.getenv("DEBUG", "false").lower() == "true":
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger

# Initialize logging
logger = setup_logging()

# Initialize project analyzer
project_analyzer = ProjectAnalyzer(
    ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
)

# Pydantic models for API requests/responses
class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str
    python_backend: bool
    ollama_available: bool

class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: str
    timestamp: datetime = Field(default_factory=datetime.now)

class ScanRequest(BaseModel):
    """Request model for directory scanning."""
    path: str
    use_ai: bool = True
    ai_model: Optional[str] = "llama2"
    max_files: int = 10000

class ScanResponse(BaseModel):
    """Response model for directory scanning."""
    scan_id: str
    path: str
    total_files: int
    total_directories: int
    file_extensions: Dict[str, int]
    key_files: List[str]
    heuristic_classification: Dict[str, Any]
    ai_classification: Optional[Dict[str, Any]]
    final_classification: Dict[str, Any]
    scan_duration_ms: int
    timestamp: datetime = Field(default_factory=datetime.now)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown tasks."""
    # Startup
    logger.info("DevSteward AI backend starting up...")
    logger.info(f"Log level: {os.getenv('LOG_LEVEL', 'INFO')}")
    logger.info(f"Debug mode: {os.getenv('DEBUG', 'false')}")
    
    yield
    
    # Shutdown
    logger.info("DevSteward AI backend shutting down...")

# Create FastAPI application
app = FastAPI(
    title="DevSteward AI",
    description="AI-powered project organizer and bootstrapper",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for Tauri frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "tauri://localhost",
        "https://tauri.localhost",
        "http://localhost:3000",  # Vue.js dev server
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    error_response = ErrorResponse(
        error="Internal Server Error",
        detail="An unexpected error occurred. Check logs for details."
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(error_response)
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP exception handler for API errors."""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    
    error_response = ErrorResponse(
        error=f"HTTP {exc.status_code}",
        detail=exc.detail
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(error_response)
    )

# API Routes

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns the current status of the application and its dependencies.
    """
    logger.info("Health check requested")
    
    # Check Ollama availability
    ollama_available = False
    try:
        import requests
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        ollama_available = response.status_code == 200
    except Exception as e:
        logger.warning(f"Ollama health check failed: {e}")
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0",
        python_backend=True,
        ollama_available=ollama_available
    )

@app.get("/models")
async def get_ollama_models():
    """
    Get available Ollama models.
    
    Returns a list of models available in the local Ollama installation.
    """
    logger.info("Ollama models requested")
    
    try:
        import requests
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        response = requests.get(f"{ollama_url}/api/tags", timeout=10)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Ollama service is not available"
            )
        
        models_data = response.json()
        models = [model["name"] for model in models_data.get("models", [])]
        
        logger.info(f"Found {len(models)} Ollama models")
        return {"models": models}
        
    except requests.RequestException as e:
        logger.error(f"Failed to connect to Ollama: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not connect to Ollama service"
        )
    except HTTPException:
        # Re-raise HTTPExceptions to preserve status codes
        raise
    except Exception as e:
        logger.error(f"Error fetching Ollama models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch available models"
        )

@app.post("/scan", response_model=ScanResponse)
async def scan_directory(request: ScanRequest):
    """
    Scan directory and analyze project structure and type.
    
    This endpoint performs a comprehensive analysis of a project directory:
    - Recursively scans files and directories
    - Analyzes file types and extensions
    - Detects key project files (package.json, Cargo.toml, etc.)
    - Applies heuristic classification rules
    - Optionally uses Ollama AI for enhanced classification
    
    Args:
        request: ScanRequest with path and options
        
    Returns:
        ScanResponse with detailed analysis results
    """
    logger.info(f"Directory scan requested for: {request.path}")
    
    try:
        # Validate the project path
        is_valid, error_message = validate_project_path(request.path)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid project path: {error_message}"
            )
        
        # Perform complete project analysis
        analysis = await project_analyzer.analyze_project(
            project_path=request.path,
            use_ai=request.use_ai,
            ai_model=request.ai_model or "llama2"
        )
        
        # Convert classification results to dictionaries
        def classification_to_dict(classification):
            if classification:
                return {
                    "category": classification.category,
                    "confidence": classification.confidence,
                    "reasoning": classification.reasoning,
                    "method": classification.method,
                    "suggested_name": classification.suggested_name
                }
            return None
        
        # Prepare response
        response = ScanResponse(
            scan_id=analysis.scan_result.scan_id,
            path=analysis.scan_result.path,
            total_files=analysis.scan_result.total_files,
            total_directories=analysis.scan_result.total_directories,
            file_extensions=analysis.scan_result.file_extensions,
            key_files=analysis.scan_result.key_files,
            heuristic_classification=classification_to_dict(analysis.heuristic_classification),
            ai_classification=classification_to_dict(analysis.ai_classification),
            final_classification=classification_to_dict(analysis.final_classification),
            scan_duration_ms=analysis.scan_result.scan_duration_ms
        )
        
        logger.info(f"Scan complete: {analysis.final_classification.category} "
                   f"({analysis.final_classification.confidence:.2f} confidence)")
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Scan failed for {request.path}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to scan directory: {str(e)}"
        )

@app.post("/organize/preview")
async def preview_organization():
    """
    Generate organization plan (dry-run).
    
    Placeholder endpoint for Phase 1 implementation.
    """
    logger.info("Organization preview requested")
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Organization preview will be implemented in Phase 1"
    )

@app.post("/organize/execute")
async def execute_organization():
    """
    Execute organization plan.
    
    Placeholder endpoint for Phase 1 implementation.
    """
    logger.info("Organization execution requested")
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Organization execution will be implemented in Phase 1"
    )

@app.post("/projects/create")
async def create_project():
    """
    Create new project from template.
    
    Placeholder endpoint for Phase 1 implementation.
    """
    logger.info("Project creation requested")
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Project creation will be implemented in Phase 1"
    )

# Development server
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8008))
    host = os.getenv("HOST", "127.0.0.1")
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"Starting DevSteward AI backend on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )