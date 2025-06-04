use log::{info, warn, error};
use serde_json::Value;
use std::path::PathBuf;
use tauri::{State, Manager};

use crate::types::*;
use crate::AppState;

// ===== System Commands =====

#[tauri::command]
pub async fn check_health(state: State<'_, AppState>) -> Result<HealthResponse, String> {
    info!("Health check requested from frontend");
    
    let bridge = state.python_bridge.lock().await;
    match bridge.check_health().await {
        Ok(health) => {
            info!("Health check successful");
            Ok(health)
        }
        Err(e) => {
            warn!("Health check failed: {}", e);
            Err(format!("Health check failed: {}", e))
        }
    }
}

#[tauri::command]
pub async fn start_python_backend(state: State<'_, AppState>) -> Result<String, String> {
    info!("Starting Python backend requested from frontend");
    
    let mut process_manager = state.process_manager.lock().await;
    match process_manager.start_python_backend().await {
        Ok(_) => {
            info!("Python backend started successfully");
            Ok("Backend started successfully".to_string())
        }
        Err(e) => {
            error!("Failed to start Python backend: {}", e);
            Err(format!("Failed to start backend: {}", e))
        }
    }
}

#[tauri::command]
pub async fn stop_python_backend(state: State<'_, AppState>) -> Result<String, String> {
    info!("Stopping Python backend requested from frontend");
    
    let mut process_manager = state.process_manager.lock().await;
    match process_manager.stop_python_backend().await {
        Ok(_) => {
            info!("Python backend stopped successfully");
            Ok("Backend stopped successfully".to_string())
        }
        Err(e) => {
            error!("Failed to stop Python backend: {}", e);
            Err(format!("Failed to stop backend: {}", e))
        }
    }
}

#[tauri::command]
pub async fn get_backend_status(state: State<'_, AppState>) -> Result<ProcessStatus, String> {
    let mut process_manager = state.process_manager.lock().await;
    let mut status = process_manager.get_backend_status();
    
    // Try to get health status if process is running
    if status.is_running {
        let bridge = state.python_bridge.lock().await;
        if let Ok(health) = bridge.check_health().await {
            status.health_status = Some(health.status);
        }
    }
    
    Ok(status)
}

// ===== Project Analysis Commands =====

#[tauri::command]
pub async fn scan_project_directory(
    path: String,
    use_ai: bool,
    ai_model: Option<String>,
    state: State<'_, AppState>
) -> Result<ScanResponse, String> {
    info!("Scanning project directory: {}", path);
    
    let request = ScanRequest {
        path,
        use_ai,
        ai_model,
        max_files: 10000,
    };
    
    let bridge = state.python_bridge.lock().await;
    match bridge.scan_project_directory(request).await {
        Ok(response) => {
            info!("Project scan completed successfully");
            Ok(response)
        }
        Err(e) => {
            error!("Project scan failed: {}", e);
            Err(format!("Project scan failed: {}", e))
        }
    }
}

#[tauri::command]
pub async fn get_ollama_models(state: State<'_, AppState>) -> Result<Vec<String>, String> {
    info!("Fetching Ollama models");
    
    let bridge = state.python_bridge.lock().await;
    match bridge.get_ollama_models().await {
        Ok(response) => {
            info!("Retrieved {} Ollama models", response.models.len());
            Ok(response.models)
        }
        Err(e) => {
            warn!("Failed to get Ollama models: {}", e);
            Err(format!("Failed to get models: {}", e))
        }
    }
}

// ===== Organization Commands =====

#[tauri::command]
pub async fn preview_organization(
    scan_id: String,
    target_category: Option<String>,
    conflict_resolution: Option<String>,
    create_backup: Option<bool>,
    custom_name: Option<String>,
    state: State<'_, AppState>
) -> Result<OrganizePreviewResponse, String> {
    info!("Generating organization preview for scan: {}", scan_id);
    
    let request = OrganizePreviewRequest {
        scan_id,
        target_category,
        conflict_resolution: conflict_resolution.unwrap_or_else(|| "rename".to_string()),
        create_backup: create_backup.unwrap_or(true),
        custom_name,
    };
    
    let bridge = state.python_bridge.lock().await;
    match bridge.preview_organization(request).await {
        Ok(response) => {
            info!("Organization preview generated successfully");
            Ok(response)
        }
        Err(e) => {
            error!("Organization preview failed: {}", e);
            Err(format!("Organization preview failed: {}", e))
        }
    }
}

#[tauri::command]
pub async fn execute_organization(
    plan_id: String,
    confirm_execution: bool,
    state: State<'_, AppState>
) -> Result<OrganizeExecuteResponse, String> {
    info!("Executing organization plan: {}", plan_id);
    
    if !confirm_execution {
        return Err("Execution requires explicit confirmation".to_string());
    }
    
    let request = OrganizeExecuteRequest {
        plan_id,
        confirm_execution,
    };
    
    let bridge = state.python_bridge.lock().await;
    match bridge.execute_organization(request).await {
        Ok(response) => {
            info!("Organization execution completed: {}", response.status);
            Ok(response)
        }
        Err(e) => {
            error!("Organization execution failed: {}", e);
            Err(format!("Organization execution failed: {}", e))
        }
    }
}

#[tauri::command]
pub async fn get_organization_progress(
    operation_id: String,
    _state: State<'_, AppState>
) -> Result<OperationProgress, String> {
    // This would typically query the backend for progress
    // For now, return a placeholder since progress tracking would need WebSockets
    warn!("Progress tracking not fully implemented yet for operation: {}", operation_id);
    
    // Return a basic progress structure
    Ok(OperationProgress {
        operation_id,
        current_step: 1,
        total_steps: 1,
        current_operation: "Progress tracking not implemented".to_string(),
        files_processed: 0,
        total_files: 0,
        bytes_processed: 0,
        total_bytes: 0,
        elapsed_time_seconds: 0.0,
        estimated_remaining_seconds: 0.0,
        status: "unknown".to_string(),
        error_message: Some("Progress tracking not implemented yet".to_string()),
    })
}

// ===== File System Commands =====

#[tauri::command]
pub async fn select_directory() -> Result<Option<String>, String> {
    use tauri::api::dialog::blocking::FileDialogBuilder;
    
    info!("Opening directory selection dialog");
    
    let result = FileDialogBuilder::new()
        .set_title("Select Project Directory")
        .pick_folder();
    
    match result {
        Some(path) => {
            info!("Directory selected: {:?}", path);
            Ok(Some(path.to_string_lossy().to_string()))
        }
        None => {
            info!("Directory selection cancelled");
            Ok(None)
        }
    }
}

#[tauri::command]
pub async fn get_home_directory() -> Result<String, String> {
    match dirs::home_dir() {
        Some(path) => Ok(path.to_string_lossy().to_string()),
        None => Err("Could not determine home directory".to_string()),
    }
}

// ===== Settings Commands =====

#[tauri::command]
pub async fn get_app_settings() -> Result<AppSettings, String> {
    // For now, return default settings
    // In a real app, this would load from a config file
    info!("Loading application settings");
    Ok(AppSettings::default())
}

#[tauri::command]
pub async fn save_app_settings(settings: AppSettings) -> Result<String, String> {
    // For now, just log the settings
    // In a real app, this would save to a config file
    info!("Saving application settings: {:?}", settings);
    Ok("Settings saved successfully".to_string())
}

// ===== Project Creation Commands =====

#[tauri::command]
pub async fn create_project_from_template(
    template_id: String,
    project_name: String,
    target_directory: String,
    initialize_git: bool,
    options: std::collections::HashMap<String, String>,
    state: State<'_, AppState>
) -> Result<Value, String> {
    info!("Creating project from template: {}", template_id);
    
    let request = CreateProjectRequest {
        template_id,
        project_name,
        target_directory,
        initialize_git,
        options,
    };
    
    let bridge = state.python_bridge.lock().await;
    match bridge.create_project_from_template(request).await {
        Ok(response) => {
            info!("Project created successfully");
            Ok(response)
        }
        Err(e) => {
            error!("Project creation failed: {}", e);
            Err(format!("Project creation failed: {}", e))
        }
    }
}

#[tauri::command]
pub async fn get_project_templates(state: State<'_, AppState>) -> Result<Vec<ProjectTemplate>, String> {
    info!("Fetching project templates");
    
    let bridge = state.python_bridge.lock().await;
    match bridge.get_project_templates().await {
        Ok(templates) => {
            info!("Retrieved {} project templates", templates.len());
            Ok(templates)
        }
        Err(e) => {
            error!("Failed to get project templates: {}", e);
            Err(format!("Failed to get templates: {}", e))
        }
    }
}

// ===== Utility Commands =====

#[tauri::command]
pub async fn open_external_url(url: String) -> Result<(), String> {
    info!("Opening external URL: {}", url);
    
    match tauri::api::shell::open(&tauri::api::shell::Scope::default(), url, None) {
        Ok(_) => Ok(()),
        Err(e) => {
            error!("Failed to open URL: {}", e);
            Err(format!("Failed to open URL: {}", e))
        }
    }
}

#[tauri::command]
pub async fn show_in_folder(path: String) -> Result<(), String> {
    info!("Showing path in folder: {}", path);
    
    let path_buf = PathBuf::from(&path);
    if path_buf.exists() {
        #[cfg(target_os = "windows")]
        {
            let _ = std::process::Command::new("explorer")
                .args(["/select,", &path])
                .spawn();
        }
        
        #[cfg(target_os = "macos")]
        {
            let _ = std::process::Command::new("open")
                .args(["-R", &path])
                .spawn();
        }
        
        #[cfg(target_os = "linux")]
        {
            let _ = std::process::Command::new("xdg-open")
                .arg(path_buf.parent().unwrap_or(&path_buf))
                .spawn();
        }
        
        Ok(())
    } else {
        Err("Path does not exist".to_string())
    }
}