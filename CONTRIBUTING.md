# Contributing to TasteMaker

Thank you for your interest in contributing to TasteMaker! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- An Anthropic API key for testing AI features

### Setting Up the Development Environment

1. **Clone the repository**
   ```bash
   git clone https://github.com/[user]/tastemaker.git
   cd tastemaker
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up the frontend**
   ```bash
   cd frontend
   npm install
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Add your ANTHROPIC_API_KEY to .env
   ```

5. **Initialize the database**
   ```bash
   cd backend
   alembic upgrade head
   ```

6. **Start development servers**

   Terminal 1 (Backend):
   ```bash
   cd backend/src
   source ../venv/bin/activate
   uvicorn main:app --reload --port 8000
   ```

   Terminal 2 (Frontend):
   ```bash
   cd frontend
   npm run dev
   ```

## Project Structure

```
tastemaker/
├── backend/
│   ├── src/               # Python source code
│   │   ├── main.py        # FastAPI app entry point
│   │   ├── config.py      # Centralized configuration
│   │   ├── models.py      # SQLAlchemy models + Pydantic schemas
│   │   ├── *_routes.py    # API route handlers
│   │   └── *_service.py   # Business logic services
│   ├── migrations/        # Alembic database migrations
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── pages/         # Page components
│   │   ├── components/    # Reusable UI components
│   │   ├── contexts/      # React contexts
│   │   └── services/      # API client
│   └── package.json       # Node dependencies
└── .env.example           # Environment template
```

## Code Style

### Python (Backend)

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Write docstrings for modules, classes, and functions
- Keep functions focused and small

### TypeScript (Frontend)

- Use TypeScript strict mode
- Prefer functional components with hooks
- Use proper typing (avoid `any`)
- Follow React best practices

## Making Changes

### Branching Strategy

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes with clear, atomic commits

3. Push and create a pull request

### Commit Messages

Write clear commit messages that explain the "why":

```
Add color palette refinement feature

Users can now refine their selected color palette by choosing
variations that stay within the same color family. This helps
narrow down the exact shades they prefer.
```

### Pull Requests

- Provide a clear description of what changed and why
- Include screenshots for UI changes
- Reference any related issues
- Ensure all tests pass (when applicable)

## Database Changes

When modifying database models:

1. Update the model in `backend/src/models.py`
2. Create a migration:
   ```bash
   cd backend
   alembic revision --autogenerate -m "Description of change"
   ```
3. Review the generated migration file
4. Apply the migration:
   ```bash
   alembic upgrade head
   ```

**Note:** SQLite has limitations with ALTER operations. Test migrations with PostgreSQL for production compatibility.

## Testing

### Running the Backend

```bash
cd backend/src
uvicorn main:app --reload --port 8000
```

Verify the API at http://localhost:8000/docs

### Running the Frontend

```bash
cd frontend
npm run dev
```

Access at http://localhost:5173

### Manual Testing Checklist

Before submitting a PR:

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] API health check returns OK (`/health`)
- [ ] Single-user mode works (auto-login)
- [ ] Color exploration flow works
- [ ] Typography exploration flow works

## Getting Help

- Open an issue for bugs or feature requests
- Check existing issues before creating new ones
- Provide detailed reproduction steps for bugs

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
