from src.models.conector import ConectorBase
from src.utils.msgs_handler import msgsHandler
from src.models.main_class import MainClass

class BondTransaction(MainClass):
	_table = "bond_transaction"
	_attrs = {
		"id": {
			"type": int,
			"post_add": True,
		},
		"bond_code": {
			"type": str,
			"column": True
		},
		"transaction_type": {
			"type": str,
			"column": True
		},
		"quantity": {
			"type": int,
			"column": True
		},
		"unit_price": {
			"type": float,
			"column": True
		},
		"valor_tecnico": {
			"type": float,
			"column": True
		},
		"interest_currency": {
			"type": str,
			"column": True
		},
		"amortization_currency": {
			"type": str,
			"column": True
		},
		"usd_quote": {
			"type": int,
			"column": True
		},
		"date": {
			"type": int,
			"column": True
		},
		"broker_name": {
			"type": str,
			"null": True,
			"column": True
		},
		"transaction_key": {
			"type": int,
			"null": True,
			"column": True
		},
	}

	def __init__(self, data):
		super().__init__(data)

	@staticmethod
	def verify(data):
		errors = BondTransaction.pre_check_add(data)
		return data, errors

	@staticmethod
	def add(data):
		attrs_data, errors = BondTransaction.verify(data)
		if len(errors) == 0:
			conector = ConectorBase()
			columns, values = BondTransaction.get_query_params(attrs_data)
			query = "INSERT INTO " + BondTransaction._table + " (" + ','.join(columns) + ") VALUES (" + ', '.join(['%s'] * len(columns)) + ")"
			attrs_data["id"] = conector.execute_query(query, values)
			return BondTransaction(attrs_data), None
		else:
			msgsHandler.print_masivo(errors)
			return None, errors

	@staticmethod
	def find_by_id(id):
		conector = ConectorBase()
		query = "SELECT * FROM " + BondTransaction._table + " WHERE id = %s"
		fila = conector.select_one(query, [id])
		if fila:
			return BondTransaction(fila)
		return None

	@staticmethod
	def find_all_by_bond(bond_code):
		conector = ConectorBase()
		transactions = []
		query = "SELECT * FROM " + BondTransaction._table + " WHERE bond_code = %s ORDER BY date"
		filas = conector.select(query, [bond_code])
		for fila in filas:
			transactions.append(BondTransaction(fila))
		return transactions

	@staticmethod
	def find_all():
		conector = ConectorBase()
		transactions = []
		query = "SELECT * FROM " + BondTransaction._table + " ORDER BY date"
		filas = conector.select(query)
		for fila in filas:
			transactions.append(BondTransaction(fila))
		return transactions

	@staticmethod
	def delete_by_id(id):
		conector = ConectorBase()
		query = "DELETE FROM " + BondTransaction._table + " WHERE id = %s"
		return conector.query_delete(query, [id])
