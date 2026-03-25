from src.models.transaction import Transaction
from src.models.ticket import Ticket
from src.utils.msgs_handler import msgsHandler
from tests.unit_tests.base import TestBase, unittest
import random

class TestTransaction(TestBase):
	def test_add_transaction(self):
		ticket_obj = Ticket("AAPL")
		data = {
			"ticket_code" : ticket_obj.ticket_code,
			"transaction_key" : random.randint(1,1000),
			"broker_name" : "IOLA",
			"quantity" : random.randint(1,100),
			"unit_price" : round(random.uniform(1,100), 4),
			"usd_quote" : random.randint(1,100),
			"date" : random.randint(1,1000)
		}
		(transaction, errors) = Transaction.add(data)
		self.assertIsNone(errors)
		self.assertIsInstance(transaction, Transaction)
		self.factory.delete_on_cleanup(transaction)
		for val in data: 
			self.assertEqual(data[val], getattr(transaction, val))
		objts = Transaction.find_all_by_ticket(data["ticket_code"])
		self.assertIn(transaction,objts)


	def test_error_pre_check_add(self):
		ticket_obj = Ticket("AMD")
		data = {
			"ticket_code" : ticket_obj.ticket_code,
			"transaction_key" : "pp",
			"broker_name" : 1.2 ,
			"quantity" : "b",
			"date" : "a",
		}
		error_expected = {
			'ERROR_ATTR_TYPE': [['transaction_key', 'int', 'str'], ['broker_name', 'str', 'float'], ['quantity', 'int', 'str'], ['date', 'int', 'str']],
			'ERROR_ATTR_NONE': [['unit_price'], ['usd_quote']]
		}
		self.generic_test_check_add(Transaction, data, False , error_expected)


	def test_error_post_check_add(self):
		data = {
			"name" : 1,
		}
		error_expected = {'ERROR_ATTR_NONE': [['id']]}
		self.generic_test_check_add(Transaction, data, True , error_expected)


	def test_post_check_add_ok(self):
		data = {"id" : random.randint(1,100)}
		self.generic_test_check_add(Transaction, data, True)


	def test_pre_check_add_ok(self):
		ticket_obj = Ticket("AMD")
		data = {
			"ticket_code" : ticket_obj.ticket_code,
			"transaction_key" : random.randint(1,1000),
			"broker_name" : "IOLA",
			"quantity" : random.randint(1,100),
			"unit_price" : round(random.uniform(1,100), 4),
			"usd_quote" : random.randint(1,100),
			"date" : random.randint(1,1000)
		}
		self.generic_test_check_add(Transaction, data, False)


	def test_find_by_id(self):
		obj_expected = self.factory.get_new("Transaction")
		obj = Transaction.find_by_id(obj_expected.id)
		self.assertIsInstance(obj, Transaction)
		self.assert_objs_equals(obj_expected, obj)


	def test_find_all_by_ticket(self):
		objs_expected = []
		ticket_code = Ticket("AMD").ticket_code
		for i in range(3):
			objs_expected.append(self.factory.get_new("Transaction", {"ticket_code" :  ticket_code}))
		objs_finded = Transaction.find_all_by_ticket(ticket_code)
		for i, obj in enumerate(objs_finded):
			self.assertIsInstance(obj, Transaction)
			self.assert_objs_equals(objs_expected[i], obj)


	def test_delete(self):
		transaction = self.factory.get_new("Transaction")
		transaction_id = transaction.id
		transaction.delete()
		obj = Transaction.find_by_id(transaction_id)
		self.assertIsNone(obj)


	def test_delete_by_id(self):
		transaction = self.factory.get_new("Transaction")
		Transaction.delete_by_id(transaction.id)
		transaction = Transaction.find_by_id(transaction.id)
		self.assertIsNone(transaction)


if __name__ == '__main__':
	unittest.main()
