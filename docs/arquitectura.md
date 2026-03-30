# Arquitectura

## Visión general

Sistema de 3 capas con separación estricta de responsabilidades:

```
[SvelteKit Frontend] ←→ REST API ←→ [Flask Backend] ←→ [MySQL]
                                          ↓
                               [Yahoo Finance / BYMA API]
                               [Gemini / OpenAI / OpenRouter]
```

---

## Backend — Flask (3 capas)

### Capa de rutas (`src/routes/`)

Flask Blueprints, uno por dominio. Su única responsabilidad es manejar la request HTTP y devolver una response. No contienen lógica de negocio.

Todos los endpoints usan `create_response()` de `routes_base.py` para generar respuestas estandarizadas:

```json
{
  "status": "ok" | "error",
  "message": "...",
  "data": { ... }
}
```

Blueprints disponibles: `stocks`, `bonds`, `transactions`, `tickets`, `ai`, `market`.

### Capa de servicios (`src/services/`)

Contiene toda la lógica de negocio. Cada servicio coordina modelos y calcula el estado derivado:

- **StockService**: gestión de posiciones de acciones, cálculo de PPC ponderado, importación CSV
- **BondService**: gestión de bonos, soporte para `compra`, `venta`, `cupon`, `amortizacion`, recálculo de PPC y paridad
- **TransactionService**: registro y reversión de transacciones de acciones con actualización automática del holding
- **MarketService**: obtención de precios desde Yahoo Finance y BYMA; cálculo de P&L
- **AiService**: construcción del prompt estructurado y delegación al provider seleccionado

### Capa de modelos (`src/models/`)

Acceso a datos puro. `MainClass` es la base común:

- Valida los datos contra el esquema `_attrs` definido en cada subclase
- Provee métodos CRUD genéricos: `add()`, `update()`, `delete()`
- `ConectorBase` gestiona la conexión MySQL y expone `execute_query()`, `select()`, `select_one()`

---

## Flujo de datos principal

### Registro de una transacción de acción

```
POST /transactions
  → TransactionRoute
    → TransactionService.add_transaction(data)
      → Transaction.add()          # INSERT en tabla transaction
      → Stock.find_by_ticket()     # leer holding actual
      → calculate_by_transaction() # recalcular PPC y quantity
      → Stock.update()             # UPDATE holding
```

### Actualización de precios de mercado

```
GET /market/prices/stocks
  → MarketRoute
    → MarketService.get_stock_prices()
      → Stock.find_all()            # tickers en portfolio
      → yfinance.download()         # precios Yahoo Finance
      → calcular P&L (ganancia %, valor actual)
      → retornar métricas
```

### Análisis de IA

```
POST /ai/analyze  { provider, model }
  → AiRoute
    → AiService.analyze_portfolio(provider, model)
      → _build_prompt()             # fetch portfolio completo + formato
      → ProviderX.analyze(prompt)   # Gemini / OpenAI / OpenRouter
      → retornar Markdown estructurado
```

---

## Providers de IA — Patrón Strategy

`BaseProvider` define la interfaz:

```python
class BaseProvider:
    def analyze(self, prompt: str) -> str: ...
    def get_models(self) -> list: ...
    def is_available(self) -> bool: ...
```

Implementaciones: `GeminiProvider`, `OpenAIProvider`, `OpenRouterProvider`.

El cliente (`AiService`) selecciona el provider en tiempo de ejecución según el parámetro recibido. Agregar un nuevo provider no requiere modificar el servicio, solo implementar la interfaz.

Modelos configurados por provider:

| Provider | Modelos disponibles |
|----------|---------------------|
| Gemini | Gemini 2.5 Flash, 2.0 Flash, 1.5 Pro |
| OpenAI | GPT-4o, GPT-4o Mini, GPT-4 Turbo |
| OpenRouter | Llama 3.3 70B, DeepSeek R1, Mistral 7B |

---

## Obtención de precios de bonos

Estrategia dual con fallback:

1. **Primero**: BYMA Open Data (datos con ~20 min de delay pero oficiales)
2. **Fallback**: Yahoo Finance (si BYMA no responde o el ticker no está disponible)

Los tickers argentinos en Yahoo Finance llevan el sufijo `.BA` (ej. `GGAL.BA`).

---

## Base de datos

MySQL 8.0. Tablas principales:

| Tabla | Propósito |
|-------|-----------|
| `tickets` | Catálogo de tickers con nombre (50+ símbolos pre-cargados) |
| `stock` | Holding actual por ticker (posición consolidada) |
| `transaction` | Historial de transacciones de acciones |
| `bond_holding` | Holding actual de bonos |
| `bond_transaction` | Historial de transacciones de bonos |
| `tokens` | Tokens de autenticación (OAuth) |

Las fechas se almacenan como timestamps UNIX (`BIGINT`). El PPC se almacena como `FLOAT` y se recalcula por software al revertir transacciones (no hay triggers en la DB).

---

## Frontend — SvelteKit

Routing file-based bajo `src/routes/`:

| Ruta | Función |
|------|---------|
| `/dashboard` | Vista principal con métricas globales y gráficos |
| `/stocks` | Posiciones de renta variable |
| `/bonds` | Posiciones de renta fija |
| `/transactions` | Historial de transacciones de acciones |
| `/bond-transactions` | Historial de transacciones de bonos |
| `/operaciones/nueva` | Formulario de nueva operación |
| `/analyze` | Interfaz de análisis con IA |

Los precios de mercado se cachean en Svelte stores para evitar llamadas redundantes dentro de la misma sesión. Los gráficos usan Apache ECharts 5 (pie charts para distribución, barras para rendimiento por ticker). El resultado del análisis IA se renderiza con `marked` como Markdown.
