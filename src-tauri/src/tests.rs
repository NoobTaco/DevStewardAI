#[cfg(test)]
mod tests {
    use super::*;
    use crate::python_bridge::PythonBridge;
    use crate::process_manager::ProcessManager;
    use crate::types::*;
    use std::sync::Arc;
    use tokio::sync::Mutex;

    /// Test that PythonBridge can be created
    #[test]
    fn test_python_bridge_creation() {
        let bridge = PythonBridge::new();
        assert_eq!(bridge.get_base_url(), "http://127.0.0.1:8008");
    }

    /// Test that ProcessManager can be created
    #[test]
    fn test_process_manager_creation() {
        let manager = ProcessManager::new();
        assert_eq!(manager.get_port(), 8008);
    }

    /// Test AppSettings default values
    #[test]
    fn test_app_settings_defaults() {
        let settings = AppSettings::default();
        assert_eq!(settings.python_backend_port, 8008);
        assert_eq!(settings.ollama_base_url, "http://localhost:11434");
        assert_eq!(settings.default_ai_model, "llama2");
        assert!(settings.create_backup_by_default);
        assert!(settings.use_ai_by_default);
    }

    /// Test ScanRequest serialization
    #[test]
    fn test_scan_request_serialization() {
        let request = ScanRequest {
            path: "/test/path".to_string(),
            use_ai: true,
            ai_model: Some("llama2".to_string()),
            max_files: 5000,
        };

        let json = serde_json::to_string(&request).unwrap();
        assert!(json.contains("test/path"));
        assert!(json.contains("llama2"));
    }

    /// Test OrganizePreviewRequest with defaults
    #[test]
    fn test_organize_preview_request_defaults() {
        let json = r#"{"scan_id": "test_scan"}"#;
        let request: OrganizePreviewRequest = serde_json::from_str(json).unwrap();
        
        assert_eq!(request.scan_id, "test_scan");
        assert_eq!(request.conflict_resolution, "rename");
        assert!(request.create_backup);
        assert!(request.target_category.is_none());
    }

    /// Test ProcessStatus creation
    #[test]
    fn test_process_status() {
        let status = ProcessStatus {
            is_running: true,
            pid: Some(12345),
            port: 8008,
            uptime_seconds: Some(120),
            health_status: Some("healthy".to_string()),
        };

        assert!(status.is_running);
        assert_eq!(status.pid, Some(12345));
        assert_eq!(status.port, 8008);
    }

    /// Test error serialization
    #[test]
    fn test_error_response_serialization() {
        let error = ErrorResponse {
            error: "TestError".to_string(),
            detail: "This is a test error".to_string(),
            timestamp: "2024-01-01T00:00:00Z".to_string(),
        };

        let json = serde_json::to_string(&error).unwrap();
        assert!(json.contains("TestError"));
        assert!(json.contains("This is a test error"));
    }

    /// Test project template structure
    #[test]
    fn test_project_template() {
        let template = ProjectTemplate {
            id: "python_util".to_string(),
            name: "Python Utility".to_string(),
            description: "A simple Python utility".to_string(),
            category: "SystemUtilities".to_string(),
            language: "Python".to_string(),
            features: vec!["requirements.txt".to_string(), "README.md".to_string()],
        };

        assert_eq!(template.category, "SystemUtilities");
        assert_eq!(template.features.len(), 2);
    }
}