"""
Tests for project_analyzer.py module.
These tests will validate the project scanning and classification logic.
"""

import pytest
from unittest.mock import patch, Mock, MagicMock
import tempfile
import json
from pathlib import Path


class TestProjectAnalyzer:
    """Tests for project analysis functionality (to be implemented)."""
    
    def test_scan_directory_basic_structure(self):
        """Test basic directory scanning structure."""
        # This test will be implemented when we create project_analyzer.py
        # For now, we're setting up the test structure
        
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir)
            
            # Create test project structure
            (test_path / "package.json").write_text('{"name": "test-project"}')
            (test_path / "src").mkdir()
            (test_path / "src" / "index.js").write_text("console.log('hello');")
            (test_path / "README.md").write_text("# Test Project")
            
            # Test directory exists and has expected structure
            assert test_path.exists()
            assert (test_path / "package.json").exists()
            assert (test_path / "src" / "index.js").exists()
            assert (test_path / "README.md").exists()
    
    def test_file_extension_analysis(self):
        """Test file extension counting and analysis."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir)
            
            # Create files with different extensions
            (test_path / "file1.js").touch()
            (test_path / "file2.js").touch()
            (test_path / "file1.py").touch()
            (test_path / "file1.vue").touch()
            (test_path / "README.md").touch()
            
            # Count extensions manually for testing
            extensions = {}
            for file in test_path.iterdir():
                if file.is_file():
                    ext = file.suffix
                    extensions[ext] = extensions.get(ext, 0) + 1
            
            assert extensions[".js"] == 2
            assert extensions[".py"] == 1
            assert extensions[".vue"] == 1
            assert extensions[".md"] == 1
    
    def test_key_file_detection(self):
        """Test detection of key project files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir)
            
            # Create key files for different project types
            key_files = [
                "package.json",      # Node.js
                "Cargo.toml",        # Rust
                "requirements.txt",  # Python
                "pom.xml",          # Java Maven
                "Gemfile",          # Ruby
                ".gitignore"        # Git
            ]
            
            for key_file in key_files:
                (test_path / key_file).touch()
            
            # Verify all key files exist
            detected_key_files = []
            for file in test_path.iterdir():
                if file.name in [
                    "package.json", "Cargo.toml", "requirements.txt", 
                    "pom.xml", "Gemfile", ".gitignore"
                ]:
                    detected_key_files.append(file.name)
            
            assert len(detected_key_files) == 6
            assert "package.json" in detected_key_files
            assert "Cargo.toml" in detected_key_files


class TestHeuristicClassification:
    """Tests for heuristic project classification (to be implemented)."""
    
    def test_javascript_project_detection(self):
        """Test detection of JavaScript/Node.js projects."""
        project_data = {
            "key_files": ["package.json"],
            "extensions": {".js": 10, ".json": 2},
            "readme_content": "# My Node.js App\nA simple Express application"
        }
        
        # Mock classification logic
        def classify_project(data):
            if "package.json" in data["key_files"]:
                if ".vue" in data["extensions"]:
                    return {"category": "Web/Frontend", "confidence": 0.8}
                elif ".js" in data["extensions"]:
                    return {"category": "Web/Backend", "confidence": 0.7}
            return {"category": "Misc", "confidence": 0.3}
        
        result = classify_project(project_data)
        assert result["category"] == "Web/Backend"
        assert result["confidence"] >= 0.7
    
    def test_python_project_detection(self):
        """Test detection of Python projects."""
        project_data = {
            "key_files": ["requirements.txt", "setup.py"],
            "extensions": {".py": 15, ".txt": 2},
            "readme_content": "# Python ML Project\nMachine learning utilities"
        }
        
        # Mock classification logic for Python
        def classify_python_project(data):
            if any(file in data["key_files"] for file in ["requirements.txt", "setup.py"]):
                if "machine learning" in data["readme_content"].lower():
                    return {"category": "DataScience", "confidence": 0.9}
                else:
                    return {"category": "SystemUtilities/Python", "confidence": 0.8}
            return {"category": "Misc", "confidence": 0.3}
        
        result = classify_python_project(project_data)
        assert result["category"] == "DataScience"
        assert result["confidence"] >= 0.8
    
    def test_rust_project_detection(self):
        """Test detection of Rust projects."""
        project_data = {
            "key_files": ["Cargo.toml"],
            "extensions": {".rs": 8, ".toml": 1},
            "readme_content": "# CLI Tool\nA command line utility written in Rust"
        }
        
        # Mock classification logic for Rust
        def classify_rust_project(data):
            if "Cargo.toml" in data["key_files"]:
                return {"category": "SystemUtilities/Rust", "confidence": 0.85}
            return {"category": "Misc", "confidence": 0.3}
        
        result = classify_rust_project(project_data)
        assert result["category"] == "SystemUtilities/Rust"
        assert result["confidence"] >= 0.8


class TestOllamaIntegration:
    """Tests for Ollama AI integration (to be implemented)."""
    
    @patch('requests.post')
    def test_ollama_classification_success(self, mock_post):
        """Test successful Ollama classification."""
        # Mock successful Ollama response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "llama2",
            "response": json.dumps({
                "category": "Web/Frontend",
                "confidence": 0.92,
                "reasoning": "Vue.js project with modern frontend architecture"
            })
        }
        mock_post.return_value = mock_response
        
        # Mock project data
        project_data = {
            "key_files": ["package.json"],
            "extensions": {".vue": 5, ".js": 3, ".css": 2},
            "readme_content": "# Vue.js Dashboard\nModern dashboard built with Vue 3"
        }
        
        # This will be the actual function call when implemented
        # result = classify_with_ollama(project_data)
        
        # For now, test the mock response
        response = mock_post.return_value
        assert response.status_code == 200
        
        data = json.loads(response.json()["response"])
        assert data["category"] == "Web/Frontend"
        assert data["confidence"] >= 0.9
        assert "reasoning" in data
    
    @patch('requests.post')
    def test_ollama_classification_failure(self, mock_post):
        """Test Ollama classification failure handling."""
        # Mock failed Ollama response
        mock_post.side_effect = Exception("Connection timeout")
        
        project_data = {
            "key_files": ["package.json"],
            "extensions": {".js": 5},
            "readme_content": "# Test Project"
        }
        
        # Test that we handle failures gracefully
        # This should fall back to heuristic classification
        try:
            mock_post("http://localhost:11434/api/generate", json={})
            assert False, "Should have raised an exception"
        except Exception as e:
            assert "Connection timeout" in str(e)
    
    def test_ollama_prompt_structure(self):
        """Test Ollama prompt structure and formatting."""
        project_data = {
            "key_files": ["package.json", ".gitignore"],
            "extensions": {".vue": 3, ".js": 2, ".css": 1},
            "readme_content": "# My Vue App\nA beautiful dashboard"
        }
        
        # Mock prompt generation
        def generate_prompt(data):
            prompt = f"""
            Analyze this project and classify it:
            
            Files: {', '.join(data['key_files'])}
            Extensions: {', '.join(data['extensions'].keys())}
            README: {data['readme_content'][:100]}...
            
            Valid categories:
            - Web/Frontend, Web/Backend, Web/FullStack
            - Mobile/CrossPlatform
            - SystemUtilities/{{language}}
            - DataScience
            - Misc
            
            Respond with JSON only:
            {{"category": "exact category", "confidence": 0.0-1.0, "reasoning": "brief explanation"}}
            """
            return prompt.strip()
        
        prompt = generate_prompt(project_data)
        
        assert "package.json" in prompt
        assert ".vue" in prompt
        assert "My Vue App" in prompt
        assert "JSON only" in prompt
        assert "category" in prompt
        assert "confidence" in prompt


class TestClassificationValidation:
    """Tests for classification result validation."""
    
    def test_valid_categories(self):
        """Test validation of classification categories."""
        valid_categories = [
            "Web/Frontend",
            "Web/Backend", 
            "Web/FullStack",
            "Mobile/CrossPlatform",
            "SystemUtilities/Python",
            "SystemUtilities/Rust",
            "SystemUtilities/Go",
            "Games/Unity",
            "Games/Godot",
            "Libraries/Python",
            "DataScience",
            "Misc"
        ]
        
        # Test each category is valid
        for category in valid_categories:
            assert "/" in category or category == "Misc" or category == "DataScience"
    
    def test_confidence_range_validation(self):
        """Test confidence score validation."""
        valid_confidences = [0.0, 0.5, 0.7, 0.85, 1.0]
        invalid_confidences = [-0.1, 1.1, 2.0, -1.0]
        
        for confidence in valid_confidences:
            assert 0.0 <= confidence <= 1.0
        
        for confidence in invalid_confidences:
            assert not (0.0 <= confidence <= 1.0)
    
    def test_classification_result_structure(self):
        """Test classification result structure."""
        sample_result = {
            "category": "Web/Frontend",
            "confidence": 0.85,
            "reasoning": "Vue.js project with component structure",
            "method": "ollama"  # or "heuristic"
        }
        
        required_fields = ["category", "confidence", "reasoning"]
        for field in required_fields:
            assert field in sample_result
        
        assert isinstance(sample_result["confidence"], (int, float))
        assert 0.0 <= sample_result["confidence"] <= 1.0