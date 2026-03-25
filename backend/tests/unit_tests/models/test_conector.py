from src.models.conector import ConectorBase
from tests.unit_tests.base import TestBase, unittest
from src.models.ticket import Ticket
from src.models.stock import Stock
import random

class TestConector(TestBase):
	def test_select_one(self):
		ticket_obj = Ticket("AAPL")
		expected = {
			"ticket_code" : ticket_obj.ticket_code,
			"transaction_key" : random.randint(1,1000),
			"broker_name" : "IOLA",
			"quantity" : random.randint(1,100),
			"unit_price" : round(random.uniform(1,100), 4),
			"usd_quote" : random.randint(1,100),
			"date" : random.randint(1,1000)
		}
		transaction = self.factory.get_new("Transaction", expected)
		conector = ConectorBase()
		query = 'select * from transaction where id = %s'
		select = conector.select_one(query, [transaction.id])
		expected["id"] = select["id"]
		self.assertDictEqual(expected, select)
		expected["unit_price"] += 1
		self.assertNotEqual(expected, select)


	def test_select_all(self):
		ticket_obj = Ticket("AAPL")
		expected = {
			"ticket_code" : ticket_obj.ticket_code,
			"transaction_key" : random.randint(1,1000),
			"broker_name" : "IOLA",
			"quantity" : random.randint(1,100),
			"unit_price" : round(random.uniform(1,100), 4),
			"usd_quote" : random.randint(1,100),
			"date" : random.randint(1,1000)
		}
		transaction = self.factory.get_new("Transaction", expected)
		conector = ConectorBase()
		query = 'select * from transaction where ticket_code = %s'
		select = conector.select(query, ["AAPL"])
		expected["id"] = transaction.id
		self.assertListEqual([expected], select)
		expected["unit_price"] += 1
		self.assertNotEqual([expected], select)


	def test_load_columns_attrs(self):
		conector = ConectorBase()
		conector.cursor.execute("select * from tickets")
		conector.cursor.fetchall()
		conector.load_column_attr()
		#En este caso se sabe que existen estos attrs
		attrs = ['ticket_code', 'name', 'date']
		self.assertListEqual(attrs, conector.columnas_name)


	def test_load_columns_attrs_one_row(self):
		conector = ConectorBase()
		conector.cursor.execute("select * from tickets")
		conector.cursor.fetchone()
		conector.load_column_attr()
		attrs = ['ticket_code', 'name', 'date']
		self.assertListEqual(attrs, conector.columnas_name)


	def test_load_columns_attrs_none_rows(self):
		conector = ConectorBase()
		conector.cursor.execute("delete from " + Stock._table)
		conector.cursor.execute("select * from " + Stock._table)
		conector.cursor.fetchone()
		conector.load_column_attr()
		attrs = ['id', 'ticket_code', 'ppc', 'quantity', 'weighted_date']
		self.assertListEqual(attrs, conector.columnas_name)


if __name__ == '__main__':
	unittest.main()