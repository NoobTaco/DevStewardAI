# PLANNING.MD - AI-Powered Project Organizer & Bootstrapper

**Version:** 2.0 (Streamlined)
**Date:** June 3, 2025
**Status:** Ready for Development

## I. Core Philosophy & Guiding Principles

- **Safety First:** No destructive file operations without dry-run preview and explicit user confirmation
- **MVP Focus:** Start simple, iterate based on user feedback
- **User Experience:** Intuitive, modern interface with Catppuccin Mocha theme
- **Privacy:** All AI processing happens locally via Ollama
- **Reliability:** Heuristic fallbacks when AI fails, atomic file operations
- **Modularity:** Clear separation between Python backend, Tauri bridge, and UI

## II. Technical Stack (Simplified)

1. **Core Logic Backend (Python):**
   - **Language:** Python 3.9+
   - **Framework:** FastAPI
   - **Key Libraries:** `fastapi`, `uvicorn`, `requests`, `pathlib`, `shutil`
   - **Testing:** `pytest`, `httpx`

2. **Desktop Shell (Tauri):**
   - **Language:** Rust
   - **Key Crates:** `tauri`, `reqwest`, `serde_json`
   - **Testing:** `cargo test`

3. **User Interface:**
   - **Framework:** Vue.js 3 (Composition API)
   - **Styling:** Tailwind CSS + Catppuccin Mocha
   - **Build Tool:** Vite
   - **Testing:** Vitest

4. **AI Integration:**
   - **LLM Server:** Ollama (local)
   - **Model:** User-selected from available models

## III. Application Architecture

### A. Simplified Architecture Flow

```
Frontend (Vue) → Tauri (Rust) → Python FastAPI → Ollama
                    ↓
              File System Operations
```

### B. Streamlined File Structure

```
DevStewardAI/
├── src-tauri/                  # Tauri Rust application
│   ├── src/
│   │   ├── main.rs             # Main Tauri app, Python process management
│   │   └── lib.rs              # Tauri commands and HTTP client
│   ├── Cargo.toml
│   └── tauri.conf.json
├── src-ui/                     # Vue.js frontend
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── components/         # Reusable UI components
│   │   │   ├── DirectoryTree.vue
│   │   │   ├── DryRunView.vue
│   │   │   └── LoadingSpinner.vue
│   │   ├── views/              # Main application views
│   │   │   ├── OrganizerView.vue
│   │   │   ├── NewProjectView.vue
│   │   │   └── SettingsView.vue
│   │   └── stores/             # Simple reactive stores
│   │       └── appStore.js
│   ├── package.json
│   ├── tailwind.config.js      # Catppuccin Mocha configured
│   └── vite.config.js
├── src-py/                     # Python FastAPI backend
│   ├── main.py                 # FastAPI app with all routes
│   ├── core/
│   │   ├── project_analyzer.py # Combined scanning + LLM analysis
│   │   ├── organizer.py        # File organization logic
│   │   ├── bootstrapper.py     # Simple project creation
│   │   └── utils.py            # Shared utilities
│   ├── templates/              # Basic project templates
│   │   ├── python_utility/
│   │   └── static_website/
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── docs/
│   ├── PLANNING.md             # This file
│   ├── TASK.md                 # Development tasks
│   ├── QUICK_START.md          # 5-minute setup guide
│   ├── PROMPTS.md              # Development prompts
│   └── AI_BEST_PRACTICES.md    # AI integration guidelines
├── .gitignore
└── README.md
```

## IV. Core Features (MVP)

### A. Project Organization (Simplified)

1. **Directory Scanning:**
   - Recursive scan with basic heuristics
   - Collect file extensions, key files (package.json, Cargo.toml, etc.)
   - Extract README content (first 1000 chars)

2. **AI Classification:**
   - Send structured data to user-selected Ollama model
   - Parse JSON response with category, confidence, reasoning
   - Fallback to heuristics if AI fails or low confidence

3. **Dry Run Preview:**
   - Show current vs. proposed structure
   - Clear visual diff with confidence scores
   - User confirmation required

4. **Safe Execution:**
   - Atomic operations (copy then delete)
   - Create operation manifest
   - Rollback capability on failure

### B. Simple Project Creation

1. **Basic Templates:**
   - Python utility script
   - Static website
   - Simple form-based creation

2. **Minimal Bootstrapping:**
   - Create directory structure
   - Copy template files
   - Optional git initialization

## V. Organizational Schema (Simplified)

```
<UserRoot>/
├── Personal/
│   ├── Web/
│   │   ├── Frontend/          # React, Vue, Angular
│   │   ├── Backend/           # APIs, servers
│   │   └── FullStack/         # Combined projects
│   ├── Mobile/
│   │   └── CrossPlatform/     # React Native, Flutter
│   ├── Games/
│   │   └── <Engine>/          # Unity, Godot, etc.
│   ├── SystemUtilities/
│   │   └── <Language>/        # Python, Rust, Go
│   ├── Libraries/
│   │   └── <Language>/        # Reusable code
│   ├── DataScience/           # ML, analysis
│   └── Misc/                  # Uncategorized
├── Work/
│   └── <Client>/
└── Learning/
    └── <Technology>/
```

## VI. AI Integration Strategy

### A. Structured Prompts

```python
CLASSIFICATION_PROMPT = """
Analyze this project and classify it:

Files: {file_summary}
README: {readme_excerpt}

Valid categories:
- Web/Frontend, Web/Backend, Web/FullStack
- Mobile/CrossPlatform
- SystemUtilities/{language}
- Games/{engine}
- Libraries/{language}
- DataScience
- Misc

Respond with JSON only:
{
  "category": "exact category",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation"
}
"""
```

### B. Reliability Measures

- Confidence thresholds (>0.7 for auto-classification)
- Heuristic fallbacks for common patterns
- User override for all classifications
- Structured JSON parsing with error handling

## VII. Development Phases

### Phase 0: Project Setup
- Initialize all project structures
- Configure build tools and dependencies
- Set up basic FastAPI server
- Create Vue.js app with Tailwind/Catppuccin

### Phase 1: Core Backend (MVP)
- Project scanning and heuristic classification
- Basic Ollama integration
- File organization with dry-run
- Simple API endpoints

### Phase 2: Tauri Integration
- Python process management
- API bridging between frontend and backend
- Error handling and logging

### Phase 3: Frontend Development
- Directory tree visualization
- Dry-run comparison views
- Basic project creation forms
- Settings and model selection

### Phase 4: Testing & Polish
- Comprehensive testing strategy
- Error handling refinement
- Performance optimization
- Documentation completion

## VIII. Risk Mitigation

### A. File Operation Safety
- Never modify files without user confirmation
- Atomic operations with rollback capability
- Comprehensive logging of all operations
- Backup creation before major changes

### B. AI Reliability
- Always provide heuristic fallback
- Clear confidence indicators to users
- Graceful handling of Ollama connection failures
- User can override any AI decision

### C. User Experience
- Clear progress indicators for long operations
- Intuitive error messages
- Responsive design for various screen sizes
- Consistent theming throughout

## IX. Success Metrics

- **Safety:** Zero accidental file losses
- **Accuracy:** >80% user acceptance of AI classifications
- **Performance:** <5 seconds for typical directory scans
- **Usability:** New users can organize projects within 10 minutes

This streamlined approach focuses on delivering core value quickly while maintaining the safety and user experience principles that make DevSteward AI unique.