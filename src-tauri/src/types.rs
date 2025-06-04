use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Response from health check endpoint
#[derive(Debug, Serialize, Deserialize)]
pub struct HealthResponse {
    pub status: String,
    pub timestamp: String,
    pub version: String,
    pub python_backend: bool,
    pub ollama_available: bool,
}

/// Request for directory scanning
#[derive(Debug, Serialize, Deserialize)]
pub struct ScanRequest {
    pub path: String,
    pub use_ai: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub ai_model: Option<String>,
    #[serde(default = "default_max_files")]
    pub max_files: u32,
}

fn default_max_files() -> u32 {
    10000
}

/// Response from directory scanning
#[derive(Debug, Serialize, Deserialize)]
pub struct ScanResponse {
    pub scan_id: String,
    pub path: String,
    pub total_files: u32,
    pub total_directories: u32,
    pub file_extensions: HashMap<String, u32>,
    pub key_files: Vec<String>,
    pub heuristic_classification: ClassificationResult,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub ai_classification: Option<ClassificationResult>,
    pub final_classification: ClassificationResult,
    pub scan_duration_ms: u32,
    pub timestamp: String,
}

/// Classification result from heuristic or AI analysis
#[derive(Debug, Serialize, Deserialize)]
pub struct ClassificationResult {
    pub category: String,
    pub confidence: f64,
    pub reasoning: String,
    pub method: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub suggested_name: Option<String>,
}

/// Request for organization preview
#[derive(Debug, Serialize, Deserialize)]
pub struct OrganizePreviewRequest {
    pub scan_id: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub target_category: Option<String>,
    #[serde(default = "default_conflict_resolution")]
    pub conflict_resolution: String,
    #[serde(default = "default_create_backup")]
    pub create_backup: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub custom_name: Option<String>,
}

fn default_conflict_resolution() -> String {
    "rename".to_string()
}

fn default_create_backup() -> bool {
    true
}

/// Response from organization preview
#[derive(Debug, Serialize, Deserialize)]
pub struct OrganizePreviewResponse {
    pub plan_id: String,
    pub scan_id: String,
    pub source_path: String,
    pub target_path: String,
    pub operations: Vec<OperationStep>,
    pub total_operations: u32,
    pub estimated_time_seconds: f64,
    pub total_files: u32,
    pub total_size_bytes: u64,
    pub conflicts_found: u32,
    pub safety_warnings: Vec<String>,
    pub timestamp: String,
}

/// Individual operation step
#[derive(Debug, Serialize, Deserialize)]
pub struct OperationStep {
    pub operation_id: String,
    pub operation_type: String,
    pub source_path: String,
    pub target_path: String,
    pub estimated_time_seconds: f64,
    pub file_count: u32,
    pub total_size_bytes: u64,
    pub conflicts: Vec<String>,
    pub resolution: String,
}

/// Request for organization execution
#[derive(Debug, Serialize, Deserialize)]
pub struct OrganizeExecuteRequest {
    pub plan_id: String,
    pub confirm_execution: bool,
}

/// Response from organization execution
#[derive(Debug, Serialize, Deserialize)]
pub struct OrganizeExecuteResponse {
    pub operation_id: String,
    pub plan_id: String,
    pub status: String,
    pub message: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub progress_url: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub rollback_manifest: Option<String>,
    pub timestamp: String,
}

/// Progress tracking for organization operations
#[derive(Debug, Serialize, Deserialize)]
pub struct OperationProgress {
    pub operation_id: String,
    pub current_step: u32,
    pub total_steps: u32,
    pub current_operation: String,
    pub files_processed: u32,
    pub total_files: u32,
    pub bytes_processed: u64,
    pub total_bytes: u64,
    pub elapsed_time_seconds: f64,
    pub estimated_remaining_seconds: f64,
    pub status: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error_message: Option<String>,
}

/// Application settings
#[derive(Debug, Serialize, Deserialize)]
pub struct AppSettings {
    pub organization_root: String,
    pub default_ai_model: String,
    pub create_backup_by_default: bool,
    pub use_ai_by_default: bool,
    pub conflict_resolution_strategy: String,
    pub ollama_base_url: String,
    pub python_backend_port: u16,
    pub auto_start_backend: bool,
}

impl Default for AppSettings {
    fn default() -> Self {
        Self {
            organization_root: "~/OrganizedProjects".to_string(),
            default_ai_model: "llama2".to_string(),
            create_backup_by_default: true,
            use_ai_by_default: true,
            conflict_resolution_strategy: "rename".to_string(),
            ollama_base_url: "http://localhost:11434".to_string(),
            python_backend_port: 8008,
            auto_start_backend: true,
        }
    }
}

/// Process status
#[derive(Debug, Serialize, Deserialize)]
pub struct ProcessStatus {
    pub is_running: bool,
    pub pid: Option<u32>,
    pub port: u16,
    pub uptime_seconds: Option<u64>,
    pub health_status: Option<String>,
}

/// Ollama models response
#[derive(Debug, Serialize, Deserialize)]
pub struct ModelsResponse {
    pub models: Vec<String>,
}

/// Error response from API
#[derive(Debug, Serialize, Deserialize)]
pub struct ErrorResponse {
    pub error: String,
    pub detail: String,
    pub timestamp: String,
}

/// Template information for project creation
#[derive(Debug, Serialize, Deserialize)]
pub struct ProjectTemplate {
    pub id: String,
    pub name: String,
    pub description: String,
    pub category: String,
    pub language: String,
    pub features: Vec<String>,
}

/// Project creation request
#[derive(Debug, Serialize, Deserialize)]
pub struct CreateProjectRequest {
    pub template_id: String,
    pub project_name: String,
    pub target_directory: String,
    pub initialize_git: bool,
    pub options: HashMap<String, String>,
}