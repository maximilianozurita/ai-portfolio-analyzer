import src.services.bond_service as bond_service
from tests.unit_tests.base import TestBase, unittest
from src.utils.msgs_handler import msgsHandler
from src.models.bond_holding import BondHolding
from src.models.bond_transaction import BondTransaction
import copy

msgs = msgsHandler()

BOND_CODE = "AL30"

def _txn_data(overrides=None):
	data = {
		"bond_code": BOND_CODE,
		"transaction_type": "compra",
		"quantity": 10,
		"unit_price": 85.5,
		"valor_tecnico": 94.3,
		"interest_currency": "USD",
		"amortization_currency": "USD",
		"usd_quote": 1000,
		"date": 1711238400,
	}
	if overrides:
		data.update(overrides)
	return data

class TestBondService(TestBase):

	def _cleanup_bond(self, bond_code=BOND_CODE):
		h = BondHolding.find_by_bond(bond_code)
		if h:
			self.factory.delete_on_cleanup(h)
		for t in BondTransaction.find_all_by_bond(bond_code):
			self.factory.delete_on_cleanup(t)

	# 1. Compra sin holding previo → crea holding
	def test_add_compra_creates_holding(self):
		data = _txn_data()
		r = bond_service.add_bond_transaction(data)
		self._cleanup_bond()
		self.assertTrue(r["ok"])
		self.assertEqual(r["msg"], msgs.get_message("BONO_HOLDING_ADDED"))
		holding = r["data"]
		self.assertEqual(holding["quantity"], 10)
		self.assertAlmostEqual(holding["ppc"], 85.5, places=4)
		expected_paridad = round(85.5 / 94.3, 6)
		self.assertAlmostEqual(holding["ppc_paridad"], expected_paridad, places=6)

	# 2. Compra con holding existente → actualiza PPC y paridad (promedio ponderado)
	def test_add_compra_updates_holding(self):
		holding = self.factory.get_new("BondHolding", {
			"bond_code": BOND_CODE, "quantity": 10, "ppc": 85.5,
			"ppc_paridad": round(85.5 / 94.3, 6), "weighted_date": 1711238400
		})
		data = _txn_data({"quantity": 5, "unit_price": 90.0, "valor_tecnico": 95.0, "date": 1711300000})
		r = bond_service.add_bond_transaction(data)
		self._cleanup_bond()
		self.assertTrue(r["ok"])
		self.assertEqual(r["msg"], msgs.get_message("BONO_HOLDING_UPDATED"))
		updated = r["data"]
		expected_qty = 15
		expected_ppc = round((85.5 * 10 + 90.0 * 5) / 15, 4)
		expected_paridad = round((round(85.5 / 94.3, 6) * 10 + round(90.0 / 95.0, 6) * 5) / 15, 6)
		self.assertEqual(updated["quantity"], expected_qty)
		self.assertAlmostEqual(updated["ppc"], expected_ppc, places=4)
		self.assertAlmostEqual(updated["ppc_paridad"], expected_paridad, places=6)

	# 3. Venta → reduce cantidad, PPC sin cambio
	def test_add_venta_updates_holding(self):
		holding = self.factory.get_new("BondHolding", {
			"bond_code": BOND_CODE, "quantity": 10, "ppc": 85.5,
			"ppc_paridad": 0.906, "weighted_date": 1711238400
		})
		data = _txn_data({"transaction_type": "venta", "quantity": 3})
		r = bond_service.add_bond_transaction(data)
		self._cleanup_bond()
		self.assertTrue(r["ok"])
		self.assertEqual(r["data"]["quantity"], 7)
		self.assertAlmostEqual(r["data"]["ppc"], 85.5, places=4)

	# 4. Venta exacta → elimina holding
	def test_add_venta_deletes_holding(self):
		holding = self.factory.get_new("BondHolding", {
			"bond_code": BOND_CODE, "quantity": 5, "ppc": 85.5,
			"ppc_paridad": 0.906, "weighted_date": 1711238400
		})
		data = _txn_data({"transaction_type": "venta", "quantity": 5})
		r = bond_service.add_bond_transaction(data)
		for t in BondTransaction.find_all_by_bond(BOND_CODE):
			self.factory.delete_on_cleanup(t)
		self.assertTrue(r["ok"])
		self.assertEqual(r["msg"], msgs.get_message("BONO_HOLDING_DELETED"))
		self.assertIsNone(BondHolding.find_by_bond(BOND_CODE))

	# 5. Venta insuficiente → error
	def test_error_venta_insuficiente(self):
		holding = self.factory.get_new("BondHolding", {
			"bond_code": BOND_CODE, "quantity": 3, "ppc": 85.5,
			"ppc_paridad": 0.906, "weighted_date": 1711238400
		})
		data = _txn_data({"transaction_type": "venta", "quantity": 10})
		r = bond_service.add_bond_transaction(data)
		self.assertFalse(r["ok"])
		self.assertEqual(r["msg"], msgs.get_message("ERROR_LAMINAS_INSUFICIENTES", [3, 10]))
		self.assertIsNotNone(BondHolding.find_by_bond(BOND_CODE))

	# 6. Cupón → holding sin cambio
	def test_add_cupon_no_holding_change(self):
		holding = self.factory.get_new("BondHolding", {
			"bond_code": BOND_CODE, "quantity": 10, "ppc": 85.5,
			"ppc_paridad": 0.906, "weighted_date": 1711238400
		})
		old_qty = holding.quantity
		data = _txn_data({"transaction_type": "cupon", "quantity": 0})
		r = bond_service.add_bond_transaction(data)
		for t in BondTransaction.find_all_by_bond(BOND_CODE):
			self.factory.delete_on_cleanup(t)
		self.assertTrue(r["ok"])
		self.assertEqual(r["msg"], msgs.get_message("BONO_CUPON_REGISTRADO"))
		current = BondHolding.find_by_bond(BOND_CODE)
		self.assertEqual(current.quantity, old_qty)

	# 7. Amortización → reduce cantidad, PPC sin cambio
	def test_add_amortizacion_updates_holding(self):
		holding = self.factory.get_new("BondHolding", {
			"bond_code": BOND_CODE, "quantity": 10, "ppc": 85.5,
			"ppc_paridad": 0.906, "weighted_date": 1711238400
		})
		data = _txn_data({"transaction_type": "amortizacion", "quantity": 4})
		r = bond_service.add_bond_transaction(data)
		self._cleanup_bond()
		self.assertTrue(r["ok"])
		self.assertEqual(r["data"]["quantity"], 6)
		self.assertAlmostEqual(r["data"]["ppc"], 85.5, places=4)

	# 8. Amortización exacta → elimina holding
	def test_add_amortizacion_deletes_holding(self):
		holding = self.factory.get_new("BondHolding", {
			"bond_code": BOND_CODE, "quantity": 5, "ppc": 85.5,
			"ppc_paridad": 0.906, "weighted_date": 1711238400
		})
		data = _txn_data({"transaction_type": "amortizacion", "quantity": 5})
		r = bond_service.add_bond_transaction(data)
		for t in BondTransaction.find_all_by_bond(BOND_CODE):
			self.factory.delete_on_cleanup(t)
		self.assertTrue(r["ok"])
		self.assertEqual(r["msg"], msgs.get_message("BONO_HOLDING_DELETED"))
		self.assertIsNone(BondHolding.find_by_bond(BOND_CODE))

	# 9. Revert de compra → inversa de la fórmula
	def test_revert_compra(self):
		holding = self.factory.get_new("BondHolding", {
			"bond_code": BOND_CODE, "quantity": 15, "ppc": 87.0,
			"ppc_paridad": 0.92, "weighted_date": 1711260000
		})
		txn = self.factory.get_new("BondTransaction", {
			"bond_code": BOND_CODE, "transaction_type": "compra",
			"quantity": 5, "unit_price": 90.0, "valor_tecnico": 95.0,
			"interest_currency": "USD", "amortization_currency": "USD",
			"usd_quote": 1000, "date": 1711300000
		})
		r = bond_service.revert_bond_transaction(txn.id)
		updated = BondHolding.find_by_bond(BOND_CODE)
		if updated:
			self.factory.delete_on_cleanup(updated)
		self.assertTrue(r["ok"])
		self.assertEqual(updated.quantity, 10)
		paridad_revertida = round(90.0 / 95.0, 6)
		expected_ppc = round((87.0 * 15 - 90.0 * 5) / 10, 4)
		expected_paridad = round((0.92 * 15 - paridad_revertida * 5) / 10, 6)
		self.assertAlmostEqual(updated.ppc, expected_ppc, places=4)
		self.assertAlmostEqual(updated.ppc_paridad, expected_paridad, places=6)

	# 10. Revert de venta → restaura cantidad
	def test_revert_venta(self):
		holding = self.factory.get_new("BondHolding", {
			"bond_code": BOND_CODE, "quantity": 7, "ppc": 85.5,
			"ppc_paridad": 0.906, "weighted_date": 1711238400
		})
		txn = self.factory.get_new("BondTransaction", {
			"bond_code": BOND_CODE, "transaction_type": "venta",
			"quantity": 3, "unit_price": 88.0, "valor_tecnico": 94.3,
			"interest_currency": "USD", "amortization_currency": "USD",
			"usd_quote": 1000, "date": 1711238400
		})
		r = bond_service.revert_bond_transaction(txn.id)
		updated = BondHolding.find_by_bond(BOND_CODE)
		if updated:
			self.factory.delete_on_cleanup(updated)
		self.assertTrue(r["ok"])
		self.assertEqual(updated.quantity, 10)
		self.assertAlmostEqual(updated.ppc, 85.5, places=4)

	# 11. Revert de cupón → solo elimina el registro
	def test_revert_cupon(self):
		holding = self.factory.get_new("BondHolding", {
			"bond_code": BOND_CODE, "quantity": 10, "ppc": 85.5,
			"ppc_paridad": 0.906, "weighted_date": 1711238400
		})
		txn = self.factory.get_new("BondTransaction", {
			"bond_code": BOND_CODE, "transaction_type": "cupon",
			"quantity": 0, "unit_price": 0.0, "valor_tecnico": 94.3,
			"interest_currency": "USD", "amortization_currency": "USD",
			"usd_quote": 1000, "date": 1711238400
		})
		txn_id = txn.id
		r = bond_service.revert_bond_transaction(txn_id)
		self.assertTrue(r["ok"])
		self.assertIsNone(BondTransaction.find_by_id(txn_id))
		current = BondHolding.find_by_bond(BOND_CODE)
		self.assertEqual(current.quantity, 10)

	# 12. Revert de amortización → restaura cantidad
	def test_revert_amortizacion(self):
		holding = self.factory.get_new("BondHolding", {
			"bond_code": BOND_CODE, "quantity": 6, "ppc": 85.5,
			"ppc_paridad": 0.906, "weighted_date": 1711238400
		})
		txn = self.factory.get_new("BondTransaction", {
			"bond_code": BOND_CODE, "transaction_type": "amortizacion",
			"quantity": 4, "unit_price": 85.5, "valor_tecnico": 94.3,
			"interest_currency": "USD", "amortization_currency": "USD",
			"usd_quote": 1000, "date": 1711238400
		})
		r = bond_service.revert_bond_transaction(txn.id)
		updated = BondHolding.find_by_bond(BOND_CODE)
		if updated:
			self.factory.delete_on_cleanup(updated)
		self.assertTrue(r["ok"])
		self.assertEqual(updated.quantity, 10)
		self.assertAlmostEqual(updated.ppc, 85.5, places=4)

	# 13. Revert de transacción inexistente → error
	def test_revert_not_found(self):
		r = bond_service.revert_bond_transaction(999999)
		self.assertFalse(r["ok"])
		self.assertEqual(r["msg"], msgs.get_message("NOT_FOUND"))


if __name__ == '__main__':
	unittest.main()
