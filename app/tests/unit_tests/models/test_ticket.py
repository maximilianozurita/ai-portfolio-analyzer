from src.models.ticket import Ticket
from src.models.conector import ConectorBase
from tests.unit_tests.base import TestBase, unittest

class TestTicket(TestBase):
	def test_init_object(self):
		cursor = ConectorBase()
		attrs_expected = cursor.select_one("select * from tickets limit 1")
		obj = Ticket(attrs_expected["ticket_code"])
		self.assertIsInstance(obj, Ticket)
		self.assert_attr_equals(attrs_expected, obj)

	def test_find_all(self):
		tickets = Ticket.find_all()
		self.assertGreater(len(tickets), 0)
		for ticket in tickets:
			self.assertIsInstance(ticket, Ticket)

	def test_find_one(self):
		ticket_obj = Ticket.find_one()
		self.assertIsInstance(ticket_obj, Ticket)

	def test_init_object_with_incorrect_ticket(self):
		ticket_obj = Ticket("TicketIncorrecto")
		self.assertIsNone(ticket_obj)

	def test_check_ticket_ok(self):
		# Se usa para verificacion de otros objetos que tienen una relacion con este.
		ticket_code = "AAPL"
		ticket_obj = Ticket(ticket_code)
		errors, data = Ticket.check_ticket(ticket_code, ["name", "date"])
		data["ticket_code"] = ticket_code
		self.assertDictEqual(errors, {})
		self.assert_attr_equals(ticket_obj, data)

	def test_error_check_ticket(self):
		ticket_code = "TICKETNOK"
		errors, data = Ticket.check_ticket(ticket_code, ["name", "date"])
		for key in data:
			self.assertIsNone(data[key])
		self.assertIsNotNone(errors["ERROR_ATTR_INCORRECTO"])

if __name__ == '__main__':
	unittest.main()