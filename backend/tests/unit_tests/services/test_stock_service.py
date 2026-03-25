import src.services.stock_service as stock_service
from tests.unit_tests.base import TestBase, unittest
from src.utils.msgs_handler import msgsHandler
msgs = msgsHandler()

class TestStockService(TestBase):
	def test_get_stock_holding(self):
		response_expected = {
			'ok': True, 
			'data': []
		}
		for i in range(5):
			stock = self.factory.get_new("Stock")
			response_expected["data"].append(stock.get_attr_dict())
		response = stock_service.get_stock_holding()
		self.assertDictEqual(response_expected, response)


	# def test_new_transaction_add_new_stock(self):
	# 	code_expected = 200
	# 	response_expected = {
	# 		'status': 'Ok', 
	# 		'message': '',
	# 		'data': []
	# 	}
	# 	# data = {
	# 	# 	"ticket_code" : ,
	# 	# 	"ppc" : ,
	# 	# 	"quantity" : ,
	# 	# 	"weighted_date" : ,
	# 	# 	"name" : ,
	# 	# 	"ratio" : 
	# 	# }
	# 	data = {
	# 		"ticket_code" : "AAPL",
	# 		"quantity" : 10
	# 	}
	# 	response, code = stock_service.set_new_transaction(data)

# test_new_transaction_update_stock_add_quantity
# test_new_transaction_update_stock_delete_quantity
# test_new_trasaction_delete_stock
# test_new_transaction_error_add_stock
# test_new_transaction_error_update_stock
# test_error_update_new_transaction

if __name__ == '__main__':
	unittest.main()