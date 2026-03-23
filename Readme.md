# Portfolio Inversiones

Sistema de seguimiento de portfolio de inversiones bursátiles. Permite registrar compras y ventas de acciones, calcular el precio promedio de costo (PPC) ponderado por cantidad, y visualizar el estado actual del portfolio mediante un dashboard con gráficos.

---

## Tabla de contenidos

- [Arquitectura](#arquitectura)
- [Stack tecnológico](#stack-tecnológico)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Primeros pasos](#primeros-pasos)
  - [Con Docker (recomendado)](#con-docker-recomendado)
  - [Desarrollo local](#desarrollo-local)
- [API REST](#api-rest)
- [Lógica de negocio](#lógica-de-negocio)
- [Base de datos](#base-de-datos)
- [Frontend](#frontend)
- [Tests](#tests)

---

## Arquitectura

```
┌─────────────────────────────────────────────────────┐
│  Browser  :5173                                     │
│  SvelteKit + Tailwind CSS + Apache ECharts          │
└────────────────────┬────────────────────────────────┘
                     │ HTTP / REST
┌────────────────────▼────────────────────────────────┐
│  Flask API  :5001                                   │
│  Routes → Services → Models                         │
└────────────────────┬────────────────────────────────┘
                     │ mysql-connector-python
┌────────────────────▼────────────────────────────────┐
│  MySQL 8.0  :3307                                   │
│  tickets · stock · transaction                      │
└─────────────────────────────────────────────────────┘
```

La API sigue una arquitectura de tres capas:

| Capa | Responsabilidad |
|------|----------------|
| **Routes** (`src/routes/`) | Blueprints Flask. Reciben requests HTTP y devuelven respuestas normalizadas. |
| **Services** (`src/services/`) | Lógica de negocio. Cálculo de PPC, validación de operaciones, orquestación. |
| **Models** (`src/models/`) | Acceso a datos. SQL, validación de atributos, CRUD. |

---

## Stack tecnológico

| Componente | Tecnología |
|-----------|-----------|
| Backend | Python 3.11 · Flask · flask-cors |
| Base de datos | MySQL 8.0 · mysql-connector-python |
| Frontend | SvelteKit · Svelte 4 · Vite |
| Estilos | Tailwind CSS 3 |
| Gráficos | Apache ECharts 5 |
| Contenerización | Docker · Docker Compose |

---

## Estructura del proyecto

```
PortfolioInversiones/
├── Dockerfile                  # Imagen del backend (Python 3.11)
├── docker-compose.yml          # Orquestación de los 3 servicios
├── requirements.txt            # Dependencias Python
│
├── DB/
│   └── init/
│       ├── 01_schema.sql       # DDL: tablas tickets, stock, transaction
│       └── 02_tickets.sql      # Datos iniciales (21 tickers)
│
├── app/
│   ├── App.py                  # Entry point Flask
│   ├── config/
│   │   ├── Settings.py
│   │   └── msgs_es.json        # Mensajes de error/éxito en español
│   ├── src/
│   │   ├── models/
│   │   │   ├── main_class.py   # Clase base con validación y CRUD
│   │   │   ├── conector.py     # Wrapper MySQL
│   │   │   ├── ticket.py       # Modelo Ticket (referencia maestro)
│   │   │   ├── stock.py        # Modelo Stock (posiciones actuales)
│   │   │   └── transaction.py  # Modelo Transaction (eventos)
│   │   ├── services/
│   │   │   ├── stock_service.py
│   │   │   └── transaction_service.py
│   │   ├── routes/
│   │   │   ├── routes_base.py  # create_response() normaliza todas las respuestas
│   │   │   ├── stocks.py
│   │   │   ├── transactions.py
│   │   │   └── tickets.py
│   │   └── utils/
│   │       └── msgs_handler.py
│   └── tests/
│       ├── suite_unit_test.py
│       ├── factory/            # Factories para datos de test
│       └── unit_tests/         # Tests unitarios por capa
│
└── frontend/
    ├── Dockerfile              # Imagen del frontend (Node 20)
    ├── package.json
    ├── src/
    │   ├── lib/
    │   │   ├── api.js          # Cliente HTTP para todos los endpoints
    │   │   └── components/     # MetricCard, StockTable, TransactionTable, Charts
    │   └── routes/
    │       ├── +layout.svelte  # Navbar global
    │       ├── dashboard/      # Métricas + gráficos
    │       ├── stocks/         # Tabla de holdings
    │       └── transactions/   # Lista + formulario de carga
    └── .env                    # PUBLIC_API_URL (solo desarrollo local)
```

---

## Primeros pasos

### Con Docker (recomendado)

**Requisitos:** Docker y Docker Compose instalados.

```bash
docker compose build
docker compose up -d
```

Esto levanta tres contenedores:

| Contenedor | Puerto | Descripción |
|-----------|--------|-------------|
| `portfolio_db` | 3307 | MySQL 8.0. Se inicializa automáticamente con el esquema y los 21 tickers. |
| `portfolio_api` | 5001 | Flask API. Espera a que la DB esté healthy. |
| `portfolio_frontend` | 5173 | SvelteKit dev server. |

Verificar que los tres servicios estén corriendo:

```bash
docker compose ps
```

Abrir el browser en `http://localhost:5173`.

### Desarrollo local

**Requisitos:** Python 3.11+, Node 18+, MySQL corriendo localmente.

**Backend:**

```bash
# Crear archivo .env en la raíz del proyecto
echo "DB_HOST=localhost" >> .env
echo "DB_USER=<usuario>" >> .env
echo "DB_PASSWORD=<contraseña>" >> .env

pip install -r requirements.txt
python app/App.py
# API disponible en http://localhost:5000
```

**Frontend:**

```bash
cd frontend
# El archivo .env ya contiene PUBLIC_API_URL=http://localhost:5001
# Si el backend corre localmente en el puerto 5000, actualizar el valor
npm install --legacy-peer-deps
npm run dev
# Frontend disponible en http://localhost:5173
```

> **Nota:** La base de datos debe existir con el nombre `stats`. Ejecutar los scripts de `DB/init/` manualmente si no se usa Docker.

---

## API REST

Todas las respuestas siguen el mismo formato:

```json
{
  "status": "Success" | "Error",
  "message": "string",
  "data": null | object | array
}
```

### Tickers

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/tickets` | Lista todos los tickers disponibles. |

**Respuesta `GET /tickets`:**
```json
{
  "status": "Success",
  "data": [
    { "ticket_code": "AAPL", "name": "Apple Inc.", "ratio": 1 }
  ]
}
```

### Holdings (Stock)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/stocks` | Lista todas las posiciones abiertas con PPC y fecha ponderada. |

**Respuesta `GET /stocks`:**
```json
{
  "status": "Success",
  "data": [
    {
      "id": 1,
      "ticket_code": "AAPL",
      "name": "Apple Inc.",
      "ppc": 1250.5000,
      "quantity": 100,
      "weighted_date": 1704067200
    }
  ]
}
```

### Transacciones

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/transactions` | Lista todas las transacciones. |
| `GET` | `/transactions?id=<id>` | Obtiene una transacción por ID. |
| `PUT` | `/transactions` | Registra una nueva transacción (compra o venta). |
| `POST` | `/transactions/<id>/delete` | Elimina una transacción sin revertir el stock. |
| `POST` | `/transactions/<id>/revert` | Revierte una transacción y recalcula el PPC del stock. |

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

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `ticket_code` | string | Sí | Debe existir en la tabla `tickets`. |
| `quantity` | int | Sí | Positivo = compra, negativo = venta. |
| `unit_price` | float | Sí | Precio por acción en pesos. |
| `usd_quote` | int | Sí | Cotización del dólar al momento de la operación. |
| `date` | int | Sí | Unix timestamp de la fecha de operación. |
| `broker_name` | string | No | Nombre del broker (IOL, Balanz, etc.). |
| `transaction_key` | int | No | ID externo de referencia. |

---

## Lógica de negocio

### Precio Promedio de Costo (PPC)

El PPC es el precio promedio ponderado por cantidad de todas las compras de un ticker. También se mantiene una `weighted_date` (fecha ponderada) que representa el centro de masa temporal de las compras.

**Al registrar una compra:**

```
nuevo_ppc = round((ppc_anterior × qty_anterior + precio_unitario × nueva_qty) / (qty_anterior + nueva_qty), 4)
nueva_fecha = int((fecha_anterior × qty_anterior + fecha_transacción × nueva_qty) / (qty_anterior + nueva_qty))
```

**Al registrar una venta:**

El PPC y la `weighted_date` no cambian. Solo disminuye la cantidad.

**Al revertir una compra:**

Se aplica la inversa de la fórmula de compra para restituir el PPC y la fecha previos.

**Al revertir una venta:**

La cantidad aumenta. El PPC y la `weighted_date` no cambian.

**Eliminación automática del stock:**

Cuando la cantidad llega a 0 luego de una transacción o reversión, la fila de `stock` se elimina (no se zeroa).

### Flujo de una transacción

```
PUT /transactions
  └─ transaction_service.add_transaction(data)
       ├─ Transaction.verify(data)      → valida ticket_code contra tabla tickets
       ├─ Transaction.add(data)         → INSERT en tabla transaction
       ├─ Stock.find_by_ticket(code)    → busca posición actual
       ├─ calculate_by_transaction()    → recalcula PPC
       └─ stock.update() | Stock.add() | stock.delete()  → actualiza holdings
```

### Flujo de una reversión

```
POST /transactions/<id>/revert
  └─ transaction_service.revert_transaction(id)
       ├─ Transaction.find_by_id(id)        → carga la transacción a revertir
       ├─ Stock.find_by_ticket(code)        → carga posición actual
       ├─ calculate_revert_transaction()    → invierte el cálculo de PPC
       ├─ stock.update() | stock.delete()   → actualiza o elimina holdings
       └─ Transaction.delete_by_id(id)      → elimina la transacción
```

---

## Base de datos

### Esquema

```sql
tickets (
  ticket_code  VARCHAR(50) PRIMARY KEY,  -- "AAPL", "MSFT", etc.
  name         VARCHAR(50),              -- "Apple Inc."
  ratio        INT,                      -- Multiplicador de precio (generalmente 1)
  date         BIGINT                    -- Unix timestamp
)

stock (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  ticket_code   VARCHAR(50) UNIQUE,      -- FK → tickets (una fila por ticker)
  ppc           FLOAT,                   -- Precio promedio de costo
  quantity      INT,                     -- Acciones en cartera
  weighted_date BIGINT                   -- Fecha ponderada de compras (Unix timestamp)
)

transaction (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  ticket_code     VARCHAR(50),           -- FK → tickets
  quantity        INT,                   -- Positivo=compra, negativo=venta
  unit_price      FLOAT,
  usd_quote       INT,
  date            BIGINT,
  ratio           INT,
  broker_name     VARCHAR(50),
  transaction_key INT
)
```

### Tickers pre-cargados

El archivo `DB/init/02_tickets.sql` inicializa 21 tickers:

`AAPL · AMD · BRKB · DISN · GOOGL · INTC · JPM · KO · MA · MCD · MELI · META · MSFT · NVDA · PAMP · PBR · PEP · V · VIST · WMT · YPF`

---

## Frontend

El frontend es una SPA construida con SvelteKit. Toda la lógica de UI corre en el cliente (los fetches están en `onMount`).

### Vistas

| Ruta | Descripción |
|------|-------------|
| `/dashboard` | Métricas globales (total invertido, posiciones abiertas) y dos gráficos ECharts: distribución del portfolio (donut) y PPC por ticker (barras). |
| `/stocks` | Tabla de posiciones actuales con ticker, nombre, cantidad, PPC, total invertido y fecha ponderada. |
| `/transactions` | Lista completa de transacciones con filtro por ticker, badges de compra/venta y botones de revertir/eliminar. |
| `/transactions/new` | Formulario para registrar una nueva transacción. |

### Cliente HTTP (`frontend/src/lib/api.js`)

Todas las llamadas a la API pasan por este módulo. La URL base se configura mediante la variable de entorno `PUBLIC_API_URL`.

```js
import { getStocks, getTransactions, addTransaction, revertTransaction, deleteTransaction, getTickets } from '$lib/api.js';
```

### Variables de entorno del frontend

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `PUBLIC_API_URL` | URL base de la API Flask | `http://localhost:5001` |

Configurar en `frontend/.env` para desarrollo local o en `docker-compose.yml` para Docker.

---

## Tests

Los tests corren con el módulo `unittest` de Python y requieren conexión a la base de datos.

```bash
# Correr toda la suite (desde el directorio app/)
cd app && python tests/suite_unit_test.py

# Correr un archivo específico
cd app && python -m unittest tests/unit_tests/services/test_transaction_service.py
```

> Los imports son relativos al directorio `app/`. Ejecutar los tests desde fuera de ese directorio causará errores de importación.

### Patrón Factory

Los tests usan un patrón factory para crear y limpiar datos de prueba automáticamente.

```python
class MiTest(TestBase):
    def test_algo(self):
        # Crea un objeto y lo registra para limpieza automática en tearDown
        stock = self.factory.get_new("Stock")

        # Obtiene un dict de datos sin insertar en la DB
        data = self.factory.get_data_for("Transaction")
```

`TestBase.tearDown()` elimina todos los objetos creados via factory al finalizar cada test.

### Cobertura de tests

| Módulo | Tests |
|--------|-------|
| `models/` | Stock, Transaction, Ticket, Conector |
| `services/` | StockService, TransactionService |
| `routes/` | Stocks, Transactions *(deshabilitados en la suite)* |
| `utils/` | MsgsHandler |
| `factory/` | StockFactory, TransactionFactory |
