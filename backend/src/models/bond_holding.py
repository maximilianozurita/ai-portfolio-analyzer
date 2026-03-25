from src.models.conector import ConectorBase
from src.utils.msgs_handler import msgsHandler
from src.models.main_class import MainClass

class BondHolding(MainClass):
	_table = "bond_holding"
	_attrs = {
		"id": {
			"type": int,
			"post_add": True,
		},
		"bond_code": {
			"type": str,
			"column": True
		},
		"quantity": {
			"type": int,
			"column": True
		},
		"ppc": {
			"type": float,
			"column": True
		},
		"ppc_paridad": {
			"type": float,
			"column": True
		},
		"weighted_date": {
			"type": int,
			"column": True
		},
	}

	def __init__(self, data):
		super().__init__(data)

#--------------------------------------------------------METODOS ESTATICOS--------------------------------------------------------------#
	@staticmethod
	def find_all():
		conector = ConectorBase()
		holdings = []
		query = "SELECT * FROM " + BondHolding._table + " ORDER BY bond_code"
		filas = conector.select(query)
		for fila in filas:
			holdings.append(BondHolding(fila))
		return holdings

	@staticmethod
	def find_by_bond(bond_code):
		conector = ConectorBase()
		query = "SELECT * FROM " + BondHolding._table + " WHERE bond_code = %s"
		fila = conector.select_one(query, [bond_code])
		if fila:
			return BondHolding(fila)
		return None

	@staticmethod
	def verify(data):
		errors = BondHolding.pre_check_add(data)
		return data, errors

	def verify_update(self, data):
		attrs_data = {**data, "bond_code": self.bond_code}
		errors = BondHolding.check_update(attrs_data)
		return attrs_data, errors

	@staticmethod
	def add(data):
		attrs_data, errors = BondHolding.verify(data)
		if len(errors) == 0:
			conector = ConectorBase()
			columns, values = BondHolding.get_query_params(attrs_data)
			query = "INSERT INTO " + BondHolding._table + " (" + ','.join(columns) + ") VALUES (" + ', '.join(['%s'] * len(columns)) + ")"
			attrs_data["id"] = conector.execute_query(query, values)
			return BondHolding(attrs_data), None
		else:
			msgsHandler.get_message_masivo(errors)
			return None, errors

	def update(self, data):
		attrs_data, errors = self.verify_update(data)
		if len(errors) == 0:
			conector = ConectorBase()
			columns, values = BondHolding.get_query_params(attrs_data)
			set_clause = ', '.join([f'{column} = %s' for column in columns])
			query = f'UPDATE {BondHolding._table} SET {set_clause} WHERE id = %s'
			values.append(self.id)
			conector.execute_query(query, values)
			attrs_data["id"] = self.id
			return BondHolding(attrs_data), None
		else:
			msgsHandler.get_message_masivo(errors)
			return None, errors
