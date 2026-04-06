# Project Structure

## Directory tree

```
ai-portfolio-analyzer/
│
├── docker-compose.yml          # Orchestration: db (MySQL 8), api (Flask), frontend (SvelteKit)
├── requirements.txt            # Python backend dependencies
├── .env.example                # Environment variables template
├── CLAUDE.md                   # Instructions for Claude Code
├── README.md                   # Main documentation
│
├── backend/
│   ├── App.py                  # Flask entry point — registers blueprints, enables CORS
│   │
│   ├── config/
│   │   ├── config.py           # Loads environment variables with python-dotenv
│   │   └── msgs_es.json        # Centralized error messages in Spanish
│   │
│   ├── src/
│   │   ├── routes/
│   │   │   ├── routes_base.py          # Helper: create_response() — standard response format
│   │   │   ├── stocks.py               # Blueprint /stocks — GET, POST /import, POST /adjust
│   │   │   ├── bonds.py                # Blueprint /bond-* — holdings and transactions
│   │   │   ├── transactions.py         # Blueprint /transactions — CRUD + revert + import
│   │   │   ├── tickets.py              # Blueprint /tickets — ticker catalog
│   │   │   ├── ai.py                   # Blueprint /ai — providers and analysis
│   │   │   └── market.py               # Blueprint /market — real-time prices
│   │   │
│   │   ├── services/
│   │   │   ├── service_base.py         # Service base (shared logic)
│   │   │   ├── stock_service.py        # PPC, CSV import, position adjustment
│   │   │   ├── bond_service.py         # PPC, parity, coupon/amortization logic
│   │   │   ├── transaction_service.py  # Recording, reverting, holding recalculation
│   │   │   ├── market_service.py       # Yahoo Finance + BYMA, P&L calculation
│   │   │   ├── ai_service.py           # Prompt builder, provider selection
│   │   │   └── ai_providers/
│   │   │       ├── base_provider.py    # Abstract interface (Strategy pattern)
│   │   │       ├── gemini_provider.py  # Google Gemini
│   │   │       ├── openai_provider.py  # OpenAI GPT
│   │   │       └── openrouter_provider.py  # OpenRouter (free models)
│   │   │
│   │   ├── models/
│   │   │   ├── main_class.py           # Base model: validation, CRUD, query params
│   │   │   ├── conector.py             # MySQL wrapper: execute_query, select, select_one
│   │   │   ├── stock.py                # Table stock: find_all, find_by_ticket, add, update
│   │   │   ├── transaction.py          # Table transaction
│   │   │   ├── bond_holding.py         # Table bond_holding
│   │   │   ├── bond_transaction.py     # Table bond_transaction (types: compra/venta/cupon/amortizacion)
│   │   │   └── ticket.py               # Table tickets (factory pattern with __new__)
│   │   │
│   │   └── utils/
│   │       └── msgs_handler.py         # Error message handling from msgs_es.json
│   │
│   ├── scripts/
│   │   └── get_data_portfolio.py       # Utility script for data extraction
│   │
│   └── tests/
│       ├── suite_unit_test.py          # Main runner — builds and runs all test cases
│       ├── factory/
│       │   ├── factory_base.py         # FactoryBase: base class with init_obj and attr_parser
│       │   ├── factory_register.py     # FactoryRegister: unified registry with automatic cleanup
│       │   ├── stock_factory.py        # Factory for Stock
│       │   ├── transaction_factory.py  # Factory for Transaction
│       │   ├── bond_holding_factory.py # Factory for BondHolding
│       │   └── bond_transaction_factory.py  # Factory for BondTransaction
│       └── unit_tests/
│           ├── base.py                 # TestBase: shared setUp/tearDown with FactoryRegister
│           ├── factory_test/           # Factory tests
│           ├── models/                 # Per-model tests (test_stock.py, test_bond_holding.py, etc.)
│           ├── services/               # Service tests (test_stock_service.py, etc.)
│           ├── routes/                 # Route tests (disabled in suite)
│           └── utils/                  # Utility tests
│
├── frontend/
│   ├── package.json                    # SvelteKit + echarts + marked + Tailwind
│   └── src/
│       ├── lib/
│       │   ├── api.js                  # All backend calls (fetch wrappers)
│       │   ├── stores.js               # Svelte stores for market price caching
│       │   └── components/
│       │       ├── StockTable.svelte
│       │       ├── TransactionTable.svelte
│       │       ├── BondHoldingTable.svelte
│       │       ├── BondTransactionTable.svelte
│       │       ├── MetricCard.svelte
│       │       └── charts/
│       │           ├── DistributionChart.svelte
│       │           ├── BondDistributionChart.svelte
│       │           ├── CombinedDistributionChart.svelte
│       │           ├── PpcBarChart.svelte
│       │           ├── BondPpcParidadChart.svelte
│       │           └── RendimientoChart.svelte
│       └── routes/
│           ├── +layout.svelte          # Global layout with navigation bar
│           ├── +page.svelte            # Redirect to /dashboard
│           ├── dashboard/
│           │   └── +page.svelte        # Global metrics + distribution and performance charts
│           ├── stocks/
│           │   └── +page.svelte        # Equity positions table
│           ├── bonds/
│           │   └── +page.svelte        # Bond positions table
│           ├── transactions/
│           │   ├── +page.svelte        # Stock transaction history
│           │   └── new/
│           │       └── +page.svelte    # New stock transaction form + CSV import
│           ├── bond-transactions/
│           │   └── new/
│           │       └── +page.svelte    # New bond transaction form
│           ├── operaciones/
│           │   └── nueva/
│           │       └── +page.svelte    # New operation form (stock or bond)
│           └── analyze/
│               └── +page.svelte        # AI analysis interface: provider/model selector, Markdown result
│
└── DB/
    ├── init/
    │   ├── 01_schema.sql               # Full schema definition (tables, FK, ENUM)
    │   └── 02_tickets.sql              # Seed data: 50+ BYMA and international tickers
    ├── changes/                        # Migration scripts
    ├── staticTables/
    │   └── tabla_tickets.json          # Static ticker catalog data
    └── scripts/
        └── update_table.py             # Utility script for table updates
```

---

## Layer responsibilities

### `src/routes/`
HTTP only: parse the request, call the corresponding service, return `create_response()`. Must not contain business logic or direct DB queries.

### `src/services/`
All business logic lives here. A service can call multiple models and coordinate composite operations (e.g. recording a transaction and updating the holding in the same operation). Does not query directly — delegates to models.

### `src/models/`
Data access exclusively. Each model corresponds to a table. `MainClass` provides field validation and generic CRUD methods. `ConectorBase` in `conector.py` manages the MySQL connection.

### `frontend/src/lib/`
Code shared across pages. `api.js` centralizes all HTTP calls to the backend — no page does `fetch` directly. `stores.js` keeps market prices cached in Svelte stores to avoid redundant calls within the same session.

### `frontend/src/routes/`
Each directory is a SvelteKit page. `+layout.svelte` wraps all pages with common navigation. Pages consume `api.js` and stores from `lib/`, and delegate table and chart rendering to components in `lib/components/`.

---

## Conventions

- Route files follow the domain name: `stocks.py`, `bonds.py`, etc.
- Services have a `_service` suffix: `stock_service.py`
- Models match the table name in singular: `stock.py`, `transaction.py`
- Test files have a `test_` prefix: `test_stock.py`, `test_bond_service.py`
- User-facing error messages are in `config/msgs_es.json`, never hardcoded in the source
