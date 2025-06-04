# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DevStewardAI is an AI-powered project organizer and bootstrapper built with:
- **Backend**: FastAPI (Python 3.9+) for core logic and Ollama integration
- **Desktop Shell**: Tauri (Rust) for native app wrapper and process management  
- **Frontend**: Vue.js 3 with Composition API, Tailwind CSS, and Catppuccin Mocha theme
- **AI Integration**: Local Ollama LLMs for project classification and organization

## Development Commands

### Environment Setup
```bash
# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install Python dependencies
cd src-py && pip install -r requirements.txt && pip install -r requirements-dev.txt

# Install frontend dependencies
cd src-ui && npm install

# Install Rust dependencies (Tauri)
cd src-tauri && cargo build
```

### Development Workflow
```bash
# Run Python backend (port 8008)
npm run dev:py

# Run Vue.js frontend development server
npm run dev:ui

# Run Tauri development environment (manages Python process)
npm run dev:tauri

# Run all tests
npm run test:py && npm run test:ui && npm run test:rust
```

### Quality Assurance
```bash
# Python formatting and linting
cd src-py && black . && flake8 .

# Rust formatting and linting
cd src-tauri && cargo fmt && cargo clippy

# Frontend linting
cd src-ui && npm run lint
```

## Architecture Overview

### Data Flow
```
Frontend (Vue) → Tauri (Rust) → Python FastAPI → Ollama
                    ↓
              File System Operations
```

### Key Components

**Python Backend (`src-py/`):**
- `main.py` - FastAPI app with all endpoints (health, models, scan, organize, create)
- `core/project_analyzer.py` - Directory scanning and AI-powered project classification
- `core/organizer.py` - Safe file organization with dry-run capabilities
- `core/bootstrapper.py` - Project creation from templates
- `templates/` - Basic project templates (Python utility, static website)

**Tauri Layer (`src-tauri/`):**
- `main.rs` - Python process lifecycle management and health checking
- `lib.rs` - Tauri commands that bridge frontend to Python API
- HTTP client for reliable communication with FastAPI backend

**Frontend (`src-ui/`):**
- `stores/appStore.js` - Reactive state management using Vue 3 Composition API
- `views/` - Main application views (Organizer, NewProject, Settings)
- `components/` - Reusable UI components (DirectoryTree, DryRunView, LoadingSpinner)

### Safety-First Philosophy

**File Operations:**
- All file modifications require explicit user confirmation after dry-run preview
- Atomic operations (copy then delete, never move directly)
- Comprehensive rollback capabilities on failure
- Operation manifest logging for audit trail

**AI Integration:**
- Structured prompts with JSON response validation
- Heuristic fallbacks when AI classification fails or has low confidence
- User can override any AI decision
- Confidence scoring displayed to users

## LLM Integration (Ollama)

### Classification Prompt Structure
The system uses structured prompts that request JSON responses with:
- `category` - Exact category from predefined schema
- `confidence` - Float between 0.0-1.0  
- `reasoning` - Brief explanation of decision
- `suggested_name` - Cleaned project name

### Organizational Schema
Projects are classified into:
- `Web/Frontend`, `Web/Backend`, `Web/FullStack`
- `Mobile/CrossPlatform` 
- `SystemUtilities/{language}` (Python, Rust, Go)
- `Games/{engine}` (Unity, Godot)
- `Libraries/{language}`
- `DataScience`
- `Misc` (fallback)

## Development Guidelines

### Code Standards
- **Python**: Use type hints, async/await, comprehensive error handling, Google-style docstrings
- **Rust**: Follow cargo fmt/clippy, use Result types, comprehensive error handling
- **Vue.js**: Composition API only, Catppuccin Mocha theme strictly enforced, scoped CSS

### Testing Priorities
1. File operation safety (most critical - prevents data loss)
2. LLM response parsing and error handling  
3. API endpoint reliability
4. Component integration and user workflows

### Error Handling Philosophy
- Never expose technical errors to users - always provide actionable, friendly messages
- Log technical details for debugging while showing user-friendly interface messages
- Implement graceful degradation (fallback to heuristics when AI fails)
- Never leave system in inconsistent state

## Project Templates

Current templates in `src-py/templates/`:
- `python_utility/` - Basic Python script with README and .gitignore
- `static_website/` - HTML/CSS/JS structure for static sites

Templates support placeholder replacement (e.g., `{{project_name}}`) and optional git initialization.

## Key Files to Understand

- `PLANNING.md` - Complete technical architecture and development roadmap
- `TASKS.md` - Detailed implementation tasks broken down by development phases  
- `AI_BEST_PRACTICES.md` - Guidelines for LLM integration, prompt engineering, and safety
- `complete_prompts.md` - Development prompts for each phase of implementation

When implementing new features, always prioritize safety (dry-run previews), user experience (loading states, error handling), and maintain the established architectural patterns.