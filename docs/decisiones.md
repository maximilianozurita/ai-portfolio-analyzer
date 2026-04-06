# Technical decisions

## Stack

### Flask over FastAPI or Django

Flask allows a minimal and explicit architecture. For a system of this size (6 domains, no complex auth, no async workers) neither Django's complexity nor FastAPI's async model overhead is justified. Flask blueprints map directly to the layered model used.

### MySQL over PostgreSQL or ORM

`mysql-connector-python` is used directly without an ORM. The advantages:
- Explicit and predictable queries (no ORM magic)
- Full control over data types (UNIX timestamps as BIGINT, etc.)
- No abstraction overhead for a relatively simple schema

The trade-off is more boilerplate in models, mitigated by `MainClass` which provides generic CRUD.

### SvelteKit

SvelteKit combines the UI framework (Svelte) with the router. For a SPA with multiple views and reactive state, it is lighter than React + React Router and has better DX than Vue for projects without a dedicated frontend team.

---

## Data architecture

### UNIX timestamps instead of DATE/DATETIME columns

Dates are stored as `BIGINT` (UNIX timestamp). This avoids timezone issues between the Python backend, MySQL DB, and JavaScript frontend, all of which handle UNIX timestamps natively.

### PPC recalculated in software, not via triggers

The weighted average cost (PPC) is recalculated in `TransactionService.calculate_by_transaction()` and `BondService.calculate_by_bond_transaction()` when recording or reverting transactions. There are no DB triggers.

**Why**: Triggers are hard to test and debug. Having the logic in Python allows direct unit tests and full traceability in the code.

### `bond_holding` and `bond_transaction` as separate tables

Bonds have more complex logic than stocks (coupons, amortizations, parity). Separating the holding from the transaction history allows recalculating the current state by replaying transactions in order, which makes reverting (`revert`) possible.

---

## AI providers — Strategy pattern

The three providers (Gemini, OpenAI, OpenRouter) implement the same `BaseProvider` interface. `AiService` does not know which provider it is using: it receives a `provider` string and resolves it at runtime.

**Benefit**: adding a new provider (e.g. Anthropic, Cohere) only requires creating a new file in `ai_providers/` without touching the service or routes.

**OpenRouter as a free alternative**: OpenRouter acts as a proxy for multiple models. Including Llama, DeepSeek, and Mistral as free options allows using the analysis feature at no cost.

---

## Bond prices: BYMA first, Yahoo Finance as fallback

BYMA is the official data source for the Argentine market, but has ~20 minutes of delay and the API is not always available. Yahoo Finance has better uptime but Argentine bond data can be inconsistent.

The fallback strategy guarantees availability without sacrificing accuracy when BYMA is accessible.

---

## Error messages in Spanish

User-facing error messages are centralized in `config/msgs_es.json`. The domain is the Argentine capital market and users are local investors. Keeping messages in a JSON file (rather than strings in the code) allows reviewing and updating them without searching through source files.

---

## Tests with factories

Tests use factories (`tests/factory/`) to create test data. This avoids static fixtures that go stale and makes tests more readable by describing the data being constructed, not just its value.

Route tests are partially commented out, likely because they require a live DB and are not integrated into CI.

---

## `tokens` table

There is a `tokens` table in the schema with OAuth fields (access_token, refresh_token, expires). No user authentication is implemented in the current code. The table may be a remnant of a planned or in-progress implementation.
