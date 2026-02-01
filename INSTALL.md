# TasteMaker Installation Guide

This guide is designed for Claude Code to follow when setting up TasteMaker.

## Prerequisites

Before starting, ensure the following are installed:
- Python 3.11 or higher
- Node.js 20 or higher
- An Anthropic API key (get one at https://console.anthropic.com/)

## Installation Steps

### Step 1: Create Backend Virtual Environment

```bash
cd backend
python -m venv venv
```

### Step 2: Activate Virtual Environment and Install Python Dependencies

On macOS/Linux:
```bash
source backend/venv/bin/activate
pip install -r backend/requirements.txt
```

On Windows:
```bash
backend\venv\Scripts\activate
pip install -r backend\requirements.txt
```

### Step 3: Install Frontend Dependencies

```bash
cd frontend
npm install
```

### Step 4: Create Environment File

```bash
cp .env.example .env
```

### Step 5: Configure API Key

**IMPORTANT**: Ask the user for their Anthropic API key, or remind them to add it to the .env file.

The user needs to edit `.env` and add their API key:
```
ANTHROPIC_API_KEY=sk-ant-...
```

If the user doesn't have an API key yet, direct them to: https://console.anthropic.com/

### Step 6: Initialize Database

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
alembic upgrade head
```

### Step 7: Start the Application

Start both the backend and frontend in separate terminals:

**Terminal 1 - Backend:**
```bash
cd backend/src
source ../venv/bin/activate  # or ..\venv\Scripts\activate on Windows
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## Verification

After starting both services:

1. Backend health check: http://localhost:8000/health
   - Should return `{"status": "ok", "config": {...}}`

2. Frontend: http://localhost:5173
   - Should show the TasteMaker landing page

3. In single-user mode (default), you should be automatically logged in as "Local User"

## Common Issues

### "ANTHROPIC_API_KEY is not configured"

The API key is missing. Remind the user to:
1. Get a key at https://console.anthropic.com/
2. Add it to the `.env` file

### Import errors when starting backend

Make sure to run uvicorn from inside the `backend/src` directory, not from `backend/`.

### Database errors

Run migrations from the `backend/` directory:
```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

## Configuration Options

TasteMaker can be configured via environment variables in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | (required) | Your Anthropic API key |
| `DATABASE_URL` | `sqlite:///./tastemaker.db` | Database connection string |
| `SINGLE_USER_MODE` | `true` | Skip authentication for local use |
| `ENABLE_BACKGROUND_JOBS` | `false` | Use Redis/Celery for video processing |

## Quick Start Script (Optional)

For convenience, you can create a dev script. On macOS/Linux:

```bash
#!/bin/bash
# scripts/dev.sh

# Start backend in background
cd backend/src
source ../venv/bin/activate
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend
cd ../../frontend
npm run dev &
FRONTEND_PID=$!

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
```

Make it executable: `chmod +x scripts/dev.sh`
