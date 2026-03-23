from src.models.transaction import Transaction
from tests.factory.factory_base import FactoryBase
from src.models.ticket import Ticket
from datetime import datetime
import random

class TransactionFactory(FactoryBase):
	def __init__(self, data):
		super().__init__(data)
		self.pkg = Transaction

	def attr_parser(self, data):
		data["ticket_code"] = data.get("ticket_code") or Ticket.find_one().ticket_code
		data["quantity"] = data.get("quantity") or random.randint(1,10)
		data["transaction_key"] = data.get("transaction_key") or random.randint(1,100)
		data["usd_quote"] = data.get("usd_quote") or random.randint(1,100)
		data["unit_price"] = data.get("unit_price") or round(random.uniform(1.0,20.0), 4)
		data["date"] = data.get("date") or int(datetime.now().timestamp())
		if "ratio" in data:
			data["ratio"] = data.get("ratio")
		if "broker_name" in data:
			data["broker_name"] = data.get("broker_name")
		return data
