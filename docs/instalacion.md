# Instalación

## Requisitos previos

- Docker y Docker Compose (recomendado)
- O: Python 3.10+, MySQL 8.0, Node.js 18+ (desarrollo local)

---

## Opción A: Docker (recomendada)

### 1. Clonar el repositorio

```bash
git clone <repo-url>
cd ai-portfolio-analyzer
```

### 2. Configurar variables de entorno

```bash
cp .env.example backend/.env
```

Editar `backend/.env`:

```env
# Base de datos (no cambiar si usás Docker)
DB_HOST=db
DB_USER=root
DB_PASSWORD=tu_password_segura

# AI — completar al menos UNA
GEMINI_API_KEY=     # Google AI Studio (tiene tier gratuito)
OPENAI_API_KEY=     # OpenAI platform
OPENROUTER_API_KEY= # OpenRouter (modelos gratuitos disponibles)
```

> El `DB_HOST=db` apunta al nombre del servicio de Docker Compose. Para desarrollo local usar `localhost`.

### 3. Levantar los servicios

```bash
docker compose build
docker compose up -d
```

### 4. Verificar que funciona

```bash
# Estado de los contenedores
docker compose ps

# Logs del backend
docker compose logs api

# Test rápido de la API
curl http://localhost:5001/tickets
```

- API REST: http://localhost:5001
- Frontend: http://localhost:5173

---

## Opción B: Desarrollo local

### Backend

```bash
# Instalar dependencias Python
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example backend/.env
# Editar backend/.env con DB_HOST=localhost y credenciales locales

# Inicializar la base de datos MySQL
mysql -u root -p < DB/init/01_schema.sql
mysql -u root -p < DB/init/02_tickets.sql

# Levantar el servidor Flask
python backend/App.py
# API disponible en http://localhost:5000
```

> En desarrollo local el puerto por defecto de Flask es 5000. Docker expone el 5001.

### Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Configurar la URL del backend
# Crear frontend/.env con:
# PUBLIC_API_URL=http://localhost:5000

# Levantar el servidor de desarrollo
npm run dev
# Frontend disponible en http://localhost:5173
```

Para build de producción:

```bash
npm run build
npm run preview
```

---

## Variables de entorno — referencia completa

| Variable | Requerida | Descripción |
|----------|-----------|-------------|
| `DB_HOST` | Sí | Host de MySQL (`db` en Docker, `localhost` en local) |
| `DB_USER` | Sí | Usuario de MySQL |
| `DB_PASSWORD` | Sí | Password de MySQL |
| `GEMINI_API_KEY` | No* | API key de Google Gemini |
| `OPENAI_API_KEY` | No* | API key de OpenAI |
| `OPENROUTER_API_KEY` | No* | API key de OpenRouter |

*Al menos una API key de IA es necesaria para usar la funcionalidad de análisis.

---

## Puertos

| Servicio | Puerto |
|----------|--------|
| MySQL | 3307 (Docker) / 3306 (local) |
| Flask API | 5001 (Docker) / 5000 (local) |
| SvelteKit | 5173 |

---

## Solución de problemas comunes

**La API no conecta a la DB**
- Verificar que `DB_HOST=db` en Docker o `DB_HOST=localhost` en local
- En Docker, esperar a que el healthcheck del servicio `db` pase: `docker compose ps`

**El análisis de IA no funciona**
- Verificar que al menos una `*_API_KEY` esté configurada en `backend/.env`
- El endpoint `GET /ai/providers` retorna los providers disponibles según las keys presentes

**Precios de mercado no cargan**
- `yfinance` requiere acceso a internet; verificar conectividad
- Los tickers argentinos deben tener sufijo `.BA` en Yahoo Finance
