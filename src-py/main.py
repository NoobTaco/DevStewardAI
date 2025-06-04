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
from core.organizer import ProjectOrganizer, ConflictResolution
from core.utils import validate_project_path, load_config

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

# Initialize project analyzer and organizer
project_analyzer = ProjectAnalyzer(
    ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
)

# Initialize project organizer
config = load_config()
default_org_root = config.get("default_organization_root") or os.path.expanduser("~/OrganizedProjects")
project_organizer = ProjectOrganizer(
    root_directory=default_org_root
)

# In-memory storage for scan results and organization plans
# In production, this would use Redis or a database
scan_results_cache: Dict[str, Any] = {}
organization_plans_cache: Dict[str, Any] = {}

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

class OrganizePreviewRequest(BaseModel):
    """Request model for organization preview."""
    scan_id: str
    target_category: Optional[str] = None
    conflict_resolution: str = "rename"  # "skip", "rename", "overwrite"
    create_backup: bool = True
    custom_name: Optional[str] = None

class OrganizePreviewResponse(BaseModel):
    """Response model for organization preview."""
    plan_id: str
    scan_id: str
    source_path: str
    target_path: str
    operations: List[Dict[str, Any]]
    total_operations: int
    estimated_time_seconds: float
    total_files: int
    total_size_bytes: int
    conflicts_found: int
    safety_warnings: List[str]
    timestamp: datetime = Field(default_factory=datetime.now)

class OrganizeExecuteRequest(BaseModel):
    """Request model for organization execution."""
    plan_id: str
    confirm_execution: bool = False

class OrganizeExecuteResponse(BaseModel):
    """Response model for organization execution."""
    operation_id: str
    plan_id: str
    status: str  # "started", "completed", "failed"
    message: str
    progress_url: Optional[str] = None
    rollback_manifest: Optional[str] = None
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
        
        # Store analysis in cache for later organization
        scan_results_cache[response.scan_id] = analysis
        
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

@app.post("/organize/preview", response_model=OrganizePreviewResponse)
async def preview_organization(request: OrganizePreviewRequest):
    """
    Generate organization plan (dry-run preview).
    
    Creates a detailed plan showing exactly what will happen during organization:
    - Target directory structure
    - Files and directories to be moved
    - Potential naming conflicts
    - Estimated operation time
    - Safety warnings
    
    Args:
        request: OrganizePreviewRequest with scan ID and options
        
    Returns:
        OrganizePreviewResponse with complete organization plan
    """
    logger.info(f"Organization preview requested for scan: {request.scan_id}")
    
    try:
        # Get scan results from cache
        if request.scan_id not in scan_results_cache:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scan results not found for ID: {request.scan_id}"
            )
        
        analysis = scan_results_cache[request.scan_id]
        
        # Map string conflict resolution to enum
        conflict_resolution_map = {
            "skip": ConflictResolution.SKIP,
            "rename": ConflictResolution.RENAME,
            "overwrite": ConflictResolution.OVERWRITE
        }
        
        conflict_resolution = conflict_resolution_map.get(
            request.conflict_resolution, 
            ConflictResolution.RENAME
        )
        
        # Generate organization plan
        plan = project_organizer.generate_organization_plan(
            project_analysis=analysis,
            target_category=request.target_category,
            conflict_resolution=conflict_resolution,
            create_backup=request.create_backup
        )
        
        # Validate the plan
        is_valid, issues = project_organizer.validate_organization_plan(plan)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid organization plan: {'; '.join(issues)}"
            )
        
        # Store plan in cache for execution
        organization_plans_cache[plan.plan_id] = plan
        
        # Convert operations to dictionaries
        operations_dict = []
        for op in plan.operations:
            operations_dict.append({
                "operation_id": op.operation_id,
                "operation_type": op.operation_type.value,
                "source_path": op.source_path,
                "target_path": op.target_path,
                "estimated_time_seconds": op.estimated_time_seconds,
                "file_count": op.file_count,
                "total_size_bytes": op.total_size_bytes,
                "conflicts": op.conflicts,
                "resolution": op.resolution.value
            })
        
        # Get target path from main operation
        main_operation = next((op for op in plan.operations 
                              if op.operation_type.value == "move_directory"), 
                             plan.operations[0])
        
        response = OrganizePreviewResponse(
            plan_id=plan.plan_id,
            scan_id=request.scan_id,
            source_path=main_operation.source_path,
            target_path=main_operation.target_path,
            operations=operations_dict,
            total_operations=plan.total_operations,
            estimated_time_seconds=plan.estimated_total_time_seconds,
            total_files=plan.total_files,
            total_size_bytes=plan.total_size_bytes,
            conflicts_found=plan.conflicts_found,
            safety_warnings=plan.safety_warnings
        )
        
        logger.info(f"Organization plan generated: {plan.total_operations} operations, "
                   f"~{plan.estimated_total_time_seconds:.1f}s estimated")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate organization preview: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate organization plan: {str(e)}"
        )

@app.post("/organize/execute", response_model=OrganizeExecuteResponse)
async def execute_organization(request: OrganizeExecuteRequest):
    """
    Execute organization plan with real-time progress tracking.
    
    Performs the actual file organization based on a previously generated plan:
    - Moves files and directories to organized structure
    - Creates backups if requested
    - Provides rollback capability if operations fail
    - Tracks progress in real-time
    
    Args:
        request: OrganizeExecuteRequest with plan ID and confirmation
        
    Returns:
        OrganizeExecuteResponse with execution status and details
    """
    logger.info(f"Organization execution requested for plan: {request.plan_id}")
    
    try:
        # Require explicit confirmation for safety
        if not request.confirm_execution:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Execution requires explicit confirmation (confirm_execution: true)"
            )
        
        # Get organization plan from cache
        if request.plan_id not in organization_plans_cache:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organization plan not found for ID: {request.plan_id}"
            )
        
        plan = organization_plans_cache[request.plan_id]
        
        # Validate plan before execution
        is_valid, issues = project_organizer.validate_organization_plan(plan)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Plan validation failed: {'; '.join(issues)}"
            )
        
        # Start async execution (in a real app, this would be a background task)
        operation_id = f"exec_{int(datetime.now().timestamp())}"
        
        # For demonstration, we'll execute synchronously but yield progress
        # In production, this would be a background task with WebSocket/SSE progress
        progress_generator = project_organizer.execute_organization_plan(plan)
        
        final_progress = None
        async for progress in progress_generator:
            final_progress = progress
            # In production, you'd send this progress via WebSocket/SSE
            logger.info(f"Progress: {progress.files_processed}/{progress.total_files} files, "
                       f"Status: {progress.status}")
        
        if final_progress and final_progress.status == "completed":
            response = OrganizeExecuteResponse(
                operation_id=operation_id,
                plan_id=request.plan_id,
                status="completed",
                message=f"Organization completed successfully. "
                       f"Moved {final_progress.files_processed} files in "
                       f"{final_progress.elapsed_time_seconds:.2f} seconds.",
                rollback_manifest=f"operation_manifest_{operation_id}.json"
            )
            
            logger.info(f"Organization execution completed successfully")
            return response
        
        elif final_progress and final_progress.status == "failed":
            response = OrganizeExecuteResponse(
                operation_id=operation_id,
                plan_id=request.plan_id,
                status="failed",
                message=f"Organization failed: {final_progress.error_message}",
                rollback_manifest=f"operation_manifest_{operation_id}.json"
            )
            
            logger.error(f"Organization execution failed: {final_progress.error_message}")
            return response
        
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Execution completed with unknown status"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Organization execution failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute organization: {str(e)}"
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