# AI Portfolio Analyzer

Gestor de inversiones argentino con análisis de IA. Rastrea posiciones en renta variable (acciones) y renta fija (bonos), obtiene precios de mercado en tiempo real y genera análisis del portfolio usando modelos de lenguaje (Gemini, OpenAI, OpenRouter).

## Documentación

| | |
|---|---|
| [Arquitectura](docs/arquitectura.md) | Diseño del sistema, componentes y flujo de datos |
| [Estructura](docs/estructura.md) | Organización del proyecto y responsabilidades |
| [Instalación](docs/instalacion.md) | Requisitos y pasos para correr el proyecto |
| [Decisiones técnicas](docs/decisiones.md) | Trade-offs y justificaciones de diseño |
| [API](docs/api.md) | Endpoints, request/response y ejemplos |
| [Testing](docs/testing.md) | Cómo correr tests y estrategia de cobertura |

---

## Descripción

Aplicación web para inversores argentinos que necesitan consolidar y analizar su cartera de inversiones. Permite:

- Registrar compras/ventas de acciones y bonos con cálculo automático de PPC (precio promedio de compra)
- Actualizar precios de mercado desde Yahoo Finance y BYMA
- Calcular P&L en tiempo real
- Solicitar análisis de la cartera a modelos de IA, con respuesta en formato estructurado

## Uso rápido

```bash
cp .env.example backend/.env
# Editar backend/.env con credenciales de DB y al menos una API key de IA
docker compose up -d
# API: http://localhost:5001
# Frontend: http://localhost:5173
```

## Tecnologías

**Backend**
- Python 3 + Flask + Flask-CORS
- MySQL 8.0 (driver: mysql-connector-python)
- yfinance — precios de acciones (Yahoo Finance)
- google-generativeai, openai — clientes de IA

**Frontend**
- SvelteKit con file-based routing
- Apache ECharts 5 — gráficos
- marked — renderizado de Markdown
- Tailwind CSS

**Infraestructura**
- Docker Compose (3 servicios: db, api, frontend)

## Instalación rápida

1. Clonar el repo y copiar `.env.example` a `backend/.env`
2. Completar credenciales de base de datos y al menos una API key de IA
3. `docker compose up -d`

Ver [docs/instalacion.md](docs/instalacion.md) para instrucciones completas, incluyendo desarrollo local sin Docker.

## Arquitectura (resumen)

Backend Flask en 3 capas (routes → services → models) + frontend SvelteKit. Los providers de IA son intercambiables mediante el patrón Strategy. Ver [docs/arquitectura.md](docs/arquitectura.md).

## Estructura del proyecto

```
ai-portfolio-analyzer/
├── backend/          # API Flask
│   ├── App.py        # Entry point
│   ├── config/       # Config y mensajes de error
│   └── src/
│       ├── routes/   # Blueprints HTTP
│       ├── services/ # Lógica de negocio
│       └── models/   # Acceso a datos (MySQL)
├── frontend/         # SvelteKit app
│   └── src/routes/   # Páginas
├── DB/               # Schema SQL e inicialización
└── docker-compose.yml
```

Ver [docs/estructura.md](docs/estructura.md) para el árbol completo con explicaciones.

