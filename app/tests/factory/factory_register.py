from tests.factory.stock_factory import StockFactory
from tests.factory.transaction_factory import TransactionFactory
class FactoryRegister:
	_class = {
		"Stock": StockFactory,
		"Transaction" : TransactionFactory
	}
	def __init__(self):
		self.created_objects = []

	def get_new(self, class_name, data = None):
		if data is None: data = {}
		if class_name in FactoryRegister._class:
			obj_factory = FactoryRegister._class[class_name](data)
			obj_created = obj_factory.init_obj()
			self.delete_on_cleanup(obj_created)
			return obj_created

	def get_data_for(self, class_name, data = None):
		if data is None: data = {}
		if class_name in FactoryRegister._class:
			obj_factory = FactoryRegister._class[class_name](data)
			return obj_factory.attrs

	def delete_on_cleanup(self, obj_created):
		if obj_created: self.created_objects.append(obj_created)
