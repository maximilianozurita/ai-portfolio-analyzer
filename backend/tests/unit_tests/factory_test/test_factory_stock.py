from tests.unit_tests.base import TestBase, unittest
from src.models.stock import Stock
from src.models.ticket import Ticket
import random

class TestFactoryStock(TestBase):
	def test_factory_creation(self):
		ticket_obj = Ticket("AAPL")
		data = {
			"ticket_code" : ticket_obj.ticket_code,
			"ppc" : round(random.uniform(1.0,20.0), 4),
			"quantity" : random.randint(1,10),
			"weighted_date" : random.randint(1,1000)
		}
		obj = self.factory.get_new("Stock", data)
		self.assertIsInstance(obj, Stock)
		for val in data:
			self.assertEqual(data[val], getattr(obj, val))


	def test_creation_with_default_value(self):
		obj = self.factory.get_new("Stock")
		self.assertIsInstance(obj, Stock)
		for attr in dir(obj):
			if not attr.startswith('__'):
				self.assertIsNotNone(getattr(obj, attr))


if __name__ == '__main__':
	unittest.main()
