from src.models.stock import Stock
from tests.factory.factory_base import FactoryBase
from src.models.ticket import Ticket
from datetime import datetime
import random

class StockFactory(FactoryBase):
	def __init__(self, data):
		super().__init__(data)
		self.pkg = Stock

	def attr_parser(self, data):
		data["ticket_code"] = data.get("ticket_code") or Ticket.find_one().ticket_code
		data["ppc"] = data.get("ppc") or round(random.uniform(1.0,20.0), 4)
		data["quantity"] = data.get("quantity") or random.randint(1,10)
		data["weighted_date"] = data.get("weighted_date") or int(datetime.now().timestamp())
		return data
