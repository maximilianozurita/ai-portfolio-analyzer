# API Reference

Base URL: `http://localhost:5001`

Todas las respuestas siguen el formato:
```json
{
  "status": "ok" | "error",
  "message": "descripción",
  "data": { ... }
}
```

---

## Tickets

### `GET /tickets`
Lista todos los tickers disponibles en el catálogo.

**Response**
```json
{
  "status": "ok",
  "data": [
    { "ticket_code": "GGAL", "name": "Grupo Financiero Galicia" },
    { "ticket_code": "YPF", "name": "YPF S.A." }
  ]
}
```

---

## Acciones (Renta Variable)

### `GET /stocks`
Lista todas las posiciones de renta variable (holdings consolidados).

**Response**
```json
{
  "status": "ok",
  "data": [
    {
      "ticket_code": "GGAL",
      "name": "Grupo Financiero Galicia",
      "quantity": 100,
      "ppc": 1250.50,
      "weighted_date": 1700000000
    }
  ]
}
```

### `POST /stocks/import`
Importa posiciones de acciones desde un archivo CSV.

**Request**: `multipart/form-data` con campo `file`

**Formato CSV**:
```csv
ticket_code,quantity,ppc,weighted_date
GGAL,100,1250.50,1700000000
```

### `POST /stocks/<ticket_code>/adjust`
Ajusta la cantidad y PPC de una posición por un factor multiplicador.

**Request body**:
```json
{ "factor": 2.0 }
```

---

## Transacciones de Acciones

### `GET /transactions`
Lista todas las transacciones. Acepta query param `ticket_code` para filtrar por ticker.

**Response**
```json
{
  "status": "ok",
  "data": [
    {
      "id": 1,
      "ticket_code": "GGAL",
      "quantity": 100,
      "unit_price": 1200.00,
      "usd_quote": 1000,
      "date": 1700000000,
      "transaction_key": null,
      "broker_name": "IOL"
    }
  ]
}
```

### `PUT /transactions`
Registra una nueva transacción de acción y actualiza el holding automáticamente.

**Request body**:
```json
{
  "ticket_code": "GGAL",
  "quantity": 100,
  "unit_price": 1200.00,
  "usd_quote": 1000,
  "date": 1700000000,
  "broker_name": "IOL"
}
```

### `POST /transactions/import`
Importa transacciones en bulk desde CSV.

**Formato CSV**:
```csv
ticket_code,quantity,unit_price,usd_quote,date
GGAL,100,1200.00,1000,1700000000
```

### `POST /transactions/<id>/delete`
Elimina una transacción por ID.

### `POST /transactions/<id>/revert`
Revierte una transacción y recalcula el holding al estado anterior.

---

## Bonos (Renta Fija)

### `GET /bond-holdings`
Lista todas las posiciones de bonos.

**Response**
```json
{
  "status": "ok",
  "data": [
    {
      "id": 1,
      "bond_code": "AL30",
      "quantity": 1000,
      "ppc": 55.20,
      "ppc_paridad": 0.52,
      "weighted_date": 1700000000
    }
  ]
}
```

### `GET /bond-transactions`
Lista transacciones de bonos. Acepta query param `bond_code` para filtrar.

### `PUT /bond-transactions`
Registra una nueva transacción de bono y recalcula el holding.

**Request body**:
```json
{
  "bond_code": "AL30",
  "transaction_type": "compra",
  "quantity": 1000,
  "unit_price": 55.20,
  "valor_tecnico": 100.00,
  "interest_currency": "USD",
  "amortization_currency": "USD",
  "usd_quote": 1000,
  "date": 1700000000,
  "broker_name": "IOL"
}
```

Tipos de transacción válidos: `compra`, `venta`, `cupon`, `amortizacion`

### `POST /bond-holdings/import`
Importa posiciones de bonos desde CSV.

**Formato CSV**:
```csv
bond_code,quantity,ppc,ppc_paridad,weighted_date
AL30,1000,55.20,0.52,1700000000
```

### `POST /bond-transactions/<id>/delete`
Elimina una transacción de bono por ID.

### `POST /bond-transactions/<id>/revert`
Revierte una transacción de bono y recalcula el holding.

---

## Precios de Mercado

### `GET /market/prices/stocks`
Obtiene precios actuales de las acciones en cartera desde Yahoo Finance. Retorna métricas de P&L.

**Response**
```json
{
  "status": "ok",
  "data": {
    "GGAL": {
      "current_price": 1350.00,
      "ppc": 1250.50,
      "gain_pct": 7.95,
      "current_value": 135000.00
    }
  }
}
```

### `GET /market/prices/bonds`
Obtiene precios de bonos. Intenta primero BYMA Open Data; si falla, usa Yahoo Finance como fallback.

---

## Análisis de IA

### `GET /ai/providers`
Lista los providers de IA disponibles según las API keys configuradas.

**Response**
```json
{
  "status": "ok",
  "data": [
    {
      "id": "gemini",
      "name": "Google Gemini",
      "models": [
        { "id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash" },
        { "id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash" }
      ]
    }
  ]
}
```

### `POST /ai/analyze`
Analiza el portfolio completo con el provider y modelo especificados. Retorna un análisis en formato Markdown con 7 secciones estructuradas.

**Request body**:
```json
{
  "provider": "gemini",
  "model": "gemini-2.5-flash"
}
```

**Response**
```json
{
  "status": "ok",
  "data": {
    "analysis": "# Análisis de Portfolio\n\n## 1. Resumen ejecutivo\n..."
  }
}
```

El análisis incluye el estado completo del portfolio (posiciones, P&L, distribución) como contexto para el modelo.

---

## Manejo de errores

Los errores retornan HTTP 200 con `status: "error"`:

```json
{
  "status": "error",
  "message": "Ticket no encontrado",
  "data": null
}
```

Los mensajes de error están centralizados en `backend/config/msgs_es.json` y están en español.
