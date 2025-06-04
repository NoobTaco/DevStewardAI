"""
Utility functions for DevSteward AI.

Common utilities for file operations, configuration management,
and helper functions used across the application.
"""

import os
import logging
import json
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime


def check_ollama_availability(base_url: str = "http://localhost:11434", timeout: int = 5) -> bool:
    """
    Check if Ollama service is available.
    
    Args:
        base_url: Ollama server URL
        timeout: Request timeout in seconds
        
    Returns:
        True if Ollama is available, False otherwise
    """
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=timeout)
        return response.status_code == 200
    except Exception:
        return False


def get_ollama_models(base_url: str = "http://localhost:11434", timeout: int = 10) -> List[str]:
    """
    Get list of available Ollama models.
    
    Args:
        base_url: Ollama server URL
        timeout: Request timeout in seconds
        
    Returns:
        List of model names, empty list if unavailable
    """
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
    except Exception as e:
        logging.warning(f"Failed to get Ollama models: {e}")
    
    return []


def safe_create_directory(path: str) -> bool:
    """
    Safely create a directory if it doesn't exist.
    
    Args:
        path: Directory path to create
        
    Returns:
        True if directory was created or already exists, False on error
    """
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Failed to create directory {path}: {e}")
        return False


def safe_read_file(file_path: str, encoding: str = 'utf-8', max_size: int = 10_000_000) -> Optional[str]:
    """
    Safely read a text file with size limits.
    
    Args:
        file_path: Path to file
        encoding: Text encoding to use
        max_size: Maximum file size in bytes
        
    Returns:
        File content as string, or None if failed
    """
    try:
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            return None
        
        # Check file size
        if path.stat().st_size > max_size:
            logging.warning(f"File {file_path} is too large ({path.stat().st_size} bytes)")
            return None
        
        with open(path, 'r', encoding=encoding, errors='ignore') as f:
            return f.read()
    
    except Exception as e:
        logging.debug(f"Could not read file {file_path}: {e}")
        return None


def safe_write_file(file_path: str, content: str, encoding: str = 'utf-8') -> bool:
    """
    Safely write content to a file.
    
    Args:
        file_path: Path to file
        content: Content to write
        encoding: Text encoding to use
        
    Returns:
        True if successful, False otherwise
    """
    try:
        path = Path(file_path)
        # Create parent directories if needed
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    
    except Exception as e:
        logging.error(f"Failed to write file {file_path}: {e}")
        return False


def safe_copy_file(src: str, dst: str) -> bool:
    """
    Safely copy a file with error handling.
    
    Args:
        src: Source file path
        dst: Destination file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        import shutil
        src_path = Path(src)
        dst_path = Path(dst)
        
        if not src_path.exists():
            logging.error(f"Source file does not exist: {src}")
            return False
        
        # Create destination directory if needed
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(src_path, dst_path)
        return True
    
    except Exception as e:
        logging.error(f"Failed to copy {src} to {dst}: {e}")
        return False


def safe_move_file(src: str, dst: str) -> bool:
    """
    Safely move a file (copy then delete).
    
    Args:
        src: Source file path
        dst: Destination file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # First copy the file
        if safe_copy_file(src, dst):
            # Then delete the source
            Path(src).unlink()
            return True
        return False
    
    except Exception as e:
        logging.error(f"Failed to move {src} to {dst}: {e}")
        return False


def get_file_size_human(size_bytes: int) -> str:
    """
    Convert file size in bytes to human readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human readable size string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"


def clean_filename(filename: str) -> str:
    """
    Clean a filename to remove invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Cleaned filename safe for filesystem
    """
    import re
    
    # Replace invalid characters with underscores
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing dots and spaces
    cleaned = cleaned.strip('. ')
    
    # Ensure it's not empty
    if not cleaned:
        cleaned = "unnamed_file"
    
    return cleaned


def validate_project_path(path: str) -> tuple[bool, str]:
    """
    Validate a project path for scanning.
    
    Args:
        path: Path to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        project_path = Path(path).resolve()
        
        if not project_path.exists():
            return False, "Path does not exist"
        
        if not project_path.is_dir():
            return False, "Path is not a directory"
        
        # Check if we have read permissions
        if not os.access(project_path, os.R_OK):
            return False, "No read permission for directory"
        
        # Check if directory is not empty
        try:
            next(project_path.iterdir())
        except StopIteration:
            return False, "Directory is empty"
        
        return True, ""
    
    except Exception as e:
        return False, f"Invalid path: {e}"


def load_config(config_path: str = ".env") -> Dict[str, Any]:
    """
    Load configuration from environment file.
    
    Args:
        config_path: Path to config file
        
    Returns:
        Dictionary of configuration values
    """
    config = {}
    
    try:
        from dotenv import load_dotenv
        load_dotenv(config_path)
        
        # Default configuration
        config = {
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "log_file": os.getenv("LOG_FILE", "devsteward_ai.log"),
            "debug": os.getenv("DEBUG", "false").lower() == "true",
            "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            "ollama_default_model": os.getenv("OLLAMA_DEFAULT_MODEL", "llama2"),
            "ollama_timeout": int(os.getenv("OLLAMA_TIMEOUT", "30")),
            "ai_confidence_threshold": float(os.getenv("AI_CONFIDENCE_THRESHOLD", "0.7")),
            "create_backup": os.getenv("CREATE_BACKUP", "true").lower() == "true",
            "init_git_by_default": os.getenv("INIT_GIT_BY_DEFAULT", "true").lower() == "true"
        }
        
    except Exception as e:
        logging.warning(f"Failed to load config from {config_path}: {e}")
    
    return config


def setup_logging(log_level: str = "INFO", log_file: str = "devsteward_ai.log") -> logging.Logger:
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Log file path
        
    Returns:
        Configured logger instance
    """
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    try:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not create log file {log_file}: {e}")
    
    # Console handler for debug mode
    if log_level.upper() == "DEBUG":
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


def generate_unique_id(prefix: str = "") -> str:
    """
    Generate a unique ID for operations.
    
    Args:
        prefix: Optional prefix for the ID
        
    Returns:
        Unique identifier string
    """
    import uuid
    timestamp = int(datetime.now().timestamp())
    unique_part = str(uuid.uuid4())[:8]
    
    if prefix:
        return f"{prefix}_{timestamp}_{unique_part}"
    else:
        return f"{timestamp}_{unique_part}"


def create_backup_path(original_path: str) -> str:
    """
    Generate a backup path for a file or directory.
    
    Args:
        original_path: Original file/directory path
        
    Returns:
        Backup path with timestamp
    """
    path = Path(original_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if path.is_file():
        # For files: filename_backup_20231201_143022.ext
        stem = path.stem
        suffix = path.suffix
        backup_name = f"{stem}_backup_{timestamp}{suffix}"
    else:
        # For directories: dirname_backup_20231201_143022
        backup_name = f"{path.name}_backup_{timestamp}"
    
    return str(path.parent / backup_name)


def estimate_operation_time(file_count: int, total_size_bytes: int) -> float:
    """
    Estimate time for file operations based on file count and size.
    
    Args:
        file_count: Number of files
        total_size_bytes: Total size in bytes
        
    Returns:
        Estimated time in seconds
    """
    # Base time per file (small overhead)
    base_time = file_count * 0.01  # 10ms per file
    
    # Time based on file size (assuming 100MB/s transfer rate)
    size_time = total_size_bytes / (100 * 1024 * 1024)
    
    # Add 20% buffer
    total_time = (base_time + size_time) * 1.2
    
    return max(total_time, 0.1)  # Minimum 0.1 seconds


class OperationLogger:
    """Logger for tracking file operations with rollback capability."""
    
    def __init__(self, operation_id: str):
        self.operation_id = operation_id
        self.operations = []
        self.start_time = datetime.now()
        
    def log_operation(self, operation_type: str, source: str, destination: str = ""):
        """Log a file operation."""
        self.operations.append({
            "type": operation_type,
            "source": source,
            "destination": destination,
            "timestamp": datetime.now().isoformat()
        })
        
    def save_manifest(self, manifest_path: str) -> bool:
        """Save operation manifest to file."""
        try:
            manifest_data = {
                "operation_id": self.operation_id,
                "start_time": self.start_time.isoformat(),
                "operations": self.operations
            }
            
            with open(manifest_path, 'w') as f:
                json.dump(manifest_data, f, indent=2)
            
            return True
        except Exception as e:
            logging.error(f"Failed to save operation manifest: {e}")
            return False
    
    def generate_rollback_script(self) -> List[str]:
        """Generate rollback commands for the operations."""
        rollback_commands = []
        
        # Reverse the operations
        for op in reversed(self.operations):
            if op["type"] == "move":
                # Reverse move: move destination back to source
                rollback_commands.append(f"mv '{op['destination']}' '{op['source']}'")
            elif op["type"] == "copy":
                # Reverse copy: delete the copy
                rollback_commands.append(f"rm -rf '{op['destination']}'")
            elif op["type"] == "create_directory":
                # Reverse create: remove directory if empty
                rollback_commands.append(f"rmdir '{op['destination']}' 2>/dev/null || true")
        
        return rollback_commands