"""
Project Organizer - Safe file organization with dry-run and rollback capabilities.

This module provides functionality to:
- Generate organization plans based on project classifications
- Execute safe file operations with atomic copy-then-delete
- Handle naming conflicts intelligently
- Provide comprehensive rollback capabilities
- Track operation progress in real-time
- Create detailed audit trails for all operations
"""

import os
import shutil
import logging
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, AsyncGenerator
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

from .utils import (
    safe_create_directory, safe_copy_file, safe_move_file,
    create_backup_path, estimate_operation_time, generate_unique_id,
    OperationLogger
)
from .project_analyzer import ProjectAnalysis, ProjectScanResult, ClassificationResult

# Configure logger for this module
logger = logging.getLogger(__name__)


class OperationType(Enum):
    """Types of file operations."""
    MOVE_DIRECTORY = "move_directory"
    COPY_DIRECTORY = "copy_directory"
    CREATE_DIRECTORY = "create_directory"
    RENAME_DIRECTORY = "rename_directory"


class ConflictResolution(Enum):
    """Strategies for handling naming conflicts."""
    SKIP = "skip"              # Skip if target exists
    RENAME = "rename"          # Add suffix like "_2", "_3"
    MERGE = "merge"           # Merge directories (future)
    OVERWRITE = "overwrite"   # Replace existing (dangerous)


@dataclass
class OperationStep:
    """Individual step in an organization plan."""
    operation_id: str
    operation_type: OperationType
    source_path: str
    target_path: str
    estimated_time_seconds: float
    file_count: int
    total_size_bytes: int
    conflicts: List[str] = None
    resolution: ConflictResolution = ConflictResolution.RENAME
    
    def __post_init__(self):
        if self.conflicts is None:
            self.conflicts = []


@dataclass
class OrganizationPlan:
    """Complete plan for organizing projects."""
    plan_id: str
    root_directory: str
    operations: List[OperationStep]
    total_operations: int
    estimated_total_time_seconds: float
    total_files: int
    total_size_bytes: int
    created_timestamp: datetime
    conflicts_found: int
    safety_warnings: List[str] = None
    
    def __post_init__(self):
        if self.safety_warnings is None:
            self.safety_warnings = []


@dataclass
class OperationProgress:
    """Real-time progress of an organization operation."""
    operation_id: str
    current_step: int
    total_steps: int
    current_operation: str
    files_processed: int
    total_files: int
    bytes_processed: int
    total_bytes: int
    elapsed_time_seconds: float
    estimated_remaining_seconds: float
    status: str  # "running", "completed", "failed", "cancelled"
    error_message: Optional[str] = None


@dataclass
class OrganizationResult:
    """Result of an organization operation."""
    operation_id: str
    plan_id: str
    success: bool
    operations_completed: int
    operations_failed: int
    total_files_moved: int
    total_bytes_moved: int
    execution_time_seconds: float
    rollback_manifest_path: Optional[str]
    error_summary: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class ProjectOrganizer:
    """Main class for organizing development projects safely."""
    
    # Default organization schema
    DEFAULT_SCHEMA = {
        "Personal": {
            "Web": {
                "Frontend": ["Web/Frontend"],
                "Backend": ["Web/Backend"],
                "FullStack": ["Web/FullStack"]
            },
            "Mobile": {
                "CrossPlatform": ["Mobile/CrossPlatform"],
                "iOS": ["Mobile/iOS"],
                "Android": ["Mobile/Android"]
            },
            "Games": {
                "Unity": ["Games/Unity"],
                "Godot": ["Games/Godot"],
                "Other": ["Games/Other"]
            },
            "SystemUtilities": {
                "Python": ["SystemUtilities/Python"],
                "Rust": ["SystemUtilities/Rust"],
                "Go": ["SystemUtilities/Go"],
                "Java": ["SystemUtilities/Java"],
                "Other": ["SystemUtilities/Other"]
            },
            "Libraries": {
                "Python": ["Libraries/Python"],
                "JavaScript": ["Libraries/JavaScript"],
                "Rust": ["Libraries/Rust"],
                "Other": ["Libraries/Other"]
            },
            "DataScience": ["DataScience"],
            "Misc": ["Misc"]
        },
        "Work": {},
        "Learning": {}
    }
    
    def __init__(self, root_directory: str, organization_schema: Optional[Dict] = None):
        """
        Initialize the project organizer.
        
        Args:
            root_directory: Root directory for organized projects
            organization_schema: Custom organization schema (uses default if None)
        """
        self.root_directory = Path(root_directory).resolve()
        self.schema = organization_schema or self.DEFAULT_SCHEMA
        
        # Ensure root directory exists
        safe_create_directory(str(self.root_directory))
        
        logger.info(f"ProjectOrganizer initialized with root: {self.root_directory}")
    
    def generate_organization_plan(
        self,
        project_analysis: ProjectAnalysis,
        target_category: Optional[str] = None,
        conflict_resolution: ConflictResolution = ConflictResolution.RENAME,
        create_backup: bool = True
    ) -> OrganizationPlan:
        """
        Generate a comprehensive organization plan for a project.
        
        Args:
            project_analysis: Complete project analysis from scanner
            target_category: Override category (uses final_classification if None)
            conflict_resolution: How to handle naming conflicts
            create_backup: Whether to create backup before operations
            
        Returns:
            OrganizationPlan with all operations to perform
        """
        logger.info(f"Generating organization plan for: {project_analysis.scan_result.path}")
        
        plan_id = generate_unique_id("plan")
        source_path = Path(project_analysis.scan_result.path)
        
        # Determine target category
        category = target_category or project_analysis.final_classification.category
        
        # Generate target path
        target_path = self._generate_target_path(
            source_path, 
            category, 
            project_analysis.final_classification.suggested_name
        )
        
        # Check for conflicts
        conflicts, resolved_target = self._resolve_naming_conflicts(
            target_path, conflict_resolution
        )
        
        # Calculate operation details
        total_size = sum(size for _, size in project_analysis.scan_result.largest_files)
        estimated_time = estimate_operation_time(
            project_analysis.scan_result.total_files, 
            total_size
        )
        
        # Create main operation
        operation = OperationStep(
            operation_id=generate_unique_id("op"),
            operation_type=OperationType.MOVE_DIRECTORY,
            source_path=str(source_path),
            target_path=str(resolved_target),
            estimated_time_seconds=estimated_time,
            file_count=project_analysis.scan_result.total_files,
            total_size_bytes=total_size,
            conflicts=conflicts,
            resolution=conflict_resolution
        )
        
        operations = []
        safety_warnings = []
        
        # Add backup operation if requested
        if create_backup:
            backup_path = create_backup_path(str(source_path))
            backup_operation = OperationStep(
                operation_id=generate_unique_id("backup"),
                operation_type=OperationType.COPY_DIRECTORY,
                source_path=str(source_path),
                target_path=backup_path,
                estimated_time_seconds=estimated_time * 0.5,  # Backup is usually faster
                file_count=project_analysis.scan_result.total_files,
                total_size_bytes=total_size
            )
            operations.append(backup_operation)
        
        # Add main move operation
        operations.append(operation)
        
        # Add safety warnings
        if conflicts:
            safety_warnings.append(f"Naming conflicts detected: {len(conflicts)} files/directories")
        
        if total_size > 1_000_000_000:  # 1GB
            safety_warnings.append("Large project detected (>1GB) - operation may take longer")
        
        if project_analysis.scan_result.total_files > 10_000:
            safety_warnings.append("Many files detected (>10k) - operation may take longer")
        
        # Create the plan
        plan = OrganizationPlan(
            plan_id=plan_id,
            root_directory=str(self.root_directory),
            operations=operations,
            total_operations=len(operations),
            estimated_total_time_seconds=sum(op.estimated_time_seconds for op in operations),
            total_files=project_analysis.scan_result.total_files,
            total_size_bytes=total_size,
            created_timestamp=datetime.now(),
            conflicts_found=len(conflicts),
            safety_warnings=safety_warnings
        )
        
        logger.info(f"Plan generated: {len(operations)} operations, "
                   f"~{plan.estimated_total_time_seconds:.1f}s estimated")
        
        return plan
    
    def _generate_target_path(
        self, 
        source_path: Path, 
        category: str, 
        suggested_name: Optional[str]
    ) -> Path:
        """Generate the target path based on category and schema."""
        
        # Use suggested name or source directory name
        project_name = suggested_name or source_path.name
        
        # Clean the project name
        project_name = self._clean_project_name(project_name)
        
        # Navigate the schema to find target directory
        target_parts = []
        
        # Split category (e.g., "Web/Frontend" -> ["Web", "Frontend"])
        category_parts = category.split("/")
        
        # Default to Personal section
        current_schema = self.schema.get("Personal", {})
        target_parts.append("Personal")
        
        # Navigate through category parts
        for part in category_parts:
            if isinstance(current_schema, dict) and part in current_schema:
                target_parts.append(part)
                current_schema = current_schema[part]
            else:
                # If category not found in schema, use it directly
                target_parts.append(part)
                break
        
        # Build target path
        target_path = self.root_directory
        for part in target_parts:
            target_path = target_path / part
        
        target_path = target_path / project_name
        
        return target_path
    
    def _clean_project_name(self, name: str) -> str:
        """Clean project name for filesystem compatibility."""
        import re
        
        # Remove or replace invalid characters
        cleaned = re.sub(r'[<>:"/\\|?*]', '_', name)
        
        # Remove leading/trailing dots and spaces
        cleaned = cleaned.strip('. ')
        
        # Collapse multiple underscores
        cleaned = re.sub(r'_+', '_', cleaned)
        
        # Ensure it's not empty
        if not cleaned:
            cleaned = "unnamed_project"
        
        return cleaned
    
    def _resolve_naming_conflicts(
        self, 
        target_path: Path, 
        resolution: ConflictResolution
    ) -> Tuple[List[str], Path]:
        """Resolve naming conflicts at target path."""
        
        conflicts = []
        resolved_path = target_path
        
        if target_path.exists():
            conflicts.append(f"Target already exists: {target_path}")
            
            if resolution == ConflictResolution.RENAME:
                # Find available name with suffix
                counter = 1
                base_name = target_path.name
                parent = target_path.parent
                
                while resolved_path.exists():
                    new_name = f"{base_name}_{counter}"
                    resolved_path = parent / new_name
                    counter += 1
                
                conflicts.append(f"Will rename to: {resolved_path.name}")
            
            elif resolution == ConflictResolution.SKIP:
                conflicts.append("Operation will be skipped due to existing target")
            
            elif resolution == ConflictResolution.OVERWRITE:
                conflicts.append("WARNING: Existing target will be overwritten")
        
        return conflicts, resolved_path
    
    async def execute_organization_plan(
        self,
        plan: OrganizationPlan,
        progress_callback: Optional[callable] = None
    ) -> AsyncGenerator[OperationProgress, None]:
        """
        Execute an organization plan with real-time progress updates.
        
        Args:
            plan: Organization plan to execute
            progress_callback: Optional callback for progress updates
            
        Yields:
            OperationProgress updates during execution
        """
        logger.info(f"Starting execution of plan: {plan.plan_id}")
        
        operation_id = generate_unique_id("exec")
        start_time = datetime.now()
        
        # Create operation logger for rollback capability
        op_logger = OperationLogger(operation_id)
        
        try:
            total_files_processed = 0
            total_bytes_processed = 0
            
            for step_index, operation in enumerate(plan.operations):
                logger.info(f"Executing step {step_index + 1}/{len(plan.operations)}: "
                           f"{operation.operation_type.value}")
                
                # Yield progress update
                progress = OperationProgress(
                    operation_id=operation_id,
                    current_step=step_index + 1,
                    total_steps=len(plan.operations),
                    current_operation=f"{operation.operation_type.value}: {operation.source_path}",
                    files_processed=total_files_processed,
                    total_files=plan.total_files,
                    bytes_processed=total_bytes_processed,
                    total_bytes=plan.total_size_bytes,
                    elapsed_time_seconds=(datetime.now() - start_time).total_seconds(),
                    estimated_remaining_seconds=max(0, plan.estimated_total_time_seconds - 
                                                   (datetime.now() - start_time).total_seconds()),
                    status="running"
                )
                
                yield progress
                
                if progress_callback:
                    progress_callback(progress)
                
                # Execute the operation
                success = await self._execute_operation_step(operation, op_logger)
                
                if success:
                    total_files_processed += operation.file_count
                    total_bytes_processed += operation.total_size_bytes
                else:
                    # Operation failed - yield error progress
                    error_progress = OperationProgress(
                        operation_id=operation_id,
                        current_step=step_index + 1,
                        total_steps=len(plan.operations),
                        current_operation=f"FAILED: {operation.operation_type.value}",
                        files_processed=total_files_processed,
                        total_files=plan.total_files,
                        bytes_processed=total_bytes_processed,
                        total_bytes=plan.total_size_bytes,
                        elapsed_time_seconds=(datetime.now() - start_time).total_seconds(),
                        estimated_remaining_seconds=0,
                        status="failed",
                        error_message=f"Failed to execute {operation.operation_type.value}"
                    )
                    yield error_progress
                    return
            
            # Final success progress
            final_progress = OperationProgress(
                operation_id=operation_id,
                current_step=len(plan.operations),
                total_steps=len(plan.operations),
                current_operation="Completed successfully",
                files_processed=total_files_processed,
                total_files=plan.total_files,
                bytes_processed=total_bytes_processed,
                total_bytes=plan.total_size_bytes,
                elapsed_time_seconds=(datetime.now() - start_time).total_seconds(),
                estimated_remaining_seconds=0,
                status="completed"
            )
            
            yield final_progress
            
            # Save operation manifest for rollback
            manifest_path = f"operation_manifest_{operation_id}.json"
            op_logger.save_manifest(manifest_path)
            
            logger.info(f"Organization plan executed successfully in "
                       f"{final_progress.elapsed_time_seconds:.2f}s")
        
        except Exception as e:
            logger.error(f"Organization plan execution failed: {e}", exc_info=True)
            
            error_progress = OperationProgress(
                operation_id=operation_id,
                current_step=0,
                total_steps=len(plan.operations),
                current_operation="Execution failed",
                files_processed=0,
                total_files=plan.total_files,
                bytes_processed=0,
                total_bytes=plan.total_size_bytes,
                elapsed_time_seconds=(datetime.now() - start_time).total_seconds(),
                estimated_remaining_seconds=0,
                status="failed",
                error_message=str(e)
            )
            
            yield error_progress
    
    async def _execute_operation_step(
        self, 
        operation: OperationStep, 
        op_logger: OperationLogger
    ) -> bool:
        """Execute a single operation step."""
        
        try:
            source_path = Path(operation.source_path)
            target_path = Path(operation.target_path)
            
            if operation.operation_type == OperationType.MOVE_DIRECTORY:
                # Ensure target parent directory exists
                safe_create_directory(str(target_path.parent))
                
                # Log the operation
                op_logger.log_operation("move", str(source_path), str(target_path))
                
                # Execute move (copy then delete)
                if source_path.is_dir():
                    # Use asyncio to make it non-blocking
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(
                        None, 
                        shutil.copytree, 
                        str(source_path), 
                        str(target_path),
                        False,  # dirs_exist_ok
                        None,   # ignore
                        True,   # copy_function
                        True,   # ignore_dangling_symlinks
                        False   # copy_stats_deep
                    )
                    
                    # Remove source after successful copy
                    await loop.run_in_executor(
                        None,
                        shutil.rmtree,
                        str(source_path)
                    )
                else:
                    return False
            
            elif operation.operation_type == OperationType.COPY_DIRECTORY:
                # Ensure target parent directory exists
                safe_create_directory(str(target_path.parent))
                
                # Log the operation
                op_logger.log_operation("copy", str(source_path), str(target_path))
                
                # Execute copy
                if source_path.is_dir():
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(
                        None,
                        shutil.copytree,
                        str(source_path),
                        str(target_path)
                    )
                else:
                    return False
            
            elif operation.operation_type == OperationType.CREATE_DIRECTORY:
                # Log the operation
                op_logger.log_operation("create_directory", "", str(target_path))
                
                # Create directory
                safe_create_directory(str(target_path))
            
            else:
                logger.warning(f"Unsupported operation type: {operation.operation_type}")
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"Operation step failed: {e}", exc_info=True)
            return False
    
    def create_rollback_plan(self, manifest_path: str) -> Optional[List[str]]:
        """Create a rollback plan from an operation manifest."""
        
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            op_logger = OperationLogger(manifest['operation_id'])
            op_logger.operations = manifest['operations']
            
            return op_logger.generate_rollback_script()
        
        except Exception as e:
            logger.error(f"Failed to create rollback plan: {e}")
            return None
    
    def validate_organization_plan(self, plan: OrganizationPlan) -> Tuple[bool, List[str]]:
        """Validate an organization plan before execution."""
        
        errors = []
        warnings = []
        
        # Check root directory exists and is writable
        if not self.root_directory.exists():
            errors.append(f"Root directory does not exist: {self.root_directory}")
        elif not os.access(self.root_directory, os.W_OK):
            errors.append(f"No write permission to root directory: {self.root_directory}")
        
        # Validate each operation
        for operation in plan.operations:
            source_path = Path(operation.source_path)
            target_path = Path(operation.target_path)
            
            # Check source exists
            if not source_path.exists():
                errors.append(f"Source path does not exist: {source_path}")
            
            # Check source is readable
            if source_path.exists() and not os.access(source_path, os.R_OK):
                errors.append(f"No read permission for source: {source_path}")
            
            # Check target parent is writable
            if target_path.parent.exists() and not os.access(target_path.parent, os.W_OK):
                errors.append(f"No write permission for target parent: {target_path.parent}")
            
            # Check for potential issues
            if operation.file_count > 50_000:
                warnings.append(f"Large operation: {operation.file_count} files")
            
            if operation.total_size_bytes > 10_000_000_000:  # 10GB
                warnings.append(f"Large operation: {operation.total_size_bytes} bytes")
        
        # Add warnings to plan if not already present
        plan.safety_warnings.extend(warnings)
        
        is_valid = len(errors) == 0
        all_issues = errors + warnings
        
        return is_valid, all_issues