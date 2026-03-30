# Estructura del proyecto

## Árbol de directorios

```
ai-portfolio-analyzer/
│
├── docker-compose.yml          # Orquestación: db (MySQL 8), api (Flask), frontend (SvelteKit)
├── requirements.txt            # Dependencias Python del backend
├── .env.example                # Template de variables de entorno
├── CLAUDE.md                   # Instrucciones para Claude Code
├── README.md                   # Documentación principal
│
├── backend/
│   ├── App.py                  # Entry point Flask — registra blueprints, habilita CORS
│   │
│   ├── config/
│   │   ├── config.py           # Carga variables de entorno con python-dotenv
│   │   └── msgs_es.json        # Mensajes de error centralizados en español
│   │
│   ├── src/
│   │   ├── routes/
│   │   │   ├── routes_base.py          # Helper: create_response() — formato estándar de respuesta
│   │   │   ├── stocks.py               # Blueprint /stocks — GET, POST /import, POST /adjust
│   │   │   ├── bonds.py                # Blueprint /bond-* — holdings y transacciones
│   │   │   ├── transactions.py         # Blueprint /transactions — CRUD + revert + import
│   │   │   ├── tickets.py              # Blueprint /tickets — catálogo de tickers
│   │   │   ├── ai.py                   # Blueprint /ai — providers y análisis
│   │   │   └── market.py               # Blueprint /market — precios en tiempo real
│   │   │
│   │   ├── services/
│   │   │   ├── service_base.py         # Base de servicios (si existe lógica compartida)
│   │   │   ├── stock_service.py        # PPC, importación CSV, ajuste de posiciones
│   │   │   ├── bond_service.py         # PPC, paridad, lógica de cupón/amortización
│   │   │   ├── transaction_service.py  # Registro, reversión, recálculo de holding
│   │   │   ├── market_service.py       # Yahoo Finance + BYMA, cálculo P&L
│   │   │   ├── ai_service.py           # Prompt builder, selección de provider
│   │   │   └── ai_providers/
│   │   │       ├── base_provider.py    # Interfaz abstracta (Strategy pattern)
│   │   │       ├── gemini_provider.py  # Google Gemini
│   │   │       ├── openai_provider.py  # OpenAI GPT
│   │   │       └── openrouter_provider.py  # OpenRouter (modelos free)
│   │   │
│   │   ├── models/
│   │   │   ├── main_class.py           # Base model: validación, CRUD, query params
│   │   │   ├── conector.py             # Wrapper MySQL: execute_query, select, select_one
│   │   │   ├── stock.py                # Tabla stock: find_all, find_by_ticket, add, update
│   │   │   ├── transaction.py          # Tabla transaction
│   │   │   ├── bond_holding.py         # Tabla bond_holding
│   │   │   ├── bond_transaction.py     # Tabla bond_transaction (tipos: compra/venta/cupon/amortizacion)
│   │   │   └── ticket.py               # Tabla tickets (patrón factory con __new__)
│   │   │
│   │   └── utils/
│   │       └── msgs_handler.py         # Manejo de mensajes de error desde msgs_es.json
│   │
│   ├── scripts/
│   │   └── get_data_portfolio.py       # Script utilitario para extracción de datos
│   │
│   └── tests/
│       ├── suite_unit_test.py          # Runner principal — agrega todos los test cases
│       ├── factory/                    # Factories de datos para tests (Stock, Transaction)
│       └── unit_tests/                 # Tests por módulo (models, services, utils, routes)
│
├── frontend/
│   ├── package.json                    # SvelteKit + echarts + marked + Tailwind
│   └── src/
│       └── routes/
│           ├── +layout.svelte          # Layout global con barra de navegación
│           ├── +page.svelte            # Redirect a /dashboard
│           ├── dashboard/
│           │   └── +page.svelte        # Métricas globales + gráficos de distribución y rendimiento
│           ├── stocks/
│           │   └── +page.svelte        # Tabla de posiciones en acciones
│           ├── bonds/
│           │   └── +page.svelte        # Tabla de posiciones en bonos
│           ├── transactions/           # Historial de transacciones de acciones
│           ├── bond-transactions/      # Historial de transacciones de bonos
│           ├── operaciones/
│           │   └── nueva/              # Formulario de nueva operación (acción o bono)
│           └── analyze/
│               └── +page.svelte        # Interfaz de análisis IA: selector de provider/modelo, resultado Markdown
│
└── DB/
    ├── init/
    │   ├── 01_schema.sql               # Definición completa del schema (tablas, FK, ENUM)
    │   └── 02_tickets.sql              # Carga inicial: 50+ tickers de BYMA y mercado internacional
    ├── changes/                        # Scripts de migración
    └── scripts/
        └── update_table.py             # Script utilitario para actualizaciones de tablas
```

---

## Responsabilidades por capa

### `src/routes/`
Solo HTTP: parsear la request, llamar al servicio correspondiente, retornar `create_response()`. No debe contener lógica de negocio ni queries a la DB.

### `src/services/`
Toda la lógica de negocio vive aquí. Un servicio puede llamar a múltiples modelos y coordinar operaciones compuestas (ej. registrar una transacción y actualizar el holding en la misma operación). No hace queries directamente — delega a los modelos.

### `src/models/`
Acceso a datos exclusivamente. Cada modelo corresponde a una tabla. `MainClass` provee la validación de campos y los métodos CRUD genéricos. `ConectorBase` en `conector.py` gestiona la conexión MySQL.

### `frontend/src/routes/`
Cada directorio es una página SvelteKit. El archivo `+layout.svelte` envuelve a todas las páginas con la navegación común. La comunicación con el backend se hace directamente desde los componentes Svelte via fetch a la URL configurada en `PUBLIC_API_URL`.

---

## Convenciones

- Los archivos de routes siguen el nombre del dominio: `stocks.py`, `bonds.py`, etc.
- Los servicios tienen sufijo `_service`: `stock_service.py`
- Los modelos coinciden con el nombre de la tabla en singular: `stock.py`, `transaction.py`
- Los mensajes de error al usuario están en `config/msgs_es.json`, nunca hardcodeados en el código
