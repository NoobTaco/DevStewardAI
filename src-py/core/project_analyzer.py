"""
Project Analyzer - Core logic for scanning and classifying projects.

This module provides functionality to:
- Recursively scan project directories
- Analyze file types and detect key project indicators
- Extract and process README content
- Apply heuristic classification rules
- Integrate with Ollama for AI-powered classification
- Generate detailed project analysis reports
"""

import os
import logging
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import requests
from datetime import datetime

# Configure logger for this module
logger = logging.getLogger(__name__)


@dataclass
class ProjectScanResult:
    """Structured result from a project directory scan."""
    scan_id: str
    path: str
    total_files: int
    total_directories: int
    file_extensions: Dict[str, int]  # Extension -> count
    key_files: List[str]
    readme_content: Optional[str]
    largest_files: List[Tuple[str, int]]  # (filename, size_bytes)
    scan_timestamp: datetime
    scan_duration_ms: int


@dataclass
class ClassificationResult:
    """Result from project classification (heuristic or AI)."""
    category: str
    confidence: float
    reasoning: str
    method: str  # "heuristic" or "ollama"
    suggested_name: Optional[str] = None
    subcategory: Optional[str] = None


@dataclass
class ProjectAnalysis:
    """Complete analysis combining scan results and classification."""
    scan_result: ProjectScanResult
    heuristic_classification: ClassificationResult
    ai_classification: Optional[ClassificationResult]
    final_classification: ClassificationResult
    metadata: Dict[str, Any]


class ProjectAnalyzer:
    """Main class for analyzing and classifying development projects."""
    
    # Key files that indicate specific project types
    KEY_FILES = {
        # JavaScript/Node.js
        'package.json': 'nodejs',
        'yarn.lock': 'nodejs',
        'package-lock.json': 'nodejs',
        
        # Python
        'requirements.txt': 'python',
        'setup.py': 'python', 
        'pyproject.toml': 'python',
        'Pipfile': 'python',
        'poetry.lock': 'python',
        
        # Rust
        'Cargo.toml': 'rust',
        'Cargo.lock': 'rust',
        
        # Go
        'go.mod': 'go',
        'go.sum': 'go',
        
        # Java
        'pom.xml': 'java',
        'build.gradle': 'java',
        'build.gradle.kts': 'java',
        
        # C/C++
        'CMakeLists.txt': 'cpp',
        'Makefile': 'cpp',
        'configure.ac': 'cpp',
        
        # .NET
        '*.csproj': 'dotnet',
        '*.sln': 'dotnet',
        
        # PHP
        'composer.json': 'php',
        
        # Ruby
        'Gemfile': 'ruby',
        'Rakefile': 'ruby',
        
        # Docker
        'Dockerfile': 'docker',
        'docker-compose.yml': 'docker',
        'docker-compose.yaml': 'docker',
        
        # Configuration
        '.gitignore': 'git',
        'README.md': 'docs',
        'README.rst': 'docs',
        'LICENSE': 'docs'
    }
    
    # File extensions and their associated languages/types
    EXTENSION_MAPPING = {
        # Web frontend
        '.vue': 'vue',
        '.jsx': 'react',
        '.tsx': 'react', 
        '.angular.ts': 'angular',
        '.svelte': 'svelte',
        '.html': 'web',
        '.css': 'web',
        '.scss': 'web',
        '.sass': 'web',
        '.less': 'web',
        
        # JavaScript/TypeScript
        '.js': 'javascript',
        '.ts': 'typescript',
        '.mjs': 'javascript',
        '.cjs': 'javascript',
        
        # Python
        '.py': 'python',
        '.pyx': 'python',
        '.pyi': 'python',
        '.ipynb': 'jupyter',
        
        # Systems languages
        '.rs': 'rust',
        '.go': 'go',
        '.c': 'c',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.h': 'c_header',
        '.hpp': 'cpp_header',
        
        # JVM languages
        '.java': 'java',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.clj': 'clojure',
        
        # Mobile
        '.swift': 'swift',
        '.dart': 'dart',
        
        # Other languages
        '.rb': 'ruby',
        '.php': 'php',
        '.cs': 'csharp',
        '.fs': 'fsharp',
        '.vb': 'vb',
        '.lua': 'lua',
        '.r': 'r',
        '.jl': 'julia',
        '.elm': 'elm',
        '.ex': 'elixir',
        '.erl': 'erlang',
        
        # Game engines
        '.unity': 'unity',
        '.gd': 'godot',
        '.tscn': 'godot',
        
        # Data/Config
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.toml': 'toml',
        '.xml': 'xml',
        '.md': 'markdown',
        '.rst': 'rst',
        '.tex': 'latex'
    }
    
    def __init__(self, ollama_base_url: str = "http://localhost:11434"):
        """Initialize the project analyzer."""
        self.ollama_base_url = ollama_base_url
        
    def scan_directory(self, project_path: str, max_files: int = 10000) -> ProjectScanResult:
        """
        Recursively scan a directory and analyze its contents.
        
        Args:
            project_path: Path to the project directory
            max_files: Maximum number of files to scan (safety limit)
            
        Returns:
            ProjectScanResult with detailed analysis
        """
        start_time = datetime.now()
        scan_id = f"scan_{int(start_time.timestamp())}"
        
        logger.info(f"Starting directory scan: {project_path}")
        
        project_path = Path(project_path).resolve()
        if not project_path.exists():
            raise FileNotFoundError(f"Project path does not exist: {project_path}")
        if not project_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {project_path}")
        
        file_extensions = Counter()
        key_files = []
        total_files = 0
        total_directories = 0
        file_sizes = []
        readme_content = None
        
        # Directories to skip (common build/cache directories)
        skip_dirs = {
            'node_modules', '.git', '.svn', '.hg', '__pycache__', 
            'target', 'build', 'dist', '.venv', 'venv', '.env',
            '.pytest_cache', '.coverage', 'htmlcov', '.mypy_cache',
            '.tox', '.nox', 'vendor', 'deps', '_build'
        }
        
        try:
            for root, dirs, files in os.walk(project_path):
                # Filter out directories we want to skip
                dirs[:] = [d for d in dirs if d not in skip_dirs]
                
                total_directories += len(dirs)
                
                for file in files:
                    total_files += 1
                    if total_files > max_files:
                        logger.warning(f"Reached max file limit ({max_files}), stopping scan")
                        break
                    
                    file_path = Path(root) / file
                    
                    # Count file extensions
                    extension = file_path.suffix.lower()
                    if extension:
                        file_extensions[extension] += 1
                    
                    # Check for key files
                    if file.lower() in [k.lower() for k in self.KEY_FILES.keys()]:
                        key_files.append(file)
                    
                    # Extract README content
                    if file.lower().startswith('readme') and readme_content is None:
                        try:
                            readme_content = self._extract_readme_content(file_path)
                        except Exception as e:
                            logger.warning(f"Could not read README {file_path}: {e}")
                    
                    # Track file sizes for largest files
                    try:
                        size = file_path.stat().st_size
                        file_sizes.append((str(file_path.relative_to(project_path)), size))
                    except Exception as e:
                        logger.debug(f"Could not get size for {file_path}: {e}")
                
                if total_files > max_files:
                    break
        
        except Exception as e:
            logger.error(f"Error during directory scan: {e}")
            raise
        
        # Get largest files (top 10)
        largest_files = sorted(file_sizes, key=lambda x: x[1], reverse=True)[:10]
        
        end_time = datetime.now()
        scan_duration = int((end_time - start_time).total_seconds() * 1000)
        
        result = ProjectScanResult(
            scan_id=scan_id,
            path=str(project_path),
            total_files=total_files,
            total_directories=total_directories,
            file_extensions=dict(file_extensions),
            key_files=key_files,
            readme_content=readme_content,
            largest_files=largest_files,
            scan_timestamp=start_time,
            scan_duration_ms=scan_duration
        )
        
        logger.info(f"Scan complete: {total_files} files, {total_directories} dirs in {scan_duration}ms")
        return result
    
    def _extract_readme_content(self, readme_path: Path) -> str:
        """Extract content from README file, limiting size."""
        try:
            # Limit README content to 2000 characters for analysis
            with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(2000)
                return content.strip()
        except Exception as e:
            logger.debug(f"Could not read README {readme_path}: {e}")
            return ""
    
    def classify_with_heuristics(self, scan_result: ProjectScanResult) -> ClassificationResult:
        """
        Classify project using rule-based heuristics.
        
        Args:
            scan_result: Result from directory scan
            
        Returns:
            ClassificationResult with heuristic classification
        """
        logger.info(f"Applying heuristic classification to {scan_result.path}")
        
        # Analyze key files for project type indicators
        project_types = defaultdict(int)
        language_scores = defaultdict(int)
        
        # Score based on key files
        for key_file in scan_result.key_files:
            if key_file.lower() in [k.lower() for k in self.KEY_FILES.keys()]:
                file_type = self.KEY_FILES.get(key_file.lower())
                if file_type:
                    project_types[file_type] += 3  # High weight for key files
        
        # Score based on file extensions
        for ext, count in scan_result.file_extensions.items():
            if ext in self.EXTENSION_MAPPING:
                lang_type = self.EXTENSION_MAPPING[ext]
                language_scores[lang_type] += count
        
        # Determine primary language/framework
        primary_language = max(language_scores, key=language_scores.get) if language_scores else None
        primary_project_type = max(project_types, key=project_types.get) if project_types else None
        
        # Classification logic
        category, confidence, reasoning = self._apply_classification_rules(
            scan_result, primary_language, primary_project_type, language_scores, project_types
        )
        
        # Generate suggested name
        suggested_name = self._generate_suggested_name(scan_result.path, category)
        
        return ClassificationResult(
            category=category,
            confidence=confidence,
            reasoning=reasoning,
            method="heuristic",
            suggested_name=suggested_name
        )
    
    def _apply_classification_rules(
        self, 
        scan_result: ProjectScanResult,
        primary_language: Optional[str],
        primary_project_type: Optional[str],
        language_scores: Dict[str, int],
        project_types: Dict[str, int]
    ) -> Tuple[str, float, str]:
        """Apply heuristic rules to determine project category."""
        
        # Web frontend detection
        if any(ext in scan_result.file_extensions for ext in ['.vue', '.jsx', '.tsx']):
            if '.vue' in scan_result.file_extensions:
                return "Web/Frontend", 0.9, "Vue.js project detected"
            elif any(ext in scan_result.file_extensions for ext in ['.jsx', '.tsx']):
                return "Web/Frontend", 0.9, "React project detected"
        
        # Node.js project detection
        if 'package.json' in [f.lower() for f in scan_result.key_files]:
            if any(ext in scan_result.file_extensions for ext in ['.vue', '.jsx', '.tsx']):
                return "Web/Frontend", 0.85, "Frontend JavaScript project with package.json"
            elif scan_result.readme_content and any(term in scan_result.readme_content.lower() for term in ['express', 'fastify', 'koa', 'api', 'server']):
                return "Web/Backend", 0.8, "Backend Node.js project"
            else:
                return "Web/FullStack", 0.7, "JavaScript project with package.json"
        
        # Python project detection
        if primary_project_type == 'python' or primary_language == 'python':
            if scan_result.readme_content:
                readme_lower = scan_result.readme_content.lower()
                if any(term in readme_lower for term in ['machine learning', 'ml', 'data science', 'pandas', 'numpy', 'tensorflow', 'pytorch']):
                    return "DataScience", 0.85, "Python data science/ML project"
                elif any(term in readme_lower for term in ['django', 'flask', 'fastapi', 'api', 'web']):
                    return "Web/Backend", 0.8, "Python web framework project"
            return "SystemUtilities/Python", 0.75, "Python utility project"
        
        # Rust project detection
        if primary_project_type == 'rust' or primary_language == 'rust':
            return "SystemUtilities/Rust", 0.85, "Rust project detected"
        
        # Go project detection
        if primary_project_type == 'go' or primary_language == 'go':
            return "SystemUtilities/Go", 0.85, "Go project detected"
        
        # Mobile development
        if primary_language == 'swift':
            return "Mobile/iOS", 0.8, "Swift iOS project"
        elif primary_language == 'dart':
            return "Mobile/CrossPlatform", 0.8, "Flutter/Dart project"
        
        # Game development
        if 'godot' in language_scores:
            return "Games/Godot", 0.85, "Godot game project"
        elif 'unity' in language_scores:
            return "Games/Unity", 0.85, "Unity game project"
        
        # Java project
        if primary_language == 'java':
            return "SystemUtilities/Java", 0.75, "Java project"
        
        # Static website
        if primary_language == 'web' and not primary_project_type:
            return "Web/Frontend", 0.6, "Static web project"
        
        # Fallback
        return "Misc", 0.3, f"Could not classify project clearly (primary: {primary_language or 'unknown'})"
    
    def _generate_suggested_name(self, project_path: str, category: str) -> str:
        """Generate a suggested clean name for the project."""
        # Get the directory name
        dir_name = Path(project_path).name
        
        # Clean up the name
        # Remove common prefixes/suffixes
        cleaned = dir_name.replace('-master', '').replace('_master', '')
        cleaned = cleaned.replace('-main', '').replace('_main', '')
        cleaned = cleaned.replace('-dev', '').replace('_dev', '')
        
        # Convert to a clean format
        # Replace separators with hyphens and convert to lowercase
        import re
        cleaned = re.sub(r'[_\s]+', '-', cleaned)
        cleaned = re.sub(r'[^a-zA-Z0-9\-]', '', cleaned)
        cleaned = cleaned.lower().strip('-')
        
        return cleaned if cleaned else "project"
    
    async def classify_with_ollama(
        self, 
        scan_result: ProjectScanResult, 
        model: str = "llama2",
        timeout: int = 30
    ) -> Optional[ClassificationResult]:
        """
        Classify project using Ollama AI model.
        
        Args:
            scan_result: Result from directory scan
            model: Ollama model to use
            timeout: Request timeout in seconds
            
        Returns:
            ClassificationResult from AI analysis, or None if failed
        """
        logger.info(f"Attempting AI classification with model: {model}")
        
        try:
            # Generate structured prompt
            prompt = self._generate_ollama_prompt(scan_result)
            
            # Make request to Ollama
            response = await self._call_ollama_api(prompt, model, timeout)
            
            if response:
                # Parse JSON response
                return self._parse_ollama_response(response)
            
        except Exception as e:
            logger.warning(f"Ollama classification failed: {e}")
        
        return None
    
    def _generate_ollama_prompt(self, scan_result: ProjectScanResult) -> str:
        """Generate structured prompt for Ollama analysis."""
        
        # Prepare file extensions summary
        ext_summary = ", ".join([f"{ext}({count})" for ext, count in 
                               sorted(scan_result.file_extensions.items(), 
                                     key=lambda x: x[1], reverse=True)[:10]])
        
        # Prepare key files summary
        key_files_summary = ", ".join(scan_result.key_files[:10])
        
        # Prepare README excerpt
        readme_excerpt = (scan_result.readme_content[:500] + "..." 
                         if scan_result.readme_content and len(scan_result.readme_content) > 500
                         else scan_result.readme_content or "No README found")
        
        prompt = f"""Analyze this software project and classify it into the most appropriate category.

Project Details:
- Path: {scan_result.path}
- Total Files: {scan_result.total_files}
- Key Files: {key_files_summary}
- File Extensions: {ext_summary}
- README Content: {readme_excerpt}

Valid Categories:
- Web/Frontend (React, Vue, Angular, static sites)
- Web/Backend (APIs, servers, backends)
- Web/FullStack (combined frontend/backend)
- Mobile/CrossPlatform (Flutter, React Native)
- Mobile/iOS (Swift, iOS apps)
- Mobile/Android (Java/Kotlin Android apps)
- SystemUtilities/Python (CLI tools, scripts)
- SystemUtilities/Rust (system tools, CLIs)
- SystemUtilities/Go (system utilities)
- SystemUtilities/Java (Java utilities)
- Games/Unity (Unity game projects)
- Games/Godot (Godot game projects)
- Libraries/Python (Python packages/libraries)
- Libraries/JavaScript (npm packages)
- Libraries/Rust (Rust crates)
- DataScience (ML, data analysis, Jupyter)
- Misc (other/unclear projects)

Respond with JSON only in this exact format:
{{
  "category": "exact category from above list",
  "confidence": 0.85,
  "reasoning": "brief explanation of classification decision",
  "suggested_name": "clean-project-name"
}}"""
        
        return prompt
    
    async def _call_ollama_api(self, prompt: str, model: str, timeout: int) -> Optional[str]:
        """Make async request to Ollama API."""
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,  # Low temperature for consistent classification
                "top_p": 0.9,
                "max_tokens": 500
            }
        }
        
        try:
            # Use asyncio to make non-blocking request
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(
                    f"{self.ollama_base_url}/api/generate",
                    json=payload,
                    timeout=timeout
                )
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                logger.warning(f"Ollama API returned status {response.status_code}")
                return None
                
        except Exception as e:
            logger.warning(f"Ollama API request failed: {e}")
            return None
    
    def _parse_ollama_response(self, response_text: str) -> Optional[ClassificationResult]:
        """Parse Ollama JSON response into ClassificationResult."""
        
        try:
            # Try to extract JSON from response
            response_text = response_text.strip()
            
            # Handle case where response might have extra text around JSON
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                data = json.loads(json_text)
                
                # Validate required fields
                required_fields = ['category', 'confidence', 'reasoning']
                if all(field in data for field in required_fields):
                    
                    # Validate confidence is a number between 0 and 1
                    confidence = float(data['confidence'])
                    if not 0.0 <= confidence <= 1.0:
                        confidence = max(0.0, min(1.0, confidence))
                    
                    return ClassificationResult(
                        category=data['category'],
                        confidence=confidence,
                        reasoning=data['reasoning'],
                        method="ollama",
                        suggested_name=data.get('suggested_name')
                    )
                else:
                    logger.warning(f"Ollama response missing required fields: {data}")
            
        except json.JSONDecodeError as e:
            logger.warning(f"Could not parse Ollama JSON response: {e}")
        except Exception as e:
            logger.warning(f"Error parsing Ollama response: {e}")
        
        return None
    
    async def analyze_project(
        self, 
        project_path: str, 
        use_ai: bool = True,
        ai_model: str = "llama2"
    ) -> ProjectAnalysis:
        """
        Complete project analysis combining scanning and classification.
        
        Args:
            project_path: Path to project directory
            use_ai: Whether to attempt AI classification
            ai_model: Ollama model to use for AI classification
            
        Returns:
            Complete ProjectAnalysis with all results
        """
        logger.info(f"Starting complete project analysis: {project_path}")
        
        # Step 1: Scan directory
        scan_result = self.scan_directory(project_path)
        
        # Step 2: Heuristic classification
        heuristic_classification = self.classify_with_heuristics(scan_result)
        
        # Step 3: AI classification (if enabled and available)
        ai_classification = None
        if use_ai:
            ai_classification = await self.classify_with_ollama(scan_result, ai_model)
        
        # Step 4: Determine final classification
        final_classification = self._determine_final_classification(
            heuristic_classification, ai_classification
        )
        
        # Step 5: Generate metadata
        metadata = {
            "analysis_timestamp": datetime.now().isoformat(),
            "analyzer_version": "1.0.0",
            "ai_model_used": ai_model if ai_classification else None,
            "confidence_threshold": 0.7
        }
        
        analysis = ProjectAnalysis(
            scan_result=scan_result,
            heuristic_classification=heuristic_classification,
            ai_classification=ai_classification,
            final_classification=final_classification,
            metadata=metadata
        )
        
        logger.info(f"Analysis complete: {final_classification.category} ({final_classification.confidence:.2f})")
        return analysis
    
    def _determine_final_classification(
        self, 
        heuristic: ClassificationResult, 
        ai: Optional[ClassificationResult]
    ) -> ClassificationResult:
        """Determine final classification from heuristic and AI results."""
        
        # If no AI classification, use heuristic
        if not ai:
            return heuristic
        
        # If AI confidence is high (>0.8), prefer AI
        if ai.confidence > 0.8:
            return ai
        
        # If heuristic confidence is much higher, prefer heuristic
        if heuristic.confidence > ai.confidence + 0.2:
            return heuristic
        
        # If AI confidence is reasonable (>0.6), prefer AI for its reasoning
        if ai.confidence > 0.6:
            return ai
        
        # Default to heuristic
        return heuristic