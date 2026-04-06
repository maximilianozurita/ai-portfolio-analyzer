# API Reference

Base URL: `http://localhost:5001`

All responses follow this format:
```json
{
  "status": "ok" | "error",
  "message": "description",
  "data": { ... }
}
```

---

## Tickets

### `GET /tickets`
List all tickers available in the catalog.

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

## Stocks (Equity)

### `GET /stocks`
List all equity holdings (consolidated positions).

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
Import equity positions from a CSV file.

**Request**: `multipart/form-data` with field `file`

**CSV format**:
```csv
ticket_code,quantity,ppc,weighted_date
GGAL,100,1250.50,1700000000
```

### `POST /stocks/<ticket_code>/adjust`
Adjust the quantity and PPC of a position by a multiplier factor (used for stock splits or corporate actions).

**Request body**:
```json
{ "factor": 2.0 }
```

---

## Stock Transactions

### `GET /transactions`
List all transactions. Accepts query params:
- `ticket_code` — filter by ticker
- `id` — retrieve a single transaction by ID (returns 404 if not found)

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
Record a new stock transaction and automatically update the holding.

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
Import transactions in bulk from CSV.

**CSV format**:
```csv
ticket_code,quantity,unit_price,usd_quote,date
GGAL,100,1200.00,1000,1700000000
```

### `POST /transactions/<id>/delete`
Delete a transaction by ID.

### `POST /transactions/<id>/revert`
Revert a transaction and recalculate the holding to its prior state.

---

## Bonds (Fixed Income)

### `GET /bond-holdings`
List all bond positions.

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
List bond transactions. Accepts query params:
- `bond_code` — filter by bond code
- `id` — retrieve a single transaction by ID (returns 404 if not found)

### `PUT /bond-transactions`
Record a new bond transaction and recalculate the holding.

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

Valid `transaction_type` values: `compra`, `venta`, `cupon`, `amortizacion`

Valid `interest_currency` and `amortization_currency` values: `ARS`, `USD`

### `POST /bond-holdings/import`
Import bond positions from CSV.

**CSV format**:
```csv
bond_code,quantity,ppc,ppc_paridad,weighted_date
AL30,1000,55.20,0.52,1700000000
```

### `POST /bond-transactions/<id>/delete`
Delete a bond transaction by ID.

### `POST /bond-transactions/<id>/revert`
Revert a bond transaction and recalculate the holding.

---

## Market Prices

### `GET /market/prices/stocks`
Get current prices for all open equity positions from Yahoo Finance. Returns P&L metrics per ticker.

**Response**
```json
{
  "status": "ok",
  "data": {
    "GGAL": {
      "price": 1350.00,
      "currency": "ARS",
      "pnl_pct": 7.95,
      "current_value": 135000.00,
      "invested_value": 125050.00,
      "pnl_ars": 9950.00
    }
  }
}
```

If `price` is `null` (Yahoo Finance returned no data), only `price` and `currency` are present.

### `GET /market/prices/bonds`
Get current prices for all open bond positions. Tries BYMA Open Data first; falls back to Yahoo Finance for any bond code not found in BYMA.

Bond prices from BYMA are raw ARS values per 100 face value. The service normalizes them by dividing by 100 before returning.

**Response** — same structure as stocks, keyed by `bond_code`.

---

## AI Analysis

### `GET /ai/providers`
List available AI providers based on which API keys are configured.

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
        { "id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash" },
        { "id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro" }
      ]
    }
  ]
}
```

A provider only appears if its API key is set and non-empty.

### `POST /ai/analyze`
Analyze the full portfolio with the specified provider and model. Returns a Markdown report with 7 structured sections.

**Request body**:
```json
{
  "provider": "gemini",
  "model": "gemini-2.5-flash",
  "market_prices_stocks": { "GGAL": { "price": 1350.00, "pnl_pct": 7.95 } },
  "market_prices_bonds": { "AL30": { "price": 0.5520, "pnl_pct": -2.10 } }
}
```

`market_prices_stocks` and `market_prices_bonds` are optional. When provided (typically by passing the data already loaded in the frontend), the prompt includes current prices and P&L figures for each position. When omitted, the analysis is based on holdings only.

**Response**
```json
{
  "status": "ok",
  "data": {
    "analysis": "# Portfolio Analysis\n\n## Executive Summary\n..."
  }
}
```

The report always contains these 7 sections:
1. Executive Summary
2. Analysis by Asset Class
3. Diversification and Concentration
4. Performance
5. Identified Risks
6. Argentine Market Context
7. Conclusions and Considerations

---

## Error handling

Errors return HTTP 200 with `status: "error"` (except 404 responses on single-resource lookups):

```json
{
  "status": "error",
  "message": "Ticket no encontrado",
  "data": null
}
```

Error messages are centralized in `backend/config/msgs_es.json` and are in Spanish.
