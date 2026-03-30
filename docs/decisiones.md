# Decisiones técnicas

## Stack

### Flask sobre FastAPI o Django

Flask permite una arquitectura mínima y explícita. Para un sistema de este tamaño (6 dominios, sin auth compleja, sin workers async) no justifica la complejidad de Django ni el overhead de aprender el modelo async de FastAPI. Los blueprints de Flask mapean directamente al modelo de capas usado.

### MySQL sobre PostgreSQL u ORM

Se usa `mysql-connector-python` directamente sin ORM. Las ventajas:
- Queries explícitas y predecibles (sin magia de ORM)
- Control total sobre los tipos de datos (timestamps UNIX como BIGINT, etc.)
- Sin overhead de abstracción para un schema relativamente simple

La desventaja es más código repetitivo en los modelos, mitigado por `MainClass` que provee CRUD genérico.

### SvelteKit

SvelteKit combina el framework de UI (Svelte) con el router. Para una SPA con múltiples vistas y estado reactivo, es más liviano que React + React Router y tiene mejor DX que Vue para proyectos sin equipo de frontend dedicado.

---

## Arquitectura de datos

### Timestamps UNIX en lugar de columnas DATE/DATETIME

Las fechas se almacenan como `BIGINT` (timestamp UNIX). Evita problemas de timezone entre el backend Python, la DB MySQL y el frontend JavaScript, que todos manejan timestamps UNIX nativamente.

### PPC recalculado por software, no por triggers

El precio promedio de compra (PPC) se recalcula en `TransactionService.calculate_by_transaction()` y `BondService.calculate_by_bond_transaction()` al registrar o revertir transacciones. No hay triggers en la DB.

**Por qué**: Los triggers son difíciles de testear y debuggear. Tener la lógica en Python permite unit tests directos y trazabilidad completa en el código.

### `bond_holding` y `bond_transaction` como tablas separadas

Los bonos tienen lógica más compleja que las acciones (cupones, amortizaciones, paridad). Separar el holding del historial de transacciones permite recalcular el estado actual replicando las transacciones en orden, lo que hace posible la reversión (`revert`).

---

## Providers de IA — patrón Strategy

Los tres providers (Gemini, OpenAI, OpenRouter) implementan la misma interfaz `BaseProvider`. El servicio `AiService` no sabe qué provider está usando: recibe un string `provider` y lo resuelve en tiempo de ejecución.

**Beneficio**: agregar un nuevo provider (ej. Anthropic, Cohere) solo requiere crear un archivo nuevo en `ai_providers/` sin tocar el servicio ni las rutas.

**OpenRouter como alternativa free**: OpenRouter actúa como proxy de múltiples modelos. Incluir Llama, DeepSeek y Mistral como opciones gratuitas permite usar la funcionalidad de análisis sin costo.

---

## Precios de bonos: BYMA primero, Yahoo Finance como fallback

BYMA es la fuente oficial de datos para el mercado argentino, pero tiene ~20 minutos de delay y la API puede no estar siempre disponible. Yahoo Finance tiene mejor uptime pero los datos de bonos argentinos pueden ser inconsistentes.

La estrategia de fallback garantiza disponibilidad sin sacrificar precisión cuando BYMA está accesible.

---

## Manejo de errores en español

Los mensajes de error al usuario están centralizados en `config/msgs_es.json`. El dominio es el mercado de capitales argentino y los usuarios son inversores locales. Tener los mensajes en un archivo JSON (en lugar de strings en el código) permite revisarlos y actualizarlos sin buscar en el código fuente.

---

## Tests con factories

Los tests usan factories (`tests/factory/`) para crear datos de prueba. Esto evita fixtures estáticos que se desactualizan y hace que los tests sean más legibles al describir el dato que se está construyendo, no solo su valor.

Los tests de rutas están parcialmente comentados, probablemente porque requieren una DB real y no están integrados en el CI.

---

## Tabla `tokens`

Existe una tabla `tokens` en el schema con campos de OAuth (access_token, refresh_token, expires). En el código actual no hay autenticación de usuarios implementada. La tabla puede ser un vestigio de una implementación planificada o en progreso.

> ⚠️ No verificado en el código fuente — no se encontraron referencias activas a esta tabla en los servicios o rutas actuales.
