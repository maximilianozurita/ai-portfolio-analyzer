# Installation

## Prerequisites

- Docker and Docker Compose (recommended)
- Or: Python 3.10+, MySQL 8.0, Node.js 18+ (local development)

---

## Option A: Docker (recommended)

### 1. Clone the repository

```bash
git clone <repo-url>
cd ai-portfolio-analyzer
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`. The DB defaults work out of the box with Docker Compose. What requires manual configuration is at least one AI API key:

```env
# AI — fill in at least ONE
GEMINI_API_KEY=     # Google AI Studio (free tier available)
OPENAI_API_KEY=     # OpenAI platform
OPENROUTER_API_KEY= # OpenRouter (free models available)
```

### 3. Start the services

```bash
docker compose build
docker compose up -d
```

### 4. Verify it works

```bash
# Container status
docker compose ps

# Backend logs
docker compose logs api

# Quick API test
curl http://localhost:5001/tickets
```

- REST API: http://localhost:5001
- Frontend: http://localhost:5173

---

## Option B: Local development

### Backend

```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with DB_HOST=localhost and local credentials

# Initialize the MySQL database
mysql -u root -p < DB/init/01_schema.sql
mysql -u root -p < DB/init/02_tickets.sql

# Start the Flask server (from the project root)
python backend/App.py
# API available at http://localhost:5000
```

> In local development the default Flask port is 5000. Docker exposes 5001 (configurable with `API_PORT` in `.env`).

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure the backend URL in .env (project root)
# PUBLIC_API_URL=http://localhost:5000

# Start the development server
npm run dev
# Frontend available at http://localhost:5173
```

For a production build:

```bash
npm run build
npm run preview
```

---

## Environment variables — full reference

All variables are configured in a single `.env` at the project root. Docker Compose and the Flask backend (`python-dotenv`) both read from that file.

| Variable | Required | Description |
|----------|----------|-------------|
| `DB_ROOT_PASSWORD` | Yes (Docker) | MySQL root user password |
| `DB_NAME` | Yes | Database name |
| `DB_USER` | Yes | MySQL user |
| `DB_PASSWORD` | Yes | MySQL user password |
| `API_PORT` | No | Host port for the API (default: `5001`) |
| `FRONTEND_PORT` | No | Host port for the frontend (default: `5173`) |
| `PUBLIC_API_URL` | No | URL the browser uses to reach the API (default: `http://localhost:5001`) |
| `GEMINI_API_KEY` | No* | Google Gemini API key |
| `OPENAI_API_KEY` | No* | OpenAI API key |
| `OPENROUTER_API_KEY` | No* | OpenRouter API key |

*At least one AI API key is required to use the analysis feature.

> `PUBLIC_API_URL` is relevant when accessing from another device on the network (e.g. via Tailscale). In that case it must point to the IP or hostname reachable from the client's browser.

> In Docker, `DB_HOST` is always `db` (the service name in the Compose internal network) and is not set in `.env`. In local development, the backend reads it from `.env` — set `DB_HOST=localhost`.

---

## Ports

| Service | Port |
|---------|------|
| MySQL | 3307 (Docker) / 3306 (local) |
| Flask API | `API_PORT` (default 5001, Docker) / 5000 (local) |
| SvelteKit | `FRONTEND_PORT` (default 5173) |

---

## Troubleshooting

**API cannot connect to the DB**
- In Docker: verify that the `db` service healthcheck passes before `api` tries to connect: `docker compose ps`
- In local: verify that `DB_HOST=localhost` is in `.env` and that MySQL is running

**AI analysis does not work**
- Verify that at least one `*_API_KEY` is configured in `.env`
- The `GET /ai/providers` endpoint returns available providers based on the keys present

**Market prices do not load**
- `yfinance` requires internet access; verify connectivity
- Argentine tickers must have the `.BA` suffix on Yahoo Finance
