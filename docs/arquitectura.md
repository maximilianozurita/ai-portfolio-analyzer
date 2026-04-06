# Architecture

## Overview

3-layer system with strict separation of responsibilities:

```
[SvelteKit Frontend] ←→ REST API ←→ [Flask Backend] ←→ [MySQL]
                                          ↓
                               [Yahoo Finance / BYMA API]
                               [Gemini / OpenAI / OpenRouter]
```

---

## Backend — Flask (3 layers)

### Routes layer (`src/routes/`)

Flask Blueprints, one per domain. Their only responsibility is handling the HTTP request and returning a response. They contain no business logic.

All endpoints use `create_response()` from `routes_base.py` to produce standardized responses:

```json
{
  "status": "ok" | "error",
  "message": "...",
  "data": { ... }
}
```

Available blueprints: `stocks`, `bonds`, `transactions`, `tickets`, `ai`, `market`.

### Services layer (`src/services/`)

Contains all business logic. Each service coordinates models and computes derived state:

- **StockService**: equity position management, weighted PPC calculation, CSV import
- **BondService**: bond management, support for `compra`, `venta`, `cupon`, `amortizacion` types, PPC and parity recalculation
- **TransactionService**: recording and reverting stock transactions with automatic holding update
- **MarketService**: price fetching from Yahoo Finance and BYMA; P&L calculation
- **AiService**: structured prompt builder and delegation to the selected provider

### Models layer (`src/models/`)

Pure data access. `MainClass` is the shared base:

- Validates data against the `_attrs` schema defined in each subclass
- Provides generic CRUD methods: `add()`, `update()`, `delete()`
- `ConectorBase` manages the MySQL connection and exposes `execute_query()`, `select()`, `select_one()`

---

## Main data flows

### Recording a stock transaction

```
PUT /transactions
  → TransactionRoute
    → TransactionService.add_transaction(data)
      → Transaction.add()          # INSERT into transaction table
      → Stock.find_by_ticket()     # read current holding
      → calculate_by_transaction() # recalculate PPC and quantity
      → Stock.update()             # UPDATE holding
```

### Updating market prices

```
GET /market/prices/stocks
  → MarketRoute
    → MarketService.get_stock_prices()
      → Stock.find_all()            # tickers in portfolio
      → yfinance.Tickers()          # Yahoo Finance prices via fast_info
      → calculate P&L (pnl_pct, pnl_ars, current_value, invested_value)
      → return metrics
```

### AI analysis

```
POST /ai/analyze  { provider, model, market_prices_stocks?, market_prices_bonds? }
  → AiRoute
    → AiService.analyze_portfolio(provider, model, market_stocks, market_bonds)
      → Stock.find_all() + BondHolding.find_all()  # current positions
      → _build_prompt()             # builds prompt with portfolio data and optional prices
      → ProviderX.analyze(prompt, model)   # Gemini / OpenAI / OpenRouter
      → return structured Markdown (7 sections)
```

The prompt includes market prices and P&L if the client sends them in the request body. The frontend passes prices already loaded in the stores, avoiding a second call to Yahoo Finance / BYMA from the backend.

---

## AI Providers — Strategy Pattern

`BaseProvider` defines the interface:

```python
class BaseProvider:
    def analyze(self, prompt: str, model: str) -> str: ...
    def get_models(self) -> list: ...
    def is_available(self) -> bool: ...
```

Implementations: `GeminiProvider`, `OpenAIProvider`, `OpenRouterProvider`.

The client (`AiService`) selects the provider at runtime based on the received parameter. Adding a new provider does not require modifying the service or routes — only implement the interface and register it in the `PROVIDERS` dictionary in `ai_service.py`.

Models configured per provider:

| Provider | Available models |
|----------|-----------------|
| Gemini | Gemini 2.5 Flash, 2.0 Flash, 1.5 Pro |
| OpenAI | GPT-4o, GPT-4o Mini, GPT-4 Turbo |
| OpenRouter | Llama 3.3 70B (free), DeepSeek R1 (free), Mistral 7B (free) |

`OpenRouterProvider` uses the Python `openai` client pointing to `https://openrouter.ai/api/v1`, since OpenRouter exposes an OpenAI-compatible API.

---

## Bond price fetching

Dual strategy with per-ticker fallback:

1. **First**: BYMA Open Data — POST to `open.bymadata.com.ar` with `T2: true`. Covers the official Argentine market with ~20 min delay.
2. **Fallback**: Yahoo Finance — only for bond tickers that BYMA did not return.

BYMA prices come in ARS per 100 face value, so the service normalizes them by dividing by 100 before returning.

---

## Database

MySQL 8.0. Main tables:

| Table | Purpose |
|-------|---------|
| `tickets` | Ticker catalog with names (50+ pre-loaded symbols) |
| `stock` | Current holding per ticker (consolidated position) |
| `transaction` | Stock transaction history |
| `bond_holding` | Current bond holdings |
| `bond_transaction` | Bond transaction history |
| `tokens` | OAuth tokens (schema present, no active implementation) |

Dates are stored as UNIX timestamps (`BIGINT`). PPC is stored as `FLOAT` and recalculated in software when recording or reverting transactions (no DB triggers).

---

## Frontend — SvelteKit

### Routing

File-based routing under `src/routes/`:

| Route | Purpose |
|-------|---------|
| `/dashboard` | Main view with global metrics and charts |
| `/stocks` | Equity positions |
| `/bonds` | Fixed-income positions |
| `/transactions` | Stock transaction history |
| `/transactions/new` | New stock transaction form + CSV import |
| `/bond-transactions/new` | New bond transaction form |
| `/operaciones/nueva` | New operation form (stock or bond) |
| `/analyze` | AI analysis interface |

### `src/lib/` layer

Code shared across pages:

- **`api.js`**: all `fetch` calls to the backend are centralized here. No page accesses the API URL directly.
- **`stores.js`**: Svelte stores for market price caching (`marketPricesStocksStore`, `marketPricesBondsStore`). Data loaded on one page persists to others within the same session, including the AI analysis page which passes them into the prompt.
- **`components/`**: reusable tables (`StockTable`, `TransactionTable`, `BondHoldingTable`, `BondTransactionTable`) and ECharts charts (`DistributionChart`, `RendimientoChart`, `BondPpcParidadChart`, etc.).

Charts use Apache ECharts 5 (pie charts for distribution, bar charts for return per ticker). The AI analysis result is rendered with `marked` as Markdown.
