import random
import string
from src.utils.msgs_handler import msgsHandler

class FactoryBase:
	def __init__(self, data):
		self.attrs = self.attr_parser(data)

	def attr_parser(self, data):
		return data

	def init_obj(self):
		(obj, errors) = self.pkg.add(self.attrs)
		if not errors:
			return obj
		else:
			msgsHandler.print_masivo(errors)

	def get_random_string(length=10):
		characters = string.ascii_letters + string.digits
		return ''.join(random.choice(characters) for i in range(length))
