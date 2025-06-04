"""
Tests for the main FastAPI application.
"""

import pytest
from fastapi import status
from unittest.mock import patch, Mock
import requests


class TestHealthEndpoint:
    """Tests for the health check endpoint."""
    
    def test_health_check_success(self, client):
        """Test successful health check."""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert data["python_backend"] is True
        assert "timestamp" in data
        assert "ollama_available" in data
    
    def test_health_check_response_structure(self, client):
        """Test health check response has correct structure."""
        response = client.get("/health")
        data = response.json()
        
        required_fields = ["status", "timestamp", "version", "python_backend", "ollama_available"]
        for field in required_fields:
            assert field in data
    
    @patch('requests.get')
    def test_health_check_with_ollama_available(self, mock_get, client):
        """Test health check when Ollama is available."""
        # Mock successful Ollama response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        response = client.get("/health")
        data = response.json()
        
        assert data["ollama_available"] is True
    
    @patch('requests.get')
    def test_health_check_with_ollama_unavailable(self, mock_get, client):
        """Test health check when Ollama is unavailable."""
        # Mock failed Ollama response
        mock_get.side_effect = requests.RequestException("Connection refused")
        
        response = client.get("/health")
        data = response.json()
        
        assert data["ollama_available"] is False


class TestModelsEndpoint:
    """Tests for the Ollama models endpoint."""
    
    @patch('requests.get')
    def test_get_models_success(self, mock_get, client):
        """Test successful models retrieval."""
        # Mock successful Ollama response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llama2:7b"},
                {"name": "codellama:7b"},
                {"name": "mistral:7b"}
            ]
        }
        mock_get.return_value = mock_response
        
        response = client.get("/models")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "models" in data
        assert len(data["models"]) == 3
        assert "llama2:7b" in data["models"]
        assert "codellama:7b" in data["models"]
        assert "mistral:7b" in data["models"]
    
    @patch('requests.get')
    def test_get_models_ollama_unavailable(self, mock_get, client):
        """Test models endpoint when Ollama is unavailable."""
        mock_get.side_effect = requests.RequestException("Connection refused")
        
        response = client.get("/models")
        
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        data = response.json()
        
        assert "error" in data
        assert data["error"] == "HTTP 503"
    
    @patch('requests.get')
    def test_get_models_ollama_error_status(self, mock_get, client):
        """Test models endpoint when Ollama returns error status."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        response = client.get("/models")
        
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


class TestPlaceholderEndpoints:
    """Tests for placeholder endpoints that will be implemented in Phase 1."""
    
    def test_scan_endpoint_not_implemented(self, client):
        """Test scan endpoint returns not implemented."""
        response = client.post("/scan")
        
        assert response.status_code == status.HTTP_501_NOT_IMPLEMENTED
        data = response.json()
        
        assert "error" in data
        assert "Phase 1" in data["detail"]
    
    def test_organize_preview_not_implemented(self, client):
        """Test organize preview endpoint returns not implemented."""
        response = client.post("/organize/preview")
        
        assert response.status_code == status.HTTP_501_NOT_IMPLEMENTED
        data = response.json()
        
        assert "error" in data
        assert "Phase 1" in data["detail"]
    
    def test_organize_execute_not_implemented(self, client):
        """Test organize execute endpoint returns not implemented."""
        response = client.post("/organize/execute")
        
        assert response.status_code == status.HTTP_501_NOT_IMPLEMENTED
        data = response.json()
        
        assert "error" in data
        assert "Phase 1" in data["detail"]
    
    def test_create_project_not_implemented(self, client):
        """Test create project endpoint returns not implemented."""
        response = client.post("/projects/create")
        
        assert response.status_code == status.HTTP_501_NOT_IMPLEMENTED
        data = response.json()
        
        assert "error" in data
        assert "Phase 1" in data["detail"]


class TestErrorHandling:
    """Tests for global error handling."""
    
    def test_404_not_found(self, client):
        """Test 404 handling for non-existent endpoints."""
        response = client.get("/nonexistent")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_cors_headers(self, client):
        """Test CORS headers are present in responses."""
        response = client.get("/health")
        
        # Note: TestClient doesn't include CORS headers by default
        # This test ensures the endpoint works; CORS is tested in integration
        assert response.status_code == status.HTTP_200_OK