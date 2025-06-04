# PROMPTS.md - Development Prompts for DevSteward AI

This document contains specific prompts for each development phase to guide AI-assisted development.

## Phase 0 Initial Setup Prompt

```
I am starting development of DevSteward AI, an AI-powered project organizer using FastAPI (Python), Tauri (Rust), and Vue.js 3. 

Please help me set up the initial project structure and basic configuration files for Phase 0. Based on the documentation in PLANNING.md and TASK.md, I need:

**Project Structure Setup:**
1. Create a comprehensive `.gitignore` file appropriate for Python, Rust, Node.js, and general development files
2. Create the complete directory structure as outlined in PLANNING.md
3. Create a professional README.md with:
   - Project overview and key features
   - Prerequisites (Python 3.9+, Rust, Node.js, Ollama)
   - Quick setup instructions
   - Development workflow
   - Architecture overview

**Python Backend Setup (`src-py/`):**
1. Create `requirements.txt` with core dependencies (FastAPI, uvicorn, requests, python-dotenv)
2. Create `requirements-dev.txt` with testing dependencies (pytest, httpx, pytest-asyncio)
3. Create a basic `main.py` with:
   - FastAPI app initialization
   - Basic health check endpoint (`GET /health`)
   - Structured logging configuration (to `devsteward_ai.log`)
   - CORS middleware for Tauri frontend
   - Basic error handling
4. Create `pytest.ini` or configure pytest in `pyproject.toml`
5. Create `.env.example` with configuration options

**Development Scripts:**
Create package.json in the root with development scripts for:
- `dev:ui` - Run Vue.js development server
- `dev:py` - Run FastAPI server with hot reload
- `dev:tauri` - Run Tauri development environment
- `test:py` - Run Python tests
- `test:ui` - Run frontend tests
- `test:rust` - Run Rust tests

Please create these files as artifacts, ensuring they follow best practices and are ready for immediate use. Focus on a clean, professional setup that will scale well as the project grows.
```

---

## Phase 1 Backend Development Prompt

```
I'm ready to start Phase 1 development of DevSteward AI's Python backend. Based on the completed Phase 0 setup and the specifications in PLANNING.md, please help me implement the core backend functionality.

**Context:**
- FastAPI server is set up with basic health check
- Need to implement AI-powered project analysis using Ollama
- Must prioritize safety with dry-run capabilities
- Should use structured logging and comprehensive error handling

**Please implement the following components:**

**1. FastAPI Main Application (`src-py/main.py`):**
- Add the remaining API endpoints:
  ```
  GET  /models              # List available Ollama models
  POST /scan                # Scan directory and analyze projects
  POST /organize/preview    # Generate organization dry-run plan
  POST /organize/execute    # Execute file organization
  POST /projects/create     # Create new project from template
  ```
- Include Pydantic models for all request/response bodies
- Add comprehensive error handling with appropriate HTTP status codes
- Implement request logging and timing

**2. Project Analyzer (`src-py/core/project_analyzer.py`):**
- `scan_directory(path)` - Recursively scan and identify project characteristics
- `classify_with_heuristics(project_data)` - Rule-based classification fallback
- `classify_with_ollama(project_data, model_name)` - AI-powered classification
- Use the structured prompt from PLANNING.md for consistent Ollama responses
- Implement confidence scoring and fallback logic

**3. File Organizer (`src-py/core/organizer.py`):**
- `generate_organization_plan(projects, target_root)` - Create dry-run plan
- `execute_organization(plan)` - Safely execute file moves with rollback capability
- Implement atomic operations (copy then delete, not move)
- Add operation logging and progress tracking

**4. Simple Bootstrapper (`src-py/core/bootstrapper.py`):**
- `create_project_from_template(name, template_type, target_path)`
- `initialize_git_repo(project_path)` - Optional git initialization
- Basic template file copying with placeholder replacement

**Requirements:**
- Use async/await throughout for better performance
- Include comprehensive error handling and logging
- Add type hints for all functions
- Create Pydantic models for data validation
- Follow the safety-first principle (never modify files without explicit confirmation)
- Include docstrings explaining each function's purpose and parameters

Please implement these components as separate artifacts, ensuring they integrate well together and follow FastAPI best practices. Focus on reliability, safety, and clear error messages.
```

---

## Phase 2 Tauri Integration Prompt

```
I'm ready to implement Phase 2 of DevSteward AI - the Tauri integration layer that bridges the Vue.js frontend with the Python FastAPI backend.

**Context:**
- Python FastAPI backend is complete with all core endpoints
- Need Tauri to manage the Python process lifecycle
- Must implement Tauri commands that call the Python API
- Error handling should be robust across the Rust/Python boundary

**Current Python API Endpoints to Bridge:**
- `GET /health` - Health check
- `GET /models` - List Ollama models  
- `POST /scan` - Scan and analyze directory
- `POST /organize/preview` - Generate dry-run plan
- `POST /organize/execute` - Execute organization
- `POST /projects/create` - Create new project

**Please implement:**

**1. Main Tauri Application (`src-tauri/src/main.rs`):**
- Python process management:
  - Start FastAPI server on port 8008 when Tauri app launches
  - Implement health checking with retry logic
  - Graceful shutdown of Python process on app exit
  - Error recovery if Python process crashes
- Configure Tauri app with proper permissions for file system and HTTP access
- Set up structured logging for Rust components

**2. Tauri Commands (`src-tauri/src/lib.rs`):**
Create Tauri commands for each Python API endpoint:
```rust
#[tauri::command]
async fn get_ollama_models() -> Result<ModelsResponse, String>

#[tauri::command]
async fn scan_directory(path: String) -> Result<ScanResponse, String>

#[tauri::command]
async fn preview_organization(scan_data: ScanData) -> Result<OrganizationPlan, String>

#[tauri::command]
async fn execute_organization(plan: OrganizationPlan) -> Result<ExecutionResult, String>

#[tauri::command]
async fn create_project(config: ProjectConfig) -> Result<ProjectResult, String>
```

**3. HTTP Client (`src-tauri/src/http_client.rs`):**
- Implement HTTP client using `reqwest`
- Add timeout handling and retry logic
- Convert Python API responses to Rust types
- Handle connection errors gracefully

**4. Update Cargo.toml:**
Add necessary dependencies:
```toml
[dependencies]
tauri = { version = "1.0", features = ["api-all"] }
reqwest = { version = "0.11", features = ["json"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
tokio = { version = "1", features = ["full"] }
```

**Requirements:**
- Use proper Rust error handling with `Result` types
- Include comprehensive logging for debugging
- Handle all edge cases (Python server not starting, network errors, etc.)
- Convert between Rust and Python data types safely
- Follow Rust best practices for async code
- Add appropriate timeouts for all HTTP requests

**Error Handling Priority:**
1. Python process management failures
2. HTTP communication errors  
3. Data serialization/deserialization errors
4. File system permission issues

Please create these as separate artifacts, ensuring they work together to provide a reliable bridge between the frontend and backend. Focus on robustness and clear error reporting.
```

---

## Phase 3 Frontend Development Prompt

```
I'm ready to implement Phase 3 of DevSteward AI - the Vue.js 3 frontend that provides an intuitive interface for project organization and creation.

**Context:**
- Tauri backend is complete with all bridge commands working
- Need a modern, responsive UI using Vue 3 Composition API
- Must strictly follow Catppuccin Mocha theme
- Should provide excellent UX with loading states and error handling

**Available Tauri Commands:**
- `get_ollama_models()` - Get available AI models
- `scan_directory(path)` - Scan and analyze projects
- `preview_organization(data)` - Generate dry-run plan
- `execute_organization(plan)` - Execute file moves
- `create_project(config)` - Create new project

**Please implement:**

**1. Global State Management (`src-ui/src/stores/appStore.js`):**
Using Vue 3 Composition API, create a reactive store with:
- Available Ollama models and selected model
- Current scan results and organization plan
- Loading states for all async operations
- Error handling state
- User preferences (theme, default directories)

**2. Core Components (`src-ui/src/components/`):**

**DirectoryTree.vue:**
- Hierarchical display of current project structure
- Visual indicators for project types and confidence levels
- Expandable/collapsible folders
- Catppuccin Mocha styling

**DryRunView.vue:**
- Side-by-side comparison of current vs. proposed structure
- Clear visual diff with move arrows
- Confidence indicators for AI classifications
- Ability to toggle individual moves on/off

**LoadingSpinner.vue:**
- Animated loading indicator matching Catppuccin theme
- Optional progress text display
- Various sizes (small, medium, large)

**ModelSelector.vue:**
- Dropdown for Ollama model selection
- Display model information (name, size if available)
- Handle case when no models are available

**3. Main Views (`src-ui/src/views/`):**

**OrganizerView.vue:**
- Directory selection with native file dialog
- "Scan Directory" button with progress indicator
- Display scan results with project classifications
- Dry-run preview with clear approve/reject interface
- Execute organization with progress tracking
- Success/error feedback

**NewProjectView.vue:**
- Form for project creation (name, type, location)
- Template selection with previews
- Target directory preview based on organizational schema
- Git initialization checkbox
- Real-time validation and error display

**SettingsView.vue:**
- Ollama model selection and status
- Default directory configuration
- Theme preferences (for future expansion)
- Access to application logs

**4. Main App Layout (`src-ui/src/App.vue`):**
- Sidebar navigation between main views
- Header with app title and status indicators
- Toast notifications for operations
- Global error boundary
- Strict Catppuccin Mocha theme application

**Design Requirements:**
- **Theme:** Strictly adhere to Catppuccin Mocha palette
- **Typography:** Clean, readable fonts with proper hierarchy
- **Spacing:** Consistent spacing using Tailwind classes
- **Interactions:** Smooth hover effects and transitions
- **Responsive:** Work well on various desktop screen sizes
- **Accessibility:** Proper ARIA labels and keyboard navigation

**UX Priorities:**
1. **Safety:** Always show what will happen before doing it
2. **Feedback:** Clear loading states and progress indicators  
3. **Error Handling:** User-friendly error messages with actions
4. **Performance:** Responsive interface even during long operations
5. **Intuitive:** Self-explanatory interface requiring minimal learning

**Catppuccin Mocha Colors to Use:**
- Background: `bg-base` (#1e1e2e)
- Surface: `bg-surface0` (#313244)  
- Text: `text-text` (#cdd6f4)
- Primary: `bg-blue` (#89b4fa)
- Success: `bg-green` (#a6e3a1)
- Warning: `bg-yellow` (#f9e2af)
- Error: `bg-red` (#f38ba8)

Please create these components as separate artifacts, ensuring they work together cohesively and provide an excellent user experience. Focus on the visual hierarchy, smooth interactions, and comprehensive error handling.
```

---

## General Development Guidelines

### Code Quality Standards

**Python Code Standards:**
- Use type hints for all function parameters and return values
- Follow PEP 8 style guidelines
- Add comprehensive docstrings using Google style
- Use async/await for I/O operations
- Implement proper error handling with custom exceptions when appropriate
- Add logging at INFO level for major operations, DEBUG for detailed tracing

**Rust Code Standards:**
- Use `cargo fmt` and `cargo clippy` for consistency
- Implement proper error handling with `Result<T, E>` types
- Use `thiserror` for custom error types
- Add comprehensive documentation comments (`///`)
- Follow Rust naming conventions (snake_case for functions/variables, PascalCase for types)
- Use `#[derive(Debug)]` for all custom types

**Vue.js Code Standards:**
- Use Composition API consistently (avoid Options API)
- Implement proper TypeScript typing when possible
- Follow Vue 3 best practices for reactivity
- Use scoped CSS with proper class naming
- Implement proper component props validation
- Add comprehensive component documentation

### Testing Guidelines

**Unit Testing Priorities:**
1. File operation safety (most critical)
2. LLM response parsing and error handling
3. Data validation and type conversion
4. Business logic correctness

**Integration Testing Focus:**
1. API endpoint functionality
2. Tauri command execution
3. Component interactions
4. Error boundary behavior

**Test Data Requirements:**
- Create mock project structures for testing
- Include edge cases (empty directories, special characters, very large projects)
- Test with various LLM response formats
- Include network failure scenarios

### Error Handling Philosophy

**User-Facing Errors:**
- Always provide actionable error messages
- Never expose technical stack traces to users
- Include suggested solutions when possible
- Log technical details for debugging while showing friendly messages

**System Errors:**
- Log all errors with context (timestamp, operation, user action)
- Implement graceful degradation (fallback to heuristics when LLM fails)
- Provide recovery options when possible
- Never leave the system in an inconsistent state

### Performance Considerations

**Backend Performance:**
- Use async/await for all I/O operations
- Implement connection pooling for database operations (if added later)
- Cache LLM responses for identical project structures
- Use streaming responses for large directory scans

**Frontend Performance:**
- Implement virtual scrolling for large directory trees
- Use Vue 3's `<Suspense>` for loading states
- Optimize component re-renders with proper key usage
- Implement debouncing for user input

### Security Guidelines

**File System Security:**
- Validate all file paths to prevent directory traversal
- Never execute user-provided commands without explicit confirmation
- Implement proper permission checking before file operations
- Sanitize all user inputs used in file paths

**Network Security:**
- Validate all data from Ollama API responses
- Implement timeouts for all network requests
- Use HTTPS for any external API calls (future feature)
- Sanitize any user data sent to LLM

---

## Debugging and Troubleshooting Prompts

### Common Issues Debugging Prompt

```
I'm encountering issues with DevSteward AI. Here's the context:

**Issue Description:**
[Describe the specific problem you're experiencing]

**Component Affected:**
- [ ] Python FastAPI backend
- [ ] Tauri Rust layer
- [ ] Vue.js frontend
- [ ] Ollama integration
- [ ] File operations

**Error Messages/Logs:**
[Paste any relevant error messages or log entries]

**Steps to Reproduce:**
1. [List the steps that lead to the issue]

**Expected vs Actual Behavior:**
- Expected: [What should happen]
- Actual: [What actually happens]

**Environment:**
- OS: [Windows/macOS/Linux]
- Python version: [version]
- Rust version: [version]
- Node.js version: [version]
- Ollama version: [version]

Please help me:
1. Identify the root cause of this issue
2. Provide a step-by-step solution
3. Suggest preventive measures to avoid similar issues
4. Add appropriate error handling if missing

Focus on the most likely causes first and provide debugging steps I can follow.
```

### Performance Optimization Prompt

```
I need to optimize the performance of DevSteward AI. Current performance issues:

**Performance Metrics:**
- Directory scan time: [X seconds for Y files]
- LLM classification time: [X seconds per project]
- UI responsiveness: [Description of lag/delays]
- Memory usage: [High/Normal/Low]

**Specific Areas for Optimization:**
- [ ] Directory scanning speed
- [ ] LLM API response times
- [ ] Frontend rendering performance
- [ ] File operation efficiency
- [ ] Memory usage optimization

**Current Bottlenecks:**
[Describe where you see the biggest performance issues]

Please provide:
1. Profiling suggestions to identify bottlenecks
2. Specific optimization strategies for each component
3. Code improvements with before/after examples
4. Performance monitoring recommendations
5. Benchmarking approaches to measure improvements

Focus on optimizations that provide the biggest impact with minimal complexity changes.
```

### Feature Enhancement Prompt

```
I want to add a new feature to DevSteward AI:

**Feature Description:**
[Detailed description of the new feature]

**User Story:**
As a [user type], I want to [action] so that [benefit/outcome].

**Current System Integration:**
- How it fits into existing architecture
- Which components need modification
- New components that need creation

**Requirements:**
- [ ] Backend API changes needed
- [ ] Database schema changes (if applicable)
- [ ] Frontend UI changes needed
- [ ] New Tauri commands required
- [ ] Additional testing requirements

**Design Considerations:**
- Performance impact
- Security implications
- User experience changes
- Backward compatibility needs

Please provide:
1. Detailed implementation plan with phases
2. Code examples for key components
3. API design (if backend changes needed)
4. UI mockups or component structure (if frontend changes needed)
5. Testing strategy for the new feature
6. Migration plan (if data changes needed)

Ensure the feature integrates seamlessly with the existing codebase and follows established patterns.
```

---

## AI Prompt Engineering for LLM Integration

### Ollama Prompt Templates

**Project Classification Prompt:**
```python
CLASSIFICATION_PROMPT = """
You are a project classification expert. Analyze the following project data and classify it according to our organizational schema.

PROJECT DATA:
Files: {file_summary}
Key Files Found: {key_files}
README Content: {readme_excerpt}
Directory Size: {file_count} files

CLASSIFICATION SCHEMA:
1. Web/Frontend - React, Vue, Angular, static sites, CSS frameworks
2. Web/Backend - APIs, servers, Node.js backends, Python web apps
3. Web/FullStack - Combined frontend/backend projects
4. Mobile/CrossPlatform - React Native, Flutter, Ionic
5. SystemUtilities/Python - CLI tools, scripts, automation
6. SystemUtilities/Rust - System tools, performance utilities
7. SystemUtilities/Go - Network tools, concurrent utilities
8. Games/Unity - Unity game projects
9. Games/Godot - Godot game projects
10. Libraries/Python - Reusable Python packages
11. Libraries/JavaScript - NPM packages, utility libraries
12. DataScience - Jupyter notebooks, ML projects, data analysis
13. Misc - Uncategorized or unclear projects

RESPONSE FORMAT (JSON only):
{
  "category": "exact category from schema above",
  "confidence": 0.85,
  "reasoning": "Brief explanation of classification decision",
  "suggested_name": "cleaned project name",
  "key_indicators": ["list", "of", "decisive", "factors"]
}

Ensure confidence is between 0.0 and 1.0. Use confidence < 0.7 for uncertain classifications.
"""
```

**Project Naming Prompt:**
```python
NAMING_PROMPT = """
You are a project naming expert. Given a project's characteristics, suggest a clean, descriptive name.

PROJECT INFO:
Current Name: {current_name}
Category: {category}
Description: {description}
Key Technologies: {technologies}

NAMING RULES:
- Use PascalCase for consistency
- Be descriptive but concise (2-4 words max)
- Avoid generic names like "Project1" or "Test"
- Include key technology if it's the main focus
- Remove version numbers, dates, or personal prefixes

RESPONSE FORMAT (JSON only):
{
  "suggested_name": "CleanProjectName",
  "reasoning": "Why this name is better",
  "alternatives": ["Alternative1", "Alternative2"]
}
"""
```

---

## Testing and Quality Assurance Prompts

### Comprehensive Testing Prompt

```
I need to implement comprehensive testing for DevSteward AI. Based on the current codebase:

**Testing Requirements:**
1. **Unit Tests:** Test individual functions and components
2. **Integration Tests:** Test component interactions
3. **End-to-End Tests:** Test complete user workflows
4. **Safety Tests:** Ensure file operations are safe
5. **Performance Tests:** Verify acceptable response times

**Components to Test:**
- Python FastAPI backend (all endpoints)
- Tauri commands and process management
- Vue.js components and user interactions
- LLM integration and error handling
- File operations (most critical)

**Test Scenarios to Cover:**
- Happy path: Normal operation flows
- Error conditions: Network failures, invalid inputs
- Edge cases: Empty directories, large projects, special characters
- Security: Path traversal attempts, malicious inputs
- Performance: Large directory scans, multiple concurrent operations

**Please provide:**
1. Complete test structure and organization
2. Mock data and fixtures for testing
3. Test utilities for common operations
4. CI/CD pipeline configuration for automated testing
5. Test coverage reporting setup
6. Performance benchmarking tests

**Priority Areas:**
1. File operation safety (highest priority)
2. API endpoint reliability
3. Error handling completeness
4. User interface functionality
5. Performance under load

Focus on tests that prevent data loss and ensure system reliability.
```

This completes your PROMPTS.md file with comprehensive development guidance for all phases of your DevSteward AI project. The prompts are designed to be specific enough to get quality AI assistance while being flexible enough to adapt as your project evolves.