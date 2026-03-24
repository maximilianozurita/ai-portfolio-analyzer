from src.models.bond_holding import BondHolding
from tests.factory.factory_base import FactoryBase
from datetime import datetime
import random

class BondHoldingFactory(FactoryBase):
	def __init__(self, data):
		super().__init__(data)
		self.pkg = BondHolding

	def attr_parser(self, data):
		data["bond_code"] = data.get("bond_code") or "AL30"
		data["quantity"] = data.get("quantity") or random.randint(1, 20)
		data["ppc"] = data.get("ppc") or round(random.uniform(50.0, 150.0), 4)
		data["ppc_paridad"] = data.get("ppc_paridad") or round(random.uniform(0.3, 1.2), 6)
		data["weighted_date"] = data.get("weighted_date") or int(datetime.now().timestamp())
		return data
