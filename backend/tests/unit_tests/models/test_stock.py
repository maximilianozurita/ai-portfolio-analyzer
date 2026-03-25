from src.models.stock import Stock
from src.models.ticket import Ticket
from tests.unit_tests.base import TestBase, unittest
import random

class TestStock(TestBase):
	def test_add_stock(self):
		ticket_obj = Ticket("AAPL")
		data = {
			"ticket_code" : ticket_obj.ticket_code,
			"ppc" : round(random.uniform(1.0,20.0), 4),
			"quantity" : random.randint(1,10),
			"weighted_date" : random.randint(1,1000)
		}
		(stock, errors) = Stock.add(data)
		self.assertIsNone(errors)
		self.assertIsInstance(stock, Stock)
		self.factory.delete_on_cleanup(stock)
		for val in data: 
			self.assertEqual(data[val], getattr(stock, val))
		objt = Stock.find_by_ticket(data["ticket_code"])
		self.assert_objs_equals(objt, stock)


	def test_update_stock(self):
		stock = self.factory.get_new("Stock")
		data = {
			"ticket_code" : stock.ticket_code,
			"quantity" : 100
		}
		Stock.update(data)

	def test_pre_check_add(self):
		ticket_obj = Ticket("AMD")
		data = {
			"ticket_code" : ticket_obj.ticket_code,
			"ppc" : "pp",
			"quantity" : 1.2 ,
			"weighted_date" : "a"
		}
		errors = Stock.pre_check_add(data)
		self.assertTrue(bool(errors))


	def test_post_check_add(self):
		data = {
			"ratio": "cincuenta"
		}
		errors = Stock.post_check_add(data)
		self.assertTrue(bool(errors))


	def test_find_all(self):
		tickets_objs = Ticket.find_all()[:3]
		objs_expected = []
		for ticket_obj in tickets_objs:
			obj_created = self.factory.get_new("Stock", {"ticket_code": ticket_obj.ticket_code})
			objs_expected.append(obj_created)
		stock_objs = Stock.find_all()
		self.assertEqual(len(objs_expected), len(stock_objs))
		for i, obj in enumerate(stock_objs):
			self.assertIsInstance(obj, Stock)
			self.assert_objs_equals(objs_expected[i], obj)


	def test_find_by_ticket(self):
		ticket_code = Ticket.find_one().ticket_code
		obj_expected = self.factory.get_new("Stock", {"ticket_code": ticket_code})
		obj = Stock.find_by_ticket(ticket_code)
		self.assertIsInstance(obj, Stock)
		self.assert_objs_equals(obj_expected, obj)


	def test_attr_can_be_null(self):
		data = {
			"id" : random.randint(1,10),
			"name" : "nombrePrueba",
		}
		errors = Stock.post_check_add(data)
		self.assertFalse(bool(errors))


	def test_add_with_ticket_incorrect(self):
		data = {
			"ticket_code" : "Incorrect_ticket_name",
			"ppc" : round(random.uniform(1.0,20.0), 4),
			"quantity" : random.randint(1,10),
			"weighted_date" : random.randint(1,1000)
		}
		(stock, errors) = Stock.add(data)
		self.assertIsNone(stock)


	def test_delete(self):
		ticket_code = Ticket.find_one().ticket_code
		stock = self.factory.get_new("Stock", {"ticket_code": ticket_code})
		stock.delete()
		obj = Stock.find_by_ticket(ticket_code)
		self.assertIsNone(obj)


if __name__ == '__main__':
	unittest.main()