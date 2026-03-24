from src.models.bond_holding import BondHolding
from tests.unit_tests.base import TestBase, unittest
import random

class TestBondHolding(TestBase):
	def test_add_bond_holding(self):
		data = {
			"bond_code": "AL30",
			"quantity": random.randint(1, 20),
			"ppc": round(random.uniform(50.0, 150.0), 4),
			"ppc_paridad": round(random.uniform(0.3, 1.2), 6),
			"weighted_date": random.randint(1000000, 9999999),
		}
		holding, errors = BondHolding.add(data)
		self.assertIsNone(errors)
		self.assertIsInstance(holding, BondHolding)
		self.factory.delete_on_cleanup(holding)
		for key in data:
			self.assertEqual(data[key], getattr(holding, key))

	def test_error_pre_check_add(self):
		data = {
			"bond_code": 123,
			"quantity": "diez",
			"ppc": "abc",
			"weighted_date": "x",
		}
		error_expected = {
			"ERROR_ATTR_TYPE": [
				["bond_code", "str", "int"],
				["quantity", "int", "str"],
				["ppc", "float", "str"],
				["weighted_date", "int", "str"],
			],
			"ERROR_ATTR_NONE": [["ppc_paridad"]],
		}
		self.generic_test_check_add(BondHolding, data, False, error_expected)

	def test_error_post_check_add(self):
		data = {"bond_code": "AL30"}
		error_expected = {"ERROR_ATTR_NONE": [["id"]]}
		self.generic_test_check_add(BondHolding, data, True, error_expected)

	def test_post_check_add_ok(self):
		data = {"id": random.randint(1, 100)}
		self.generic_test_check_add(BondHolding, data, True)

	def test_pre_check_add_ok(self):
		data = {
			"bond_code": "GD35",
			"quantity": 5,
			"ppc": 90.5,
			"ppc_paridad": 0.95,
			"weighted_date": 1711238400,
		}
		self.generic_test_check_add(BondHolding, data, False)

	def test_find_by_bond(self):
		holding = self.factory.get_new("BondHolding")
		found = BondHolding.find_by_bond(holding.bond_code)
		self.assertIsInstance(found, BondHolding)
		self.assert_objs_equals(holding, found)

	def test_find_by_bond_not_found(self):
		result = BondHolding.find_by_bond("INEXISTENTE_XXX")
		self.assertIsNone(result)

	def test_find_all(self):
		holding = self.factory.get_new("BondHolding")
		all_holdings = BondHolding.find_all()
		self.assertIn(holding, all_holdings)

	def test_update(self):
		holding = self.factory.get_new("BondHolding")
		new_qty = holding.quantity + 5
		new_ppc = round(holding.ppc * 1.1, 4)
		updated, errors = holding.update({"quantity": new_qty, "ppc": new_ppc,
										  "ppc_paridad": holding.ppc_paridad,
										  "weighted_date": holding.weighted_date})
		self.assertIsNone(errors)
		self.assertEqual(updated.quantity, new_qty)
		self.assertEqual(updated.ppc, new_ppc)

	def test_delete(self):
		holding = self.factory.get_new("BondHolding")
		bond_code = holding.bond_code
		holding.delete()
		result = BondHolding.find_by_bond(bond_code)
		self.assertIsNone(result)


if __name__ == '__main__':
	unittest.main()
