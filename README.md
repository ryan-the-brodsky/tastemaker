# TasteMaker

Extract UI/UX taste preferences and generate AI-readable style profiles.

TasteMaker helps you capture your design preferences through interactive exploration, then outputs machine-readable "Agent Skills" that AI coding tools can use to make consistent design decisions.

## Install with Claude Code (Recommended)

The easiest way to get started:

```bash
git clone https://github.com/[user]/tastemaker.git
cd tastemaker
claude
```

Then tell Claude: **"install this project"** or **"set up tastemaker"**

Claude Code will read the installation guide and handle setup for your platform.

## Manual Installation

### Prerequisites

- Python 3.11+
- Node.js 20+
- An Anthropic API key ([get one here](https://console.anthropic.com/))

### Quick Start

```bash
# Clone the repository
git clone https://github.com/[user]/tastemaker.git
cd tastemaker

# Set up backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up frontend
cd ../frontend
npm install

# Configure environment
cd ..
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Initialize database
cd backend
alembic upgrade head

# Start backend (in one terminal)
cd src
uvicorn main:app --reload --port 8000

# Start frontend (in another terminal)
cd frontend
npm run dev
```

Access the app at http://localhost:5173

## Docker Installation

```bash
# Clone and configure
git clone https://github.com/[user]/tastemaker.git
cd tastemaker
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Start with Docker
docker-compose up

# Access at http://localhost:8000
```

For a full setup with PostgreSQL and Redis:
```bash
docker-compose -f docker-compose.full.yml up
```

## How It Works

1. **Describe your project** - Tell TasteMaker what you're building
2. **Explore colors** - Choose from AI-generated color palettes
3. **Explore typography** - Select font pairings that match your style
4. **Refine components** - A/B test button styles, cards, inputs, etc.
5. **Export your style** - Download an Agent Skills package

The output is a structured ruleset that AI coding assistants can use to generate consistent UI components matching your taste.

## Configuration

TasteMaker is configured via environment variables. Copy `.env.example` to `.env` and customize:

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | (required) | Your Anthropic API key |
| `DATABASE_URL` | `sqlite:///./tastemaker.db` | SQLite (default) or PostgreSQL |
| `SINGLE_USER_MODE` | `true` | Skip auth for local use |
| `ENABLE_BACKGROUND_JOBS` | `false` | Use Celery for video processing |

## Architecture

```
tastemaker/
├── backend/           # FastAPI REST API (Python)
│   └── src/           # Source code
├── frontend/          # React + Vite + TypeScript + Tailwind
├── .env.example       # Environment template
├── docker-compose.yml # Simple Docker setup
└── INSTALL.md         # Installation guide
```

## API Documentation

When the backend is running, API docs are available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.
