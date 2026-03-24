# Portfolio Inversiones — Guia de Usuario

Sistema de seguimiento de portfolio de inversiones bursátiles. Permite registrar compras y ventas de acciones, calcular el precio promedio de costo (PPC) ponderado y visualizar el estado del portfolio mediante un dashboard con gráficos.

> Para documentacion tecnica del codigo ver [CLAUDE.md](./CLAUDE.md).

---

## Tabla de contenidos

- [Requisitos](#requisitos)
- [Instalacion con Docker (recomendado)](#instalacion-con-docker-recomendado)
- [Instalacion local](#instalacion-local)
- [Como usar la aplicacion](#como-usar-la-aplicacion)
- [API REST — referencia rapida](#api-rest--referencia-rapida)

---

## Requisitos

**Con Docker (recomendado):**
- Docker y Docker Compose instalados.

**Sin Docker (desarrollo local):**
- Python 3.11+
- Node 18+
- MySQL 8.0 corriendo localmente

---

## Instalacion con Docker (recomendado)

```bash
docker compose build
docker compose up -d
```

Esto levanta tres contenedores:

| Contenedor | Puerto | Descripcion |
|---|---|---|
| `portfolio_db` | 3307 | MySQL 8.0. Se inicializa automaticamente con el esquema y los 21 tickers. |
| `portfolio_api` | 5001 | Flask API. Espera a que la DB este healthy. |
| `portfolio_frontend` | 5173 | SvelteKit dev server. |

Verificar que los tres servicios esten corriendo:

```bash
docker compose ps
```

Abrir el browser en `http://localhost:5173`.

---

## Instalacion local

### Backend

1. Crear archivo `.env` en la raiz del proyecto:

```bash
DB_HOST=localhost
DB_USER=<usuario>
DB_PASSWORD=<contrasena>
```

2. Instalar dependencias e iniciar el servidor:

```bash
pip install -r requirements.txt
python app/App.py
# API disponible en http://localhost:5000
```

3. Crear la base de datos `stats` y ejecutar los scripts de `DB/init/` en orden:
   - `01_schema.sql` — crea las tablas
   - `02_tickets.sql` — carga los 21 tickers

### Frontend

```bash
cd frontend
# Editar .env si el backend no corre en el puerto 5001:
# PUBLIC_API_URL=http://localhost:5000
npm install --legacy-peer-deps
npm run dev
# Frontend disponible en http://localhost:5173
```

---

## Como usar la aplicacion

### Dashboard (`/dashboard`)

Vista principal con metricas globales del portfolio:
- Total invertido en pesos y en dolares
- Cantidad de posiciones abiertas
- Grafico de torta: distribucion del portfolio por ticker
- Grafico de barras: PPC (precio promedio de costo) por ticker

### Holdings (`/stocks`)

Tabla con todas las posiciones abiertas. Muestra por cada ticker:
- Nombre del instrumento
- Cantidad de acciones
- PPC (precio promedio de costo)
- Total invertido
- Fecha ponderada de compras

### Transacciones (`/transactions`)

Lista completa de todas las operaciones registradas. Permite:
- Filtrar por ticker
- Identificar compras (badge verde) y ventas (badge rojo)
- Revertir una transaccion: deshace el efecto en el portfolio y recalcula el PPC
- Eliminar una transaccion: la borra sin modificar el estado del stock

### Nueva transaccion (`/transactions/new`)

Formulario para registrar una compra o venta:

| Campo | Descripcion |
|---|---|
| Ticker | Codigo del instrumento (ej: `AAPL`, `NVDA`). Debe estar en la lista de tickers disponibles. |
| Cantidad | Positivo = compra, negativo = venta. |
| Precio unitario | Precio por accion en pesos. |
| Cotizacion USD | Cotizacion del dolar al momento de la operacion. |
| Fecha | Fecha de la operacion. |
| Broker | Opcional. Nombre del broker (ej: IOL, Balanz). |

---

## API REST — referencia rapida

Todas las respuestas siguen el mismo formato:

```json
{
  "status": "Success | Error",
  "message": "string",
  "data": null | object | array
}
```

### Endpoints

| Metodo | Endpoint | Descripcion |
|---|---|---|
| `GET` | `/tickets` | Lista todos los tickers disponibles. |
| `GET` | `/stocks` | Lista todas las posiciones abiertas. |
| `GET` | `/transactions` | Lista todas las transacciones. |
| `GET` | `/transactions?id=<id>` | Obtiene una transaccion por ID. |
| `PUT` | `/transactions` | Registra una nueva transaccion. |
| `POST` | `/transactions/<id>/delete` | Elimina una transaccion. |
| `POST` | `/transactions/<id>/revert` | Revierte una transaccion y recalcula el PPC. |

**Body `PUT /transactions`:**

```json
{
  "ticket_code": "AAPL",
  "quantity": 100,
  "unit_price": 1250.50,
  "usd_quote": 1000,
  "date": 1704067200,
  "broker_name": "IOL"
}
```

### Tickers pre-cargados

`AAPL · AMD · BRKB · DISN · GOOGL · INTC · JPM · KO · MA · MCD · MELI · META · MSFT · NVDA · PAMP · PBR · PEP · V · VIST · WMT · YPF`
