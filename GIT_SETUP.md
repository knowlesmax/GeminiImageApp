# Git Setup Guide for Gemini Image App

## 📋 Quick Start

### 1. Initial Setup (Already Done)
```bash
git init
git add .
git commit -m "Initial commit: Gemini Image App with complete features"
```

### 2. Connect to Remote Repository (Optional)
```bash
# Add your remote repository
git remote add origin https://github.com/yourusername/gemini-image-app.git

# Push to remote
git push -u origin main
```

## 🔍 What's Being Tracked

### ✅ Tracked Files
- All source code (`backend/`, `frontend/src/`)
- Configuration files (`package.json`, `requirements.txt`, `vite.config.js`)
- Documentation (`README.md`, `doc.md`)
- Environment template (`.env.example`)
- AI model files (`storage/models/*.pt`) - **~500MB total**
- Directory structure (`.gitkeep` files)

### ❌ Ignored Files
- Environment variables (`.env`)
- Dependencies (`node_modules/`, `.venv/`)
- Generated files (`storage/generated/*`)
- Uploaded files (`storage/uploads/*`)
- IDE settings (`.vscode/`, `.idea/`)
- OS files (`.DS_Store`, `Thumbs.db`)
- Cache and temporary files

## 🎯 AI Model Files Consideration

The YOLO model files (`*.pt`) are currently **tracked** but are quite large (~500MB total).

### Option 1: Keep Models in Git (Current)
**Pros:** Easy setup, models always available
**Cons:** Large repository size, slow clones

### Option 2: Exclude Models from Git
To exclude model files, uncomment these lines in `.gitignore`:
```gitignore
# Uncomment to ignore model files:
*.pt
*.pth
*.onnx
```

**Pros:** Smaller repository, faster operations
**Cons:** Need to download models on first run

### Option 3: Use Git LFS (Recommended for Teams)
```bash
# Install Git LFS
git lfs install

# Track model files with LFS
git lfs track "*.pt"
git add .gitattributes
git commit -m "Add Git LFS for model files"
```

## 🚀 Common Git Commands

### Daily Development
```bash
# Check status
git status

# Add changes
git add .

# Commit changes
git commit -m "Your commit message"

# Push to remote
git push

# Pull latest changes
git pull
```

### Branch Management
```bash
# Create new branch
git checkout -b feature/new-feature

# Switch branches
git checkout main

# Merge branch
git merge feature/new-feature

# Delete branch
git branch -d feature/new-feature
```

### Viewing Changes
```bash
# See what files changed
git status

# See what changed in files
git diff

# See commit history
git log --oneline

# See ignored files
git status --ignored
```

## 🔧 Environment Setup

### 1. Copy Environment Template
```bash
cp .env.example .env
```

### 2. Edit `.env` with Your Values
```bash
# Required: Add your Google AI API key
GOOGLE_API_KEY=your_actual_api_key_here
GEMINI_API_KEY=your_actual_api_key_here

# Optional: Customize other settings
SECRET_KEY=your_random_secret_key
```

### 3. Install Dependencies
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

## 📝 Commit Message Guidelines

Use clear, descriptive commit messages:

```bash
# Good examples
git commit -m "Add YOLO object detection feature"
git commit -m "Fix image upload validation bug"
git commit -m "Update README with installation instructions"
git commit -m "Refactor API error handling"

# Bad examples
git commit -m "fix"
git commit -m "update"
git commit -m "changes"
```

## 🔒 Security Notes

- **Never commit** `.env` files with real API keys
- **Always use** `.env.example` as a template
- **Review changes** before committing sensitive files
- **Use environment variables** for all secrets

## 📊 Repository Size

Current repository size breakdown:
- Source code: ~2MB
- Dependencies (ignored): ~200MB
- AI models: ~500MB
- Generated files (ignored): Variable

Total tracked size: ~502MB
