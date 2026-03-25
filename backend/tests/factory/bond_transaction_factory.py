from src.models.bond_transaction import BondTransaction
from tests.factory.factory_base import FactoryBase
from datetime import datetime
import random

class BondTransactionFactory(FactoryBase):
	def __init__(self, data):
		super().__init__(data)
		self.pkg = BondTransaction

	def attr_parser(self, data):
		data["bond_code"] = data.get("bond_code") or "AL30"
		data["transaction_type"] = data.get("transaction_type") or "compra"
		data["quantity"] = data.get("quantity") or random.randint(1, 10)
		data["unit_price"] = data.get("unit_price") or round(random.uniform(50.0, 150.0), 4)
		data["valor_tecnico"] = data.get("valor_tecnico") or round(random.uniform(80.0, 120.0), 4)
		data["interest_currency"] = data.get("interest_currency") or "USD"
		data["amortization_currency"] = data.get("amortization_currency") or "USD"
		data["usd_quote"] = data.get("usd_quote") or random.randint(900, 1200)
		data["date"] = data.get("date") or int(datetime.now().timestamp())
		if "broker_name" in data:
			data["broker_name"] = data.get("broker_name")
		return data
