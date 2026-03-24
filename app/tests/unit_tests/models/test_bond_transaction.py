from src.models.bond_transaction import BondTransaction
from tests.unit_tests.base import TestBase, unittest
import random

class TestBondTransaction(TestBase):
	def _sample_data(self, overrides=None):
		data = {
			"bond_code": "AL30",
			"transaction_type": "compra",
			"quantity": random.randint(1, 10),
			"unit_price": round(random.uniform(50.0, 150.0), 4),
			"valor_tecnico": round(random.uniform(80.0, 120.0), 4),
			"interest_currency": "USD",
			"amortization_currency": "USD",
			"usd_quote": random.randint(900, 1200),
			"date": random.randint(1000000, 9999999),
		}
		if overrides:
			data.update(overrides)
		return data

	def test_add_bond_transaction(self):
		data = self._sample_data()
		txn, errors = BondTransaction.add(data)
		self.assertIsNone(errors)
		self.assertIsInstance(txn, BondTransaction)
		self.factory.delete_on_cleanup(txn)
		for key in data:
			self.assertEqual(data[key], getattr(txn, key))

	def test_error_pre_check_add(self):
		data = {
			"bond_code": 123,
			"transaction_type": 5,
			"quantity": "x",
			"date": "y",
		}
		error_expected = {
			"ERROR_ATTR_TYPE": [
				["bond_code", "str", "int"],
				["transaction_type", "str", "int"],
				["quantity", "int", "str"],
				["date", "int", "str"],
			],
			"ERROR_ATTR_NONE": [["unit_price"], ["valor_tecnico"],
								["interest_currency"], ["amortization_currency"],
								["usd_quote"]],
		}
		self.generic_test_check_add(BondTransaction, data, False, error_expected)

	def test_error_post_check_add(self):
		data = {"bond_code": "AL30"}
		error_expected = {"ERROR_ATTR_NONE": [["id"]]}
		self.generic_test_check_add(BondTransaction, data, True, error_expected)

	def test_post_check_add_ok(self):
		data = {"id": random.randint(1, 100)}
		self.generic_test_check_add(BondTransaction, data, True)

	def test_pre_check_add_ok(self):
		data = self._sample_data()
		self.generic_test_check_add(BondTransaction, data, False)

	def test_find_by_id(self):
		txn = self.factory.get_new("BondTransaction")
		found = BondTransaction.find_by_id(txn.id)
		self.assertIsInstance(found, BondTransaction)
		self.assert_objs_equals(txn, found)

	def test_find_all_by_bond(self):
		bond_code = "GD35"
		created = [self.factory.get_new("BondTransaction", {"bond_code": bond_code}) for _ in range(3)]
		found = BondTransaction.find_all_by_bond(bond_code)
		for obj in created:
			self.assertIn(obj, found)

	def test_delete_by_id(self):
		txn = self.factory.get_new("BondTransaction")
		BondTransaction.delete_by_id(txn.id)
		self.assertIsNone(BondTransaction.find_by_id(txn.id))

	def test_delete(self):
		txn = self.factory.get_new("BondTransaction")
		txn_id = txn.id
		txn.delete()
		self.assertIsNone(BondTransaction.find_by_id(txn_id))


if __name__ == '__main__':
	unittest.main()
