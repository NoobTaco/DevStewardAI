// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod python_bridge;
mod process_manager;
mod commands;

use log::{info, error};
use std::sync::Arc;
use tokio::sync::Mutex;
use tauri::{Manager, State};

use python_bridge::PythonBridge;
use process_manager::ProcessManager;
use commands::*;

// Application state
pub struct AppState {
    pub python_bridge: Arc<Mutex<PythonBridge>>,
    pub process_manager: Arc<Mutex<ProcessManager>>,
}

fn main() {
    // Initialize logging
    env_logger::init();
    info!("Starting DevSteward AI desktop application");

    // Initialize application state
    let python_bridge = Arc::new(Mutex::new(PythonBridge::new()));
    let process_manager = Arc::new(Mutex::new(ProcessManager::new()));
    
    let app_state = AppState {
        python_bridge,
        process_manager,
    };

    tauri::Builder::default()
        .manage(app_state)
        .invoke_handler(tauri::generate_handler![
            // System commands
            check_health,
            start_python_backend,
            stop_python_backend,
            get_backend_status,
            
            // Project analysis commands
            scan_project_directory,
            get_ollama_models,
            
            // Organization commands
            preview_organization,
            execute_organization,
            get_organization_progress,
            
            // File system commands
            select_directory,
            get_home_directory,
            
            // Settings commands
            get_app_settings,
            save_app_settings,
            
            // Project creation commands (placeholder)
            create_project_from_template,
            get_project_templates
        ])
        .setup(|app| {
            let app_handle = app.handle();
            
            // Start the Python backend process in the background
            tauri::async_runtime::spawn(async move {
                let state: State<AppState> = app_handle.state();
                let mut process_manager = state.process_manager.lock().await;
                
                match process_manager.start_python_backend().await {
                    Ok(_) => info!("Python backend started successfully"),
                    Err(e) => error!("Failed to start Python backend: {}", e),
                }
            });
            
            Ok(())
        })
        .on_window_event(|event| match event.event() {
            tauri::WindowEvent::CloseRequested { .. } => {
                info!("Application closing, cleaning up...");
                // Cleanup will be handled by the Drop implementation
            }
            _ => {}
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}