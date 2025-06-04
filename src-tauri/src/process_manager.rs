use log::{info, warn, error, debug};
use std::process::{Child, Command, Stdio};
use std::time::{Duration, Instant};
use thiserror::Error;
use tokio::time::sleep;

use crate::types::ProcessStatus;

#[derive(Error, Debug)]
pub enum ProcessError {
    #[error("Failed to start process: {0}")]
    StartFailed(String),
    #[error("Process not found")]
    ProcessNotFound,
    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),
    #[error("Process communication failed: {0}")]
    CommunicationFailed(String),
}

pub struct ProcessManager {
    python_process: Option<Child>,
    start_time: Option<Instant>,
    port: u16,
}

impl ProcessManager {
    pub fn new() -> Self {
        Self {
            python_process: None,
            start_time: None,
            port: 8008,
        }
    }

    /// Start the Python FastAPI backend process
    pub async fn start_python_backend(&mut self) -> Result<(), ProcessError> {
        info!("Starting Python backend process...");

        // Kill existing process if running
        if self.is_backend_running() {
            warn!("Backend already running, stopping first");
            self.stop_python_backend().await?;
        }

        // Find the Python executable path
        let python_path = self.find_python_executable()?;
        let backend_path = self.get_backend_path()?;

        debug!("Using Python: {}", python_path);
        debug!("Backend path: {}", backend_path);

        // Start the process
        let mut child = Command::new(&python_path)
            .args(&["-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", &self.port.to_string()])
            .current_dir(&backend_path)
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .map_err(|e| ProcessError::StartFailed(format!("Failed to spawn process: {}", e)))?;

        info!("Python backend started with PID: {}", child.id());

        // Store the process
        self.python_process = Some(child);
        self.start_time = Some(Instant::now());

        // Wait for the backend to be ready
        self.wait_for_backend_ready().await?;

        info!("Python backend is ready and accepting connections");
        Ok(())
    }

    /// Stop the Python backend process
    pub async fn stop_python_backend(&mut self) -> Result<(), ProcessError> {
        if let Some(mut child) = self.python_process.take() {
            info!("Stopping Python backend process (PID: {})", child.id());

            // Try graceful shutdown first
            match child.kill() {
                Ok(_) => {
                    // Wait for process to exit
                    match child.wait() {
                        Ok(status) => {
                            info!("Python backend stopped with status: {}", status);
                        }
                        Err(e) => {
                            warn!("Error waiting for process to exit: {}", e);
                        }
                    }
                }
                Err(e) => {
                    error!("Failed to kill Python backend process: {}", e);
                    return Err(ProcessError::CommunicationFailed(format!("Kill failed: {}", e)));
                }
            }

            self.start_time = None;
        } else {
            debug!("No Python backend process to stop");
        }

        Ok(())
    }

    /// Check if the backend process is running
    pub fn is_backend_running(&mut self) -> bool {
        if let Some(ref mut child) = self.python_process {
            match child.try_wait() {
                Ok(Some(_)) => {
                    // Process has exited
                    debug!("Python backend process has exited");
                    self.python_process = None;
                    self.start_time = None;
                    false
                }
                Ok(None) => {
                    // Process is still running
                    true
                }
                Err(e) => {
                    error!("Error checking process status: {}", e);
                    false
                }
            }
        } else {
            false
        }
    }

    /// Get detailed status of the backend process
    pub fn get_backend_status(&mut self) -> ProcessStatus {
        let is_running = self.is_backend_running();
        let pid = self.python_process.as_ref().map(|child| child.id());
        let uptime_seconds = self.start_time.map(|start| start.elapsed().as_secs());

        ProcessStatus {
            is_running,
            pid,
            port: self.port,
            uptime_seconds,
            health_status: None, // Will be filled by health check
        }
    }

    /// Wait for the backend to be ready by polling the health endpoint
    async fn wait_for_backend_ready(&self) -> Result<(), ProcessError> {
        let max_attempts = 30; // 30 seconds timeout
        let mut attempts = 0;

        info!("Waiting for Python backend to be ready...");

        while attempts < max_attempts {
            match self.check_backend_health().await {
                Ok(true) => {
                    return Ok(());
                }
                Ok(false) => {
                    debug!("Backend not ready yet, retrying... (attempt {}/{})", attempts + 1, max_attempts);
                }
                Err(e) => {
                    debug!("Health check failed: {} (attempt {}/{})", e, attempts + 1, max_attempts);
                }
            }

            attempts += 1;
            sleep(Duration::from_secs(1)).await;
        }

        Err(ProcessError::CommunicationFailed(
            "Backend failed to become ready within timeout".to_string()
        ))
    }

    /// Check if the backend is healthy by calling the health endpoint
    async fn check_backend_health(&self) -> Result<bool, ProcessError> {
        let client = reqwest::Client::new();
        let url = format!("http://127.0.0.1:{}/health", self.port);

        match client.get(&url).timeout(Duration::from_secs(5)).send().await {
            Ok(response) => {
                if response.status().is_success() {
                    Ok(true)
                } else {
                    debug!("Health check returned status: {}", response.status());
                    Ok(false)
                }
            }
            Err(e) => {
                debug!("Health check request failed: {}", e);
                Ok(false)
            }
        }
    }

    /// Find the Python executable (preferring virtual environment)
    fn find_python_executable(&self) -> Result<String, ProcessError> {
        let backend_path = self.get_backend_path()?;
        
        // Try virtual environment first
        let venv_python = format!("{}/venv/bin/python", backend_path);
        if std::path::Path::new(&venv_python).exists() {
            return Ok(venv_python);
        }

        // Try alternative venv path on Windows
        let venv_python_win = format!("{}/venv/Scripts/python.exe", backend_path);
        if std::path::Path::new(&venv_python_win).exists() {
            return Ok(venv_python_win);
        }

        // Fall back to system Python
        Ok("python3".to_string())
    }

    /// Get the path to the Python backend directory
    fn get_backend_path(&self) -> Result<String, ProcessError> {
        let current_exe = std::env::current_exe()
            .map_err(|e| ProcessError::IoError(e))?;
        
        let app_dir = current_exe
            .parent()
            .ok_or_else(|| ProcessError::StartFailed("Cannot determine app directory".to_string()))?;

        // In development, go up to find src-py
        let backend_path = app_dir
            .parent()
            .and_then(|p| p.parent())
            .map(|p| p.join("src-py"))
            .ok_or_else(|| ProcessError::StartFailed("Cannot find backend directory".to_string()))?;

        Ok(backend_path.to_string_lossy().to_string())
    }

    /// Set the port for the backend
    pub fn set_port(&mut self, port: u16) {
        self.port = port;
    }

    /// Get the current port
    pub fn get_port(&self) -> u16 {
        self.port
    }
}

impl Drop for ProcessManager {
    fn drop(&mut self) {
        if self.python_process.is_some() {
            warn!("ProcessManager dropping with active process, attempting cleanup");
            // Note: We can't use async here, so we do a synchronous kill
            if let Some(mut child) = self.python_process.take() {
                let _ = child.kill();
                let _ = child.wait();
            }
        }
    }
}