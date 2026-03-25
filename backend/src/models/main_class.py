from src.utils.msgs_handler import msgsHandler
from src.models.conector import ConectorBase

class MainClass:
	def __init__(self, data):
		errors = self.post_check_add(data)
		if len(errors) == 0:
			for attr in self._attrs:
				value = data.get(attr, None)
				setattr(self, attr, value)
		else:
			msgsHandler.get_message_masivo(errors)
			raise AttributeError("No se pudo crear objeto")

	#Define que attrs se consideran relevantes para saber si 2 objs son iguales 
	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.__dict__ == other.__dict__
		return False

	#Permite visualizar mejor el objeto y sus attr
	def __repr__(self):
		attrs = self.get_attr_dict()
		return self.__class__.__name__ + f'({attrs})'

	def delete(self):
		conector = ConectorBase()
		query = "delete from " + self._table + " where id = %s"
		r = conector.query_delete(query, [self.id])
		del self
		return r

	def get_attr_dict(self):
		attrs = {}
		for key in self._attrs:
			value = getattr(self, key)
			attrs[key] = value
		return attrs


#--------------------------------------------------------METODOS ESTATICOS--------------------------------------------------------------#
	@classmethod
	def get_attrs_keys(cls):
		attrs_array = []
		for attr in cls._attrs:
			attrs_array.append(attr)
		return attrs_array


	@classmethod
	def get_query_params(cls, data):
		columns = []
		values = []
		for attr_key, attr_dict in cls._attrs.items():
			if "column" in attr_dict:
				columns.append(attr_key)
				values.append(data.get(attr_key, None))
		return columns, values


	@classmethod
	def pre_check_add(cls, data, errors = None):
		if errors is None: errors = {}
		return MainClass.check_add(data, cls._attrs, False, errors)

	@classmethod
	def post_check_add(cls, data, errors = None):
		if errors is None: errors = {}
		return MainClass.check_add(data, cls._attrs, True, errors)

	@staticmethod
	def check_add(data, class_attrs, post_add, errors):
		attrs = {}
		if post_add:
			attrs = {key: value for key, value in class_attrs.items() if 'post_add' in value}
		else:
			attrs = {key: value for key, value in class_attrs.items() if 'post_add' not in value}
		for key, attr_dict in attrs.items():
			attr_type = attr_dict["type"]
			can_be_null = "null" in attr_dict
			if key in data:
				value = data[key]
				if not can_be_null and value is None:
					errors.setdefault("ERROR_ATTR_NONE", []).append([key])
				if not isinstance(value, attr_type):
					errors.setdefault("ERROR_ATTR_TYPE", []).append([key, attr_type.__name__, type(value).__name__])
			elif not can_be_null:
				errors.setdefault("ERROR_ATTR_NONE", []).append([key])
		return errors

	@classmethod
	def check_update(cls, data):
		errors = {}
		class_attrs = cls._attrs
		for key in data:
			if key not in class_attrs:
				errors.setdefault("ERROR_ATTR_INCORRECTO", []).append([key])
			else:
				attr_dict = class_attrs[key]
				attr_type = attr_dict["type"]
				if not isinstance(data[key], attr_type):
					errors.setdefault("ERROR_ATTR_TYPE", []).append([key, attr_type.__name__, type(data[key]).__name__])
		return errors
