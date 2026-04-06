# Testing

## How to run the tests

```bash
# From the project root
python backend/tests/suite_unit_test.py
```

The runner uses Python's standard `unittest` library. No pytest or additional dependencies required.

---

## Test structure

```
backend/tests/
├── suite_unit_test.py              # Main runner — builds and runs all TestSuites
├── factory/
│   ├── factory_base.py             # FactoryBase: base class with attr_parser and init_obj
│   ├── factory_register.py         # FactoryRegister: unified registry with automatic cleanup
│   ├── stock_factory.py            # Factory for Stock objects
│   ├── transaction_factory.py      # Factory for Transaction objects
│   ├── bond_holding_factory.py     # Factory for BondHolding objects
│   └── bond_transaction_factory.py # Factory for BondTransaction objects
└── unit_tests/
    ├── base.py                     # TestBase: shared setUp/tearDown with FactoryRegister lifecycle
    ├── factory_test/
    │   ├── test_factory_stock.py
    │   └── test_factory_transaction.py
    ├── models/
    │   ├── test_stock.py
    │   ├── test_ticket.py
    │   ├── test_conector.py
    │   ├── test_transaction.py
    │   ├── test_bond_holding.py
    │   └── test_bond_transaction.py
    ├── services/
    │   ├── test_stock_service.py
    │   ├── test_transaction_service.py
    │   └── test_bond_service.py
    ├── routes/
    │   ├── test_stock_route.py      # commented out in suite
    │   └── test_transaction_route.py # commented out in suite
    └── utils/
        └── test_msg_handler.py
```

---

## Coverage

| Layer | Coverage |
|-------|----------|
| Models | Yes — all models have tests |
| Services | Yes — stock, transaction, bond |
| Utils | Yes — msgs_handler |
| Factories | Yes — stock and transaction factory tests included |
| Routes | Partial — test files exist but are commented out in the suite |

Route tests are disabled in `suite_unit_test.py`. They require a live DB connection and are not prepared to run in CI without infrastructure.

---

## Factories and the TestBase lifecycle

All test classes inherit from `TestBase` (`unit_tests/base.py`), which manages object lifecycle:

```python
class TestBase(unittest.TestCase):
    def setUp(self):
        self.factory = FactoryRegister()

    def tearDown(self):
        for obj in self.factory.created_objects:
            obj.delete()
```

`FactoryRegister` is a unified registry of all four factory types. It tracks every object created via `get_new()` and deletes them automatically in `tearDown`, keeping the test database clean between runs.

To create a test object:

```python
# Creates and persists a BondHolding with random defaults
holding = self.factory.get_new("BondHolding")

# With specific values
stock = self.factory.get_new("Stock", {"ticket_code": "GGAL", "quantity": 100, "ppc": 1250.0})

# Get only the attribute dict without persisting
data = self.factory.get_data_for("Transaction", {"ticket_code": "YPF"})
```

Supported factory names: `"Stock"`, `"Transaction"`, `"BondHolding"`, `"BondTransaction"`.

---

## Requirements to run the tests

Tests for models and services interact directly with the database. You need:

1. A running MySQL instance
2. The schema initialized (`DB/init/01_schema.sql`)
3. Environment variables configured in `.env` at the project root

---

## Adding new tests

1. Create the file at `unit_tests/<layer>/test_<module>.py`
2. Inherit from `TestBase` (for DB-backed tests) or `unittest.TestCase` (for pure unit tests)
3. Register the class in `suite_unit_test.py`:

```python
from tests.unit_tests.services.test_new_service import TestNewService

modules = [
    ...
    TestNewService,
]
```
