use log::{info, warn, error, debug};
use reqwest::Client;
use serde_json::Value;
use std::collections::HashMap;
use std::time::Duration;
use thiserror::Error;

use crate::types::*;

#[derive(Error, Debug)]
pub enum BridgeError {
    #[error("HTTP request failed: {0}")]
    RequestFailed(#[from] reqwest::Error),
    #[error("JSON parsing failed: {0}")]
    JsonError(#[from] serde_json::Error),
    #[error("Backend not available")]
    BackendNotAvailable,
    #[error("Invalid response from backend: {0}")]
    InvalidResponse(String),
    #[error("Backend returned error: {0}")]
    BackendError(String),
}

pub struct PythonBridge {
    client: Client,
    base_url: String,
}

impl PythonBridge {
    pub fn new() -> Self {
        let client = Client::builder()
            .timeout(Duration::from_secs(30))
            .build()
            .expect("Failed to create HTTP client");

        Self {
            client,
            base_url: "http://127.0.0.1:8008".to_string(),
        }
    }

    pub fn set_base_url(&mut self, url: String) {
        self.base_url = url;
    }

    /// Check backend health
    pub async fn check_health(&self) -> Result<HealthResponse, BridgeError> {
        debug!("Checking backend health");
        let url = format!("{}/health", self.base_url);
        
        let response = self.client
            .get(&url)
            .send()
            .await?;

        if response.status().is_success() {
            let health: HealthResponse = response.json().await?;
            Ok(health)
        } else {
            Err(BridgeError::BackendNotAvailable)
        }
    }

    /// Get available Ollama models
    pub async fn get_ollama_models(&self) -> Result<ModelsResponse, BridgeError> {
        debug!("Fetching Ollama models");
        let url = format!("{}/models", self.base_url);
        
        let response = self.client
            .get(&url)
            .send()
            .await?;

        if response.status().is_success() {
            let models: ModelsResponse = response.json().await?;
            Ok(models)
        } else {
            let error_text = response.text().await.unwrap_or_else(|_| "Unknown error".to_string());
            Err(BridgeError::BackendError(error_text))
        }
    }

    /// Scan a project directory
    pub async fn scan_project_directory(&self, request: ScanRequest) -> Result<ScanResponse, BridgeError> {
        info!("Scanning project directory: {}", request.path);
        let url = format!("{}/scan", self.base_url);
        
        let response = self.client
            .post(&url)
            .json(&request)
            .send()
            .await?;

        if response.status().is_success() {
            let scan_result: ScanResponse = response.json().await?;
            info!("Scan completed successfully: {}", scan_result.scan_id);
            Ok(scan_result)
        } else {
            let error_text = response.text().await.unwrap_or_else(|_| "Unknown error".to_string());
            error!("Scan failed: {}", error_text);
            Err(BridgeError::BackendError(error_text))
        }
    }

    /// Preview organization plan
    pub async fn preview_organization(&self, request: OrganizePreviewRequest) -> Result<OrganizePreviewResponse, BridgeError> {
        info!("Generating organization preview for scan: {}", request.scan_id);
        let url = format!("{}/organize/preview", self.base_url);
        
        let response = self.client
            .post(&url)
            .json(&request)
            .send()
            .await?;

        if response.status().is_success() {
            let preview: OrganizePreviewResponse = response.json().await?;
            info!("Organization preview generated: {} operations", preview.total_operations);
            Ok(preview)
        } else {
            let error_text = response.text().await.unwrap_or_else(|_| "Unknown error".to_string());
            error!("Organization preview failed: {}", error_text);
            Err(BridgeError::BackendError(error_text))
        }
    }

    /// Execute organization plan
    pub async fn execute_organization(&self, request: OrganizeExecuteRequest) -> Result<OrganizeExecuteResponse, BridgeError> {
        info!("Executing organization plan: {}", request.plan_id);
        let url = format!("{}/organize/execute", self.base_url);
        
        let response = self.client
            .post(&url)
            .json(&request)
            .send()
            .await?;

        if response.status().is_success() {
            let execute_result: OrganizeExecuteResponse = response.json().await?;
            info!("Organization execution status: {}", execute_result.status);
            Ok(execute_result)
        } else {
            let error_text = response.text().await.unwrap_or_else(|_| "Unknown error".to_string());
            error!("Organization execution failed: {}", error_text);
            Err(BridgeError::BackendError(error_text))
        }
    }

    /// Create a new project from template
    pub async fn create_project_from_template(&self, request: CreateProjectRequest) -> Result<Value, BridgeError> {
        info!("Creating project from template: {}", request.template_id);
        let url = format!("{}/projects/create", self.base_url);
        
        let response = self.client
            .post(&url)
            .json(&request)
            .send()
            .await?;

        if response.status().is_success() {
            let result: Value = response.json().await?;
            info!("Project created successfully");
            Ok(result)
        } else if response.status() == 501 {
            // Not implemented yet - expected
            warn!("Project creation not implemented yet in backend");
            Err(BridgeError::BackendError("Project creation not implemented yet".to_string()))
        } else {
            let error_text = response.text().await.unwrap_or_else(|_| "Unknown error".to_string());
            error!("Project creation failed: {}", error_text);
            Err(BridgeError::BackendError(error_text))
        }
    }

    /// Get available project templates
    pub async fn get_project_templates(&self) -> Result<Vec<ProjectTemplate>, BridgeError> {
        debug!("Fetching project templates");
        // For now, return hardcoded templates since backend doesn't implement this yet
        let templates = vec![
            ProjectTemplate {
                id: "python_utility".to_string(),
                name: "Python Utility".to_string(),
                description: "Basic Python script with dependencies and documentation".to_string(),
                category: "SystemUtilities".to_string(),
                language: "Python".to_string(),
                features: vec!["README.md".to_string(), "requirements.txt".to_string(), ".gitignore".to_string()],
            },
            ProjectTemplate {
                id: "static_website".to_string(),
                name: "Static Website".to_string(),
                description: "Basic HTML/CSS/JS website structure".to_string(),
                category: "Web".to_string(),
                language: "HTML/CSS/JS".to_string(),
                features: vec!["index.html".to_string(), "style.css".to_string(), "script.js".to_string()],
            },
        ];

        Ok(templates)
    }

    /// Make a generic GET request to the backend
    pub async fn get_request(&self, endpoint: &str) -> Result<Value, BridgeError> {
        let url = format!("{}{}", self.base_url, endpoint);
        debug!("Making GET request to: {}", url);
        
        let response = self.client
            .get(&url)
            .send()
            .await?;

        if response.status().is_success() {
            let result: Value = response.json().await?;
            Ok(result)
        } else {
            let error_text = response.text().await.unwrap_or_else(|_| "Unknown error".to_string());
            Err(BridgeError::BackendError(error_text))
        }
    }

    /// Make a generic POST request to the backend
    pub async fn post_request(&self, endpoint: &str, data: &Value) -> Result<Value, BridgeError> {
        let url = format!("{}{}", self.base_url, endpoint);
        debug!("Making POST request to: {}", url);
        
        let response = self.client
            .post(&url)
            .json(data)
            .send()
            .await?;

        if response.status().is_success() {
            let result: Value = response.json().await?;
            Ok(result)
        } else {
            let error_text = response.text().await.unwrap_or_else(|_| "Unknown error".to_string());
            Err(BridgeError::BackendError(error_text))
        }
    }

    /// Test connectivity to the backend
    pub async fn test_connectivity(&self) -> bool {
        match self.check_health().await {
            Ok(_) => {
                debug!("Backend connectivity test passed");
                true
            }
            Err(e) => {
                debug!("Backend connectivity test failed: {}", e);
                false
            }
        }
    }

    /// Get backend base URL
    pub fn get_base_url(&self) -> &str {
        &self.base_url
    }
}