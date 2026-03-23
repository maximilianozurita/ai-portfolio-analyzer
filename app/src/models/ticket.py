from src.models.conector import ConectorBase

class Ticket:
	_tabla = "tickets"
	def __new__(cls, ticket_code, data = None):
		if ticket_code is not None:
			if not data:
				data = Ticket.load_data(ticket_code)
			if data:
				instance = super(Ticket, cls).__new__(cls)
				instance.ticket_code = data["ticket_code"]
				instance.name = data["name"]
				instance.ratio = data["ratio"]
				instance.date = data["date"]
				return instance
		return None

	def __repr__(self):
			attrs = ', '.join(f'{attr}={getattr(self, attr)}' for attr in vars(self))
			return self.__class__.__name__ + f'({attrs})'

	@staticmethod
	def find_all():
		conector = ConectorBase()
		tickets = []
		query = "SELECT * from " + Ticket._tabla
		filas = conector.select(query)
		for fila in filas:
			tickets.append(Ticket(fila["ticket_code"], fila))
		return tickets

	@staticmethod
	def find_one():
		conector = ConectorBase()
		query = "SELECT t.* from " + Ticket._tabla + " t left join stock s on (t.ticket_code = s.ticket_code) where s.ticket_code is null limit 1"
		attrs_expected = conector.select_one(query)
		if attrs_expected:
			return Ticket(attrs_expected["ticket_code"])
		return None

	@staticmethod
	def load_data(ticket_code):
		conector = ConectorBase()
		query = "SELECT * from " + Ticket._tabla + " WHERE ticket_code = %s"
		return conector.select_one(query, [ticket_code])


	@staticmethod
	def check_ticket(ticket_code, columns):
		conector = ConectorBase()
		query = "SELECT " + ','.join(columns) + " FROM " + Ticket._tabla + " WHERE ticket_code = %s"
		ticket_data = conector.select_one(query, [ticket_code])
		if ticket_data:
			return {}, ticket_data
		else:
			return {"ERROR_ATTR_INCORRECTO" : [[ticket_code]]}, {key: None for key in columns}
