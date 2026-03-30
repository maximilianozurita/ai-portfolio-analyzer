# Testing

## Cómo correr los tests

```bash
# Desde la raíz del proyecto
python backend/tests/suite_unit_test.py
```

El runner usa `unittest` de la librería estándar de Python. No requiere pytest ni dependencias adicionales.

---

## Estructura de tests

```
backend/tests/
├── suite_unit_test.py          # Runner principal — agrega todos los TestSuites
├── factory/
│   ├── stock_factory.py        # Factory para datos de Stock
│   └── transaction_factory.py  # Factory para datos de Transaction
└── unit_tests/
    ├── models/
    │   ├── stock_test.py
    │   ├── ticket_test.py
    │   ├── conector_test.py
    │   ├── transaction_test.py
    │   ├── bond_holding_test.py
    │   └── bond_transaction_test.py
    ├── services/
    │   ├── stock_service_test.py
    │   ├── transaction_service_test.py
    │   └── bond_service_test.py
    └── utils/
        └── msgs_handler_test.py
```

---

## Cobertura

| Capa | Cobertura |
|------|-----------|
| Modelos | Sí — todos los modelos tienen tests |
| Servicios | Sí — stock, transaction, bond |
| Utils | Sí — msgs_handler |
| Rutas | Parcial — tests comentados en suite |

Los tests de rutas están deshabilitados en el suite actual. Probablemente requieren una DB real y no están preparados para correr en CI sin infraestructura.

---

## Factories

En lugar de fixtures estáticos, se usan factories para crear objetos de prueba:

```python
# Ejemplo conceptual
stock = StockFactory.build(ticket_code="GGAL", quantity=100, ppc=1250.0)
```

Las factories están en `tests/factory/` y permiten construir objetos con valores por defecto sobreescribibles, haciendo los tests más expresivos.

---

## Requisitos para correr los tests

Los tests de modelos y servicios interactúan con la base de datos. Se necesita:

1. Una instancia de MySQL corriendo
2. El schema inicializado (`DB/init/01_schema.sql`)
3. Variables de entorno configuradas en `backend/.env`

---

## Agregar nuevos tests

1. Crear el archivo en `unit_tests/<capa>/<modulo>_test.py`
2. Heredar de `unittest.TestCase`
3. Agregar el `TestLoader` correspondiente en `suite_unit_test.py`

```python
# En suite_unit_test.py
from unit_tests.services.nuevo_service_test import NuevoServiceTest
suite.addTests(loader.loadTestsFromTestCase(NuevoServiceTest))
```
