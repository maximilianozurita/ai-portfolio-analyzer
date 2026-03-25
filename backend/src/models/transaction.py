from src.models.conector import ConectorBase
from src.utils.msgs_handler import msgsHandler
from src.models.main_class import MainClass
from src.models.ticket import Ticket

class Transaction(MainClass):
	_table = "transaction"
	_attrs = {
		"id": {
			"type" : int,
			"post_add" : True,
		},
		"ticket_code": {
			"type": str,
			"column" : True
		},
		"transaction_key": {
			"type": int,
			"null" : True,
			"column" : True
		},
		"broker_name": {
			"type": str,
			"null" : True,
			"column" : True
		},
		"quantity": {
			"type": int,
			"column" : True
		},
		"unit_price": {
			"type": float,
			"column" : True
		},
		"usd_quote": {
			"type": int,
			"column" : True
		},
		"date": {
			"type": int,
			"column" : True
		},
	}

	def __init__(self, data):
		super().__init__(data)

	@staticmethod
	def verify(data):
		errors, ticket_data = Ticket.check_ticket(data["ticket_code"], ["ticket_code"])
		attrs_data = {**data, **ticket_data}
		errors = Transaction.pre_check_add(attrs_data, errors)
		return attrs_data, errors

	@staticmethod
	def add(data):
		attrs_data, errors = Transaction.verify(data)
		if len(errors) == 0:
			conector = ConectorBase()
			columns, values = Transaction.get_query_params(attrs_data)
			query = "INSERT INTO " + Transaction._table + " (" + ','.join(columns) + ") VALUES (" + ', '.join(['%s'] * len(columns)) + ")"
			attrs_data["id"] = conector.execute_query(query, values)
			return Transaction(attrs_data), None
		else:
			msgsHandler.print_masivo(errors)
			return None, errors

	@staticmethod
	def find_by_id(id):
		conector = ConectorBase()
		query = "SELECT * from " + Transaction._table + " where id = %s"
		fila = conector.select_one(query, [id])
		if fila:
			return Transaction(fila)
		return None

	@staticmethod
	def find_all_by_ticket(ticket_code):
		conector = ConectorBase()
		transaction = []
		query = "SELECT * from " + Transaction._table + " where ticket_code = %s"
		filas = conector.select(query, [ticket_code])
		for fila in filas:
			transaction.append(Transaction(fila))
		return transaction

	@staticmethod
	def find_all():
		conector = ConectorBase()
		transaction = []
		query = "SELECT * from " + Transaction._table
		filas = conector.select(query)
		for fila in filas:
			transaction.append(Transaction(fila))
		return transaction


	@staticmethod
	def delete_by_id(id):
		conector = ConectorBase()
		query = "delete from " + Transaction._table + " where id = %s"
		return conector.query_delete(query, [id])
