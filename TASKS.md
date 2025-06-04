# TASK.MD - Development Tasks for DevSteward AI (Streamlined)

This document outlines the streamlined development approach focusing on MVP delivery.

## Phase 0: Project Setup & Foundation

### Project Structure
- [ ] Initialize main repository with proper `.gitignore`
- [ ] Create directory structure as outlined in `PLANNING.md`
- [ ] Set up `README.md` with project overview and setup instructions

### Python Backend Setup (`src-py/`)
- [ ] Create Python virtual environment
- [ ] Create `requirements.txt` with core dependencies:
  ```
  fastapi>=0.104.0
  uvicorn[standard]>=0.24.0
  requests>=2.31.0
  python-dotenv>=1.0.0
  ```
- [ ] Create `requirements-dev.txt`:
  ```
  pytest>=7.4.0
  httpx>=0.25.0
  pytest-asyncio>=0.21.0
  ```
- [ ] Set up basic FastAPI app in `main.py` with health check
- [ ] Configure structured logging to `devsteward_ai.log`
- [ ] Create basic `pytest` configuration

### Tauri Setup (`src-tauri/`)
- [ ] Initialize Tauri project: `cargo tauri init`
- [ ] Configure `tauri.conf.json`:
  - Set window title to "DevSteward AI"
  - Configure permissions for file system access and HTTP requests
  - Set appropriate window dimensions and constraints
- [ ] Add required dependencies to `Cargo.toml`:
  ```toml
  [dependencies]
  tauri = { version = "1.0", features = ["api-all"] }
  reqwest = { version = "0.11", features = ["json"] }
  serde = { version = "1.0", features = ["derive"] }
  serde_json = "1.0"
  tokio = { version = "1", features = ["full"] }
  ```

### Frontend Setup (`src-ui/`)
- [ ] Initialize Vue 3 project with Vite: `npm create vue@latest src-ui`
- [ ] Install and configure Tailwind CSS:
  ```bash
  npm install -D tailwindcss postcss autoprefixer
  npx tailwindcss init -p
  ```
- [ ] Configure Catppuccin Mocha theme in `tailwind.config.js`
- [ ] Install additional dependencies:
  ```bash
  npm install @vueuse/core lucide-vue-next
  npm install -D vitest @vue/test-utils
  ```
- [ ] Set up basic `App.vue` with Catppuccin theming
- [ ] Configure Vitest for testing

### Development Scripts
- [ ] Add development scripts to root `package.json`:
  ```json
  {
    "scripts": {
      "dev:ui": "cd src-ui && npm run dev",
      "dev:py": "cd src-py && uvicorn main:app --reload --port 8008",
      "dev:tauri": "cd src-tauri && cargo tauri dev",
      "test:py": "cd src-py && pytest",
      "test:ui": "cd src-ui && npm run test",
      "test:rust": "cd src-tauri && cargo test"
    }
  }
```

## Phase 1: Core Backend Development (Python)

### API Structure (`src-py/main.py`)
- [ ] Implement core FastAPI endpoints:
  ```python
  GET  /health              # Health check
  GET  /models              # List Ollama models
  POST /scan                # Scan directory + analyze
  POST /organize/preview    # Generate dry-run plan
  POST /organize/execute    # Execute organization
  POST /projects/create     # Create new project
  ```
- [ ] Add comprehensive error handling and logging
- [ ] Implement request/response models with Pydantic
- [ ] Add CORS middleware for Tauri frontend

### Project Analysis (`src-py/core/project_analyzer.py`)
- [ ] Implement `scan_directory()`:
  - Recursive directory traversal
  - File extension analysis
  - Key file detection (package.json, Cargo.toml, etc.)
  - README content extraction
- [ ] Implement `classify_with_heuristics()`:
  - Rule-based classification for common patterns
  - Confidence scoring
- [ ] Implement `classify_with_ollama()`:
  - Structured prompt creation
  - Ollama API integration (`POST /api/generate`)
  - JSON response parsing with error handling
  - Fallback to heuristics on failure
- [ ] **Testing:** Unit tests with mock file systems and Ollama responses

### File Organization (`src-py/core/organizer.py`)
- [ ] Implement `generate_organization_plan()`:
  - Map classifications to target directory structure
  - Handle naming conflicts
  - Generate move operations list
- [ ] Implement `execute_organization()`:
  - Atomic file operations (copy then delete)
  - Operation logging and rollback capability
  - Progress tracking
- [ ] **Testing:** Unit tests with temporary directories

### Simple Project Creation (`src-py/core/bootstrapper.py`)
- [ ] Implement `create_project_from_template()`:
  - Template file copying
  - Basic placeholder replacement
  - Directory structure creation
- [ ] Implement `initialize_git_repo()`:
  - Optional git initialization
  - .gitignore copying
- [ ] **Testing:** Unit tests with temporary directories

### Project Templates (`src-py/templates/`)
- [ ] Create `python_utility/` template:
  ```
  {{project_name}}/
  ├── {{project_name}}.py
  ├── README.md
  └── .gitignore
  ```
- [ ] Create `static_website/` template:
  ```
  {{project_name}}/
  ├── index.html
  ├── css/style.css
  ├── js/script.js
  └── README.md
  ```

### Utilities (`src-py/core/utils.py`)
- [ ] Implement Ollama connection checking
- [ ] Implement safe file operation helpers
- [ ] Implement logging configuration
- [ ] **Testing:** Unit tests for utility functions

## Phase 2: Tauri Integration (Rust)

### Python Process Management (`src-tauri/src/main.rs`)
- [ ] Implement Python server lifecycle management:
  - Start FastAPI server on app launch
  - Health check with retry logic  
  - Graceful shutdown on app exit
- [ ] Handle Python process errors and recovery
- [ ] **Testing:** Integration tests for process management

### Tauri Commands (`src-tauri/src/lib.rs`)
- [ ] Implement Tauri commands for each API endpoint:
  ```rust
  #[tauri::command]
  async fn get_ollama_models() -> Result<Vec<Model>, String>
  
  #[tauri::command] 
  async fn scan_directory(path: String) -> Result<ScanResult, String>
  
  #[tauri::command]
  async fn preview_organization(scan_id: String) -> Result<OrganizationPlan, String>
  
  #[tauri::command]
  async fn execute_organization(plan: OrganizationPlan) -> Result<ExecutionResult, String>
  
  #[tauri::command]
  async fn create_project(config: ProjectConfig) -> Result<ProjectResult, String>
  ```
- [ ] Implement HTTP client for Python API calls
- [ ] Add comprehensive error handling and type conversion
- [ ] **Testing:** Unit tests for command logic

## Phase 3: Frontend Development (Vue.js)

### Global State (`src-ui/src/stores/appStore.js`)
- [ ] Implement reactive store using Vue 3 Composition API:
  ```javascript
  export const useAppStore = () => {
    const models = ref([])
    const currentScan = ref(null)
    const organizationPlan = ref(null)
    const loading = ref(false)
    // ... state and actions
  }
  ```

### Core Components (`src-ui/src/components/`)
- [ ] `DirectoryTree.vue` - File tree visualization
- [ ] `DryRunView.vue` - Organization plan comparison
- [ ] `LoadingSpinner.vue` - Loading states
- [ ] `ModelSelector.vue` - Ollama model selection
- [ ] `ConfidenceIndicator.vue` - AI confidence display

### Main Views (`src-ui/src/views/`)
- [ ] `OrganizerView.vue`:
  - Directory selection dialog
  - Scan initiation and progress
  - Dry-run results display
  - Organization execution
- [ ] `NewProjectView.vue`:
  - Project creation form
  - Template selection
  - Target directory preview
- [ ] `SettingsView.vue`:
  - Ollama model selection
  - Application preferences
  - Log file access

### Navigation (`src-ui/src/App.vue`)
- [ ] Implement sidebar navigation
- [ ] Apply Catppuccin Mocha theme globally
- [ ] Add loading states and error boundaries

### **Testing Strategy for Phase 3:**
- [ ] Component unit tests with Vue Test Utils
- [ ] Mock Tauri `invoke` calls in tests
- [ ] Visual regression tests for theming

## Phase 4: Integration & Polish

### End-to-End Testing
- [ ] Set up Playwright or Cypress
- [ ] Write E2E tests for main workflows:
  - Complete organization process
  - Project creation workflow
  - Error handling scenarios

### Error Handling & UX Polish
- [ ] Comprehensive error boundaries in Vue components
- [ ] User-friendly error messages throughout
- [ ] Loading states for all async operations
- [ ] Responsive design verification

### Documentation
- [ ] Complete `README.md` with setup instructions
- [ ] Create `QUICK_START.md` for new users
- [ ] Document API endpoints in `API.md`
- [ ] Create troubleshooting guide

### Performance & Safety
- [ ] Profile directory scanning performance
- [ ] Test file operation safety with large projects
- [ ] Verify rollback functionality
- [ ] Load testing with various project sizes

## Success Criteria by Phase

**Phase 0 Complete:**
- All development tools configured
- Basic "Hello World" in each component
- Development scripts working

**Phase 1 Complete:**
- Python API fully functional with tests
- Ollama integration working
- File operations safe and tested

**Phase 2 Complete:**
- Tauri app launches Python backend
- All API calls work through Tauri commands
- Error handling implemented

**Phase 3 Complete:**
- Complete UI for all main features
- Catppuccin theme properly applied
- User can complete full workflows

**Phase 4 Complete:**
- All tests passing
- Documentation complete
- Ready for user testing

## Next Steps After MVP

- User feedback collection
- Performance optimization
- Additional project templates  
- Advanced organizational schemas
- CI/CD pipeline setup