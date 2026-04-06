# AI Portfolio Analyzer

Argentine investment portfolio manager with AI analysis. Tracks equity (stocks) and fixed-income (bonds) positions, fetches real-time market prices, and generates portfolio analysis using language models (Gemini, OpenAI, OpenRouter).

## Documentation

| | |
|---|---|
| [Architecture](docs/arquitectura.md) | System design, components and data flow |
| [Structure](docs/estructura.md) | Project organization and responsibilities |
| [Installation](docs/instalacion.md) | Requirements and steps to run the project |
| [Technical decisions](docs/decisiones.md) | Trade-offs and design justifications |
| [API](docs/api.md) | Endpoints, request/response and examples |
| [Testing](docs/testing.md) | How to run tests and coverage strategy |

---

## Description

Web application for Argentine investors who need to consolidate and analyze their investment portfolio. It allows you to:

- Record stock and bond buy/sell operations with automatic PPC (weighted average cost) calculation
- Update market prices from Yahoo Finance and BYMA
- Calculate real-time P&L
- Request portfolio analysis from AI models, with a structured 7-section response

## Quick start

```bash
cp .env.example .env
# Edit .env with at least one AI API key
docker compose up -d
# API: http://localhost:5001
# Frontend: http://localhost:5173
```

## Technologies

**Backend**
- Python 3 + Flask + Flask-CORS
- MySQL 8.0 (driver: mysql-connector-python)
- yfinance — stock prices (Yahoo Finance)
- google-generativeai, openai — AI clients

**Frontend**
- SvelteKit with file-based routing
- Apache ECharts 5 — charts
- marked — Markdown rendering
- Tailwind CSS

**Infrastructure**
- Docker Compose (3 services: db, api, frontend)

## Quick installation

1. Clone the repo and copy `.env.example` to `.env`
2. Fill in at least one AI API key (DB credentials have working defaults)
3. `docker compose build && docker compose up -d`

See [docs/instalacion.md](docs/instalacion.md) for complete instructions, including local development without Docker.

## Architecture (summary)

3-layer Flask backend (routes → services → models) + SvelteKit frontend. AI providers are interchangeable via the Strategy pattern. The frontend caches market prices in Svelte stores and passes them to the analysis endpoint, avoiding redundant calls. See [docs/arquitectura.md](docs/arquitectura.md).

## Project structure

```
ai-portfolio-analyzer/
├── backend/          # Flask API
│   ├── App.py        # Entry point
│   ├── config/       # Config and error messages
│   └── src/
│       ├── routes/   # HTTP Blueprints
│       ├── services/ # Business logic + AI providers
│       └── models/   # Data access (MySQL)
├── frontend/         # SvelteKit app
│   └── src/
│       ├── lib/      # api.js, stores.js, reusable components
│       └── routes/   # Pages
├── DB/               # SQL schema and initialization
├── .env.example      # Environment variables template
└── docker-compose.yml
```

See [docs/estructura.md](docs/estructura.md) for the full annotated tree.
