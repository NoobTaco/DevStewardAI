"""
Pytest configuration and fixtures for DevSteward AI tests.
"""

import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    """
    Create a test client for the FastAPI application.
    """
    return TestClient(app)


@pytest.fixture
def sample_project_data():
    """
    Sample project data for testing.
    """
    return {
        "path": "/test/project",
        "files": [
            "package.json",
            "src/index.js",
            "src/components/App.vue",
            "README.md"
        ],
        "file_extensions": {
            ".js": 2,
            ".vue": 1,
            ".json": 1,
            ".md": 1
        },
        "key_files": ["package.json"],
        "readme_content": "# Test Project\nA sample Vue.js project for testing."
    }


@pytest.fixture
def sample_scan_result():
    """
    Sample directory scan result for testing.
    """
    return {
        "scan_id": "test-scan-123",
        "path": "/test/project",
        "total_files": 5,
        "file_types": {
            "JavaScript": 2,
            "Vue": 1,
            "JSON": 1,
            "Markdown": 1
        },
        "key_indicators": ["package.json", "vue"],
        "heuristic_classification": {
            "category": "Web/Frontend",
            "confidence": 0.85,
            "reasoning": "Vue.js project with package.json"
        },
        "ai_classification": None
    }


@pytest.fixture
def sample_organization_plan():
    """
    Sample organization plan for testing.
    """
    return {
        "scan_id": "test-scan-123",
        "source_path": "/test/project",
        "target_path": "/organized/Personal/Web/Frontend/test-project",
        "operations": [
            {
                "type": "move",
                "source": "/test/project",
                "target": "/organized/Personal/Web/Frontend/test-project",
                "files_count": 5
            }
        ],
        "classification": {
            "category": "Web/Frontend",
            "confidence": 0.85,
            "method": "heuristic"
        },
        "conflicts": [],
        "estimated_time": 2.5
    }


@pytest.fixture
def mock_ollama_response():
    """
    Mock Ollama API response for testing.
    """
    return {
        "model": "llama2",
        "response": '''{"category": "Web/Frontend", "confidence": 0.9, "reasoning": "Vue.js project with modern frontend structure"}'''
    }