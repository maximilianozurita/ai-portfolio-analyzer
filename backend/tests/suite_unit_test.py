import unittest
from tests.unit_tests.factory_test.test_factory_stock import TestFactoryStock
from tests.unit_tests.factory_test.test_factory_transaction import TestFactoryTransaction
from tests.unit_tests.utils.test_msg_handler import TestMsgHandler
from tests.unit_tests.models.test_stock import TestStock
from tests.unit_tests.models.test_ticket import TestTicket
from tests.unit_tests.models.test_conector import TestConector
from tests.unit_tests.models.test_transaction import TestTransaction
from tests.unit_tests.models.test_bond_holding import TestBondHolding
from tests.unit_tests.models.test_bond_transaction import TestBondTransaction
from tests.unit_tests.services.test_stock_service import TestStockService
from tests.unit_tests.services.test_transaction_service import TestTransactionService
from tests.unit_tests.services.test_bond_service import TestBondService
# from tests.unit_tests.routes.test_stock_route import TestStockRoute
# from tests.unit_tests.routes.test_transaction_route import TestTransactionRoute

modules = [
	TestMsgHandler,
	TestFactoryStock,
	TestFactoryTransaction,
	TestStockService,
	TestTransactionService,
	TestBondService,
	# TestStockRoute,
	# TestTransactionRoute,
	TestStock,
	TestTicket,
	TestConector,
	TestTransaction,
	TestBondHolding,
	TestBondTransaction,
]

def suite():
	loader = unittest.TestLoader()
	suite = unittest.TestSuite()
	for test_case in modules:
		suite.addTests(loader.loadTestsFromTestCase(test_case))
		test_case_names = loader.getTestCaseNames(test_case)
		print("Test cases in " + test_case.__name__ + ": ", test_case_names)
	return suite

if __name__ == "__main__":
	runner = unittest.TextTestRunner()
	runner.run(suite())
