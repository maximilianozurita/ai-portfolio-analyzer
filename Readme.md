# Portfolio Inversiones

Sistema de seguimiento de portfolio bursátil para el mercado argentino. Permite registrar compras, ventas y operaciones de bonos, calcular el precio promedio de costo (PPC) ponderado, visualizar el estado del portfolio con gráficos interactivos, obtener precios de mercado en tiempo real y **analizar el portfolio con inteligencia artificial** usando múltiples providers (Gemini, GPT, OpenRouter).

> Documentación técnica del código: [CLAUDE.md](./CLAUDE.md)

---

## Tabla de contenidos

- [Instalación con Docker](#instalación-con-docker-recomendado)
- [Instalación local](#instalación-local)
- [Stack tecnológico](#stack-tecnológico)
- [Interfaz de usuario](#interfaz-de-usuario)
- [Analizador de Portfolio con IA](#analizador-de-portfolio-con-ia)
- [Datos de prueba](#datos-de-prueba)
- [API REST](#api-rest--referencia-rápida)

---

## Instalación con Docker (recomendado)

### Requisitos

- Docker y Docker Compose

### Pasos

**1. Configurar variables de entorno:**

```bash
cp .env.example backend/.env
```

Editar `backend/.env` con los valores de base de datos y, opcionalmente, las API keys de los providers de IA:

```bash
# Base de datos (valores por defecto para Docker)
DB_HOST=db
DB_USER=root
DB_PASSWORD=rootpassword

# API keys de IA (al menos una para usar el analizador)
GEMINI_API_KEY=
OPENAI_API_KEY=
OPENROUTER_API_KEY=
```

**2. Levantar los contenedores:**

```bash
docker compose build
docker compose up -d
```

Esto inicia tres servicios:

| Contenedor | Puerto | Descripción |
|---|---|---|
| `portfolio_db` | 3307 | MySQL 8.0. Se inicializa automáticamente con el esquema y los 21 tickers. |
| `portfolio_api` | 5001 | Flask API. Espera a que la DB esté healthy. |
| `portfolio_frontend` | 5173 | SvelteKit dev server. |

**3. Verificar que los servicios estén corriendo:**

```bash
docker compose ps
```

**4. Abrir la aplicación en:** `http://localhost:5173`

---

## Instalación local

### Requisitos

- Python 3.11+
- Node 18+
- MySQL 8.0 corriendo localmente

### Backend

```bash
cp .env.example backend/.env
# Editar backend/.env con los valores de la DB local

pip install -r requirements.txt
python backend/App.py
# API disponible en http://localhost:5000
```

Crear la base de datos `stats` y ejecutar los scripts de `DB/init/` en orden:
- `01_schema.sql` — crea las tablas
- `02_tickets.sql` — carga los 21 tickers

### Frontend

```bash
cd frontend
npm install
npm run dev
# Frontend disponible en http://localhost:5173
```

Si el backend corre en un puerto distinto al 5001, editar `frontend/.env`:

```
PUBLIC_API_URL=http://localhost:5000
```

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python 3.11 · Flask · flask-cors |
| Base de datos | MySQL 8.0 · mysql-connector-python |
| Frontend | SvelteKit · Svelte 4 · Vite |
| Estilos | Tailwind CSS 3 |
| Gráficos | Apache ECharts 5 |
| Precios de mercado | yfinance (Yahoo Finance) |
| IA | google-generativeai · openai (también usado para OpenRouter) |
| Contenedores | Docker · Docker Compose |

La API sigue una arquitectura de tres capas: **Routes → Services → Models**. El módulo de IA es independiente y se activa solo si hay al menos una API key configurada.

---

## Interfaz de usuario

La aplicación se divide en las siguientes secciones, accesibles desde la barra de navegación:

### Dashboard

Vista global del portfolio con métricas combinadas de acciones y bonos:

- **Total invertido** y **valor actual** (si hay precios de mercado cargados)
- **P&L total** en pesos y porcentaje
- Dos paneles resumen: **Renta Variable** y **Renta Fija**, cada uno con su respectivo botón para actualizar precios desde Yahoo Finance
- **Gráfico de distribución global** (donut): muestra el peso de cada activo sobre el total del portfolio. Puede alternar entre distribución por PPC o por precio de mercado actual
- **Gráfico de rendimiento** (barras): P&L % por ticker de renta variable, en verde/rojo

### Renta Variable (`/stocks`)

Gestión de posiciones de acciones y CEDEARs:

- Métricas: total invertido, posiciones abiertas, valor actual y P&L (cuando hay precios disponibles)
- Gráfico de distribución por ticker (PPC o precio actual)
- Gráfico de rendimiento por ticker
- Tabla de posiciones con precio actual, valor actual y P&L por ticker
- **Actualizar precios**: obtiene cotizaciones en tiempo real desde Yahoo Finance (BYMA · ARS). Los precios se cachean en el cliente y persisten mientras no se recargue la página
- Tab **Ajustar posición**: aplica un factor multiplicador a cantidad y PPC (para splits o cambios de ratio de CEDEARs)
- Tab **Importar posición inicial**: carga el portfolio desde un CSV sin necesidad de ingresar el historial de transacciones

### Renta Fija (`/bonds`)

Gestión de posiciones de bonos soberanos y corporativos:

- Métricas: total invertido, posiciones abiertas, valor actual y P&L
- Gráfico de distribución por bono (PPC o precio actual)
- Tabla de holdings con PPC, paridad, precio actual y P&L
- **Actualizar precios**: igual que en Renta Variable, con nota de que la cobertura de bonos en Yahoo Finance es parcial
- Tab **Operaciones**: historial de transacciones de bonos con opciones de revertir o eliminar
- Tab **Importar posición inicial**: carga desde CSV

### Transacciones (`/transactions`)

Historial completo de operaciones de acciones y CEDEARs:

- Filtro por ticker
- Badges de compra (verde) y venta (rojo)
- **Revertir**: deshace el efecto en el portfolio y recalcula el PPC
- **Eliminar**: borra la transacción sin modificar el estado del stock

### Nueva Operación (`/operaciones/nueva`)

Formulario unificado para registrar operaciones:

- Tab **Acción / CEDEAR**: registra compras o ventas con ticker, cantidad, precio, cotización USD, fecha y broker
- Tab **Bono**: registra compras, ventas, amortizaciones o cupones con código de bono, cantidad, precio, valor técnico, cotización USD y fecha

### Analizar con IA (`/analyze`)

Ver sección [Analizador de Portfolio con IA](#analizador-de-portfolio-con-ia).

---

## Analizador de Portfolio con IA

La página `/analyze` conecta tu portfolio con modelos de lenguaje para generar un informe de análisis profesional. Es la funcionalidad central de la aplicación.

### Qué analiza

El analizador envía al modelo seleccionado:

- Todas las posiciones abiertas de **acciones y CEDEARs** con PPC, cantidad y valor invertido
- Todas las posiciones de **bonos** con PPC, paridad y valor invertido
- Si los precios de mercado están cargados (desde el Dashboard o las páginas de Renta Variable/Fija): precio actual, valor actual y **P&L en pesos y porcentaje** por activo

El informe incluye las siguientes secciones:

1. **Resumen Ejecutivo** — composición del portfolio, valor total invertido y actual
2. **Análisis por Clase de Activo** — acciones y bonos por separado
3. **Diversificación y Concentración** — balance entre activos, sectores y geografía
4. **Rendimiento** — análisis del P&L si hay datos de mercado disponibles
5. **Riesgos Identificados** — concentración, exposición cambiaria, riesgo soberano, liquidez
6. **Contexto del Mercado Argentino** — factores macroeconómicos relevantes
7. **Conclusiones y Consideraciones** — puntos de atención y acciones a evaluar

La respuesta se renderiza en **Markdown** con formato tipográfico completo.

### Configurar un provider de IA

Agregar al menos una clave en `backend/.env`:

```bash
# Google Gemini — recomendado, capa gratuita generosa
# Obtener en: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=tu_key_aqui

# OpenAI GPT
# Obtener en: https://platform.openai.com/api-keys
OPENAI_API_KEY=tu_key_aqui

# OpenRouter — acceso a modelos completamente gratuitos
# Obtener en: https://openrouter.ai/keys
OPENROUTER_API_KEY=tu_key_aqui
```

Solo aparecen en el selector los providers cuya clave está configurada.

### Providers y modelos disponibles

| Provider | Modelos | Costo |
|---|---|---|
| Google Gemini | Gemini 2.5 Flash, Gemini 2.0 Flash, Gemini 1.5 Pro | Gratuito con límites / pago |
| OpenAI GPT | GPT-4o, GPT-4o Mini, GPT-4 Turbo | Pago |
| OpenRouter | Llama 3.3 70B, DeepSeek R1, Mistral 7B | Gratuito |

> **Consejo**: para usar el analizador sin costo, configurar `OPENROUTER_API_KEY` y seleccionar cualquiera de los modelos gratuitos de OpenRouter.

### Contexto de mercado en el análisis

Para obtener un análisis más rico (con P&L y precios actuales), actualizar los precios antes de analizar:

1. Ir al **Dashboard** y presionar "Actualizar precios" en el panel de Renta Variable y/o Renta Fija
2. Los precios se guardan en caché en el cliente
3. Al presionar **Analizar Portfolio**, los precios cacheados se incluyen automáticamente en el contexto enviado al modelo

Si no hay precios cargados, el análisis se basa únicamente en los valores de PPC.

### Exportar el informe

Una vez generado el análisis, están disponibles dos opciones de descarga:

- **Descargar .md**: archivo Markdown con encabezado de fecha, provider y modelo
- **Descargar PDF**: abre una ventana con el informe en formato tipográfico y activa el diálogo de impresión del navegador (seleccionar "Guardar como PDF")

---

## Datos de prueba

En `Docs/samples/` hay CSVs de ejemplo para probar la importación:

### `stocks_ejemplo.csv` — Acciones

```
ticket_code,quantity,ppc,weighted_date
AAPL,50,18500.00,2024-03-15
NVDA,20,42000.00,2024-06-10
```

Importar desde: **Renta Variable → Importar posición inicial**

### `bonos_ejemplo.csv` — Bonos

```
bond_code,quantity,ppc,ppc_paridad,weighted_date
AL30,5000,72.00,0.6800,2024-02-10
GD30,3000,78.00,0.7400,2024-05-18
```

> El campo `ppc` en el CSV debe ingresarse como precio bruto (ej. `72.00`); el sistema lo divide por 100 internamente.

Importar desde: **Renta Fija → Importar posición inicial**

---

## API REST — referencia rápida

Todas las respuestas siguen el formato:

```json
{
  "status": "Success | Error",
  "message": "string",
  "data": null | object | array
}
```

### Endpoints

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/tickets` | Lista todos los tickers disponibles. |
| `GET` | `/stocks` | Lista todas las posiciones abiertas de acciones. |
| `GET` | `/transactions` | Lista todas las transacciones. |
| `PUT` | `/transactions` | Registra una nueva transacción. |
| `POST` | `/transactions/<id>/revert` | Revierte una transacción y recalcula el PPC. |
| `POST` | `/transactions/<id>/delete` | Elimina una transacción sin modificar el stock. |
| `GET` | `/bond-holdings` | Lista posiciones de bonos. |
| `GET` | `/bond-transactions` | Lista transacciones de bonos. |
| `PUT` | `/bond-transactions` | Registra una operación de bono. |
| `POST` | `/bond-transactions/<id>/revert` | Revierte una operación de bono. |
| `GET` | `/market/prices/stocks` | Cotizaciones actuales de acciones (Yahoo Finance). |
| `GET` | `/market/prices/bonds` | Cotizaciones actuales de bonos (Yahoo Finance). |
| `GET` | `/ai/providers` | Lista providers de IA disponibles. |
| `POST` | `/ai/analyze` | Genera un análisis del portfolio con IA. |

**Body `POST /ai/analyze`:**

```json
{
  "provider": "gemini",
  "model": "gemini-2.5-flash",
  "market_prices_stocks": { "AAPL": { "price": 18500, "pnl_pct": 5.2, ... } },
  "market_prices_bonds": { "AL30": { "price": 0.72, "pnl_pct": -1.4, ... } }
}
```

Los campos `market_prices_stocks` y `market_prices_bonds` son opcionales. Si se incluyen, el análisis incorpora precios actuales y P&L por activo.

### Tickers pre-cargados

`AAPL · AMD · BRKB · DISN · GOOGL · INTC · JPM · KO · MA · MCD · MELI · META · MSFT · NVDA · PAMP · PBR · PEP · V · VIST · WMT · YPF`
