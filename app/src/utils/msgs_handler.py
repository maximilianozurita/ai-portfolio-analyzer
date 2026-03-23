import json

class msgsHandler:
	def __init__(self):
		self.messages = self.__load_messages('config/msgs_es.json')

	def __load_messages(self, json_file):
		with open(json_file) as file:
			return json.load(file)

	def get_message(self, key, params = []):
		if isinstance(params, list):
			message = self.messages.get(key, "Unknown error")
			count_params = message.count('{}')
			if len(params) == count_params and len(params) != 0:
				message = message.format(*params)
			elif (len(params) > count_params):
				message = ''
			elif (len(params) < count_params):
				message = ''
		else:
			message = ''
		return message

	@staticmethod
	def get_message_masivo(errors):
		menssages = []
		msgs = msgsHandler()
		for key, values in errors.items():
			for params in values:
				menssages.append(msgs.get_message(key, params))
		return menssages

	@staticmethod
	def print_masivo(errors):
		msgs = msgsHandler()
		for key, values in errors.items():
			for params in values:
				print(msgs.get_message(key, params))
