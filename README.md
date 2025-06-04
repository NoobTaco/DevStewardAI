# DevSteward AI

**An AI-powered project organizer and bootstrapper for developers**

DevSteward AI helps you automatically organize your development projects using local AI models and provides intelligent project creation tools. It combines the power of Ollama for local AI processing with a clean, modern interface built with Tauri, Vue.js, and FastAPI.

## ✨ Key Features

- **🤖 AI-Powered Organization**: Uses local Ollama models to intelligently classify and organize your projects
- **🔒 Privacy-First**: All AI processing happens locally - no data leaves your machine
- **🛡️ Safety-First**: Dry-run previews and atomic file operations ensure your data is never lost
- **⚡ Modern Stack**: FastAPI backend, Tauri desktop app, Vue.js 3 frontend with Catppuccin theming
- **📁 Smart Classification**: Automatically categorizes projects into logical directory structures
- **🚀 Project Bootstrapping**: Create new projects from intelligent templates
- **🎯 Heuristic Fallbacks**: Works even when AI models are unavailable

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+** with pip
- **Rust** (latest stable) with Cargo
- **Node.js 18+** with npm
- **Ollama** ([Install from ollama.ai](https://ollama.ai))

### Ollama Setup

1. Install Ollama following the instructions at [ollama.ai](https://ollama.ai)
2. Pull a recommended model:
   ```bash
   ollama pull llama2
   # or
   ollama pull codellama
   ```
3. Verify installation:
   ```bash
   ollama list
   ```

## 🚀 Quick Setup

### 1. Clone and Enter Directory
```bash
git clone <repository-url>
cd DevStewardAI
```

### 2. Set Up Python Backend
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
cd src-py
pip install -r requirements.txt
pip install -r requirements-dev.txt
cd ..
```

### 3. Set Up Frontend
```bash
cd src-ui
npm install
cd ..
```

### 4. Set Up Tauri
```bash
cd src-tauri
cargo build
cd ..
```

### 5. Configure Environment
```bash
cp src-py/.env.example src-py/.env
# Edit .env with your preferred settings
```

## 🛠️ Development Workflow

DevSteward AI provides convenient npm scripts for development:

### Start Development Servers

```bash
# Run Python FastAPI backend (port 8008)
npm run dev:py

# Run Vue.js frontend development server
npm run dev:ui

# Run Tauri development environment (recommended)
npm run dev:tauri
```

### Run Tests

```bash
# Run all tests
npm run test:py && npm run test:ui && npm run test:rust

# Run individual test suites
npm run test:py    # Python backend tests
npm run test:ui    # Vue.js frontend tests  
npm run test:rust  # Rust/Tauri tests
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

## 🏗️ Architecture Overview

DevSteward AI follows a three-tier architecture designed for safety, performance, and maintainability:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vue.js 3 UI   │ -> │  Tauri (Rust)   │ -> │ FastAPI (Python)│ -> │ Ollama (Local)  │
│  (Frontend)     │    │ (Desktop Shell) │    │   (Core Logic)  │    │  (AI Models)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
                                 │
                                 v
                        ┌─────────────────┐
                        │  File System    │
                        │   Operations    │
                        └─────────────────┘
```

### Core Components

- **Frontend (`src-ui/`)**: Vue.js 3 with Composition API, Tailwind CSS, and Catppuccin Mocha theme
- **Desktop Shell (`src-tauri/`)**: Rust-based Tauri app for native OS integration and Python process management
- **Backend (`src-py/`)**: FastAPI-powered core logic with project analysis, organization, and AI integration
- **AI Integration**: Local Ollama models for intelligent project classification

### Data Flow

1. **User Interaction**: User selects directories or creates projects through Vue.js interface
2. **Command Bridge**: Tauri translates UI actions into HTTP requests to Python backend
3. **Analysis**: FastAPI backend scans projects and optionally consults Ollama for classification
4. **Safety Preview**: Dry-run results shown to user for confirmation
5. **Execution**: Atomic file operations performed with comprehensive logging and rollback capability

## 📁 Project Structure

```
DevStewardAI/
├── src-tauri/                  # Tauri Rust application
│   ├── src/
│   │   ├── main.rs             # Python process management
│   │   └── lib.rs              # Tauri commands and HTTP client
│   ├── Cargo.toml
│   └── tauri.conf.json
├── src-ui/                     # Vue.js frontend
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── components/         # Reusable UI components
│   │   ├── views/              # Main application views
│   │   └── stores/             # Reactive state management
│   ├── package.json
│   └── tailwind.config.js      # Catppuccin Mocha theme
├── src-py/                     # Python FastAPI backend
│   ├── main.py                 # FastAPI app with all routes
│   ├── core/                   # Core business logic
│   ├── templates/              # Project templates
│   ├── tests/                  # Test suite
│   ├── requirements.txt        # Production dependencies
│   └── requirements-dev.txt    # Development dependencies
├── docs/                       # Documentation
├── .gitignore
└── README.md
```

## 🔧 Configuration

### Environment Variables (`.env`)

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama2

# Logging
LOG_LEVEL=INFO
LOG_FILE=devsteward_ai.log

# Development
DEBUG=false
```

### Ollama Model Selection

DevSteward AI works with any Ollama model, but performs best with:

- **llama2** (7B/13B) - Good balance of speed and accuracy
- **codellama** (7B/13B) - Specialized for code understanding
- **mistral** (7B) - Fast and efficient for classification tasks

## 🛡️ Safety Features

- **Dry-Run Previews**: See exactly what changes will be made before execution
- **Atomic Operations**: Files are copied before deletion, ensuring no data loss
- **Rollback Capability**: All operations can be undone if something goes wrong
- **Operation Logging**: Comprehensive audit trail of all file operations
- **Heuristic Fallbacks**: Works reliably even when AI models fail

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes following the existing code style
4. Run tests: `npm run test:py && npm run test:ui && npm run test:rust`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues:

1. Check that Ollama is running: `ollama list`
2. Verify all dependencies are installed correctly
3. Check the application logs: `devsteward_ai.log`
4. Consult the troubleshooting guide in `docs/`

## 🔗 Links

- [Ollama](https://ollama.ai) - Local AI model server
- [Tauri](https://tauri.app) - Desktop app framework
- [FastAPI](https://fastapi.tiangolo.com) - Python web framework
- [Vue.js](https://vuejs.org) - Frontend framework
- [Catppuccin](https://catppuccin.com) - Color theme