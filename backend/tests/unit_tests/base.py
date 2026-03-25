from tests.factory.factory_register import FactoryRegister
import unittest

class TestBase(unittest.TestCase):
	def setUp(self):
		self.factory = FactoryRegister()
		print("=======================================")
		print(f"Running test: {self.id().split('.')[-1]}")

	def tearDown(self):
		print(f"\nEnding test: {self.id().split('.')[-1]} \n")
		objs_to_delete = self.factory.created_objects
		for obj in objs_to_delete:
			obj.delete()

#================================================== Assert methods ======================================================================
	def assert_objs_equals(self, obj1, obj2):
		self.assertEqual(type(obj1), type(obj2))
		attr1 = obj1.__dict__
		attr2 = obj2.__dict__
		self.assertEqual(attr1, attr2)


	def assert_attr_equals(self, expected, testing):
		if not isinstance(expected, dict) and isinstance(expected, object):
			expected = expected.__dict__
		if not isinstance(testing, dict) and isinstance(expected, object):
			testing = testing.__dict__
		self.assertDictEqual(expected, testing)

#================================================== Generic tests ======================================================================
	def generic_test_check_add(self, cls, data, isPostCheck, expected_errors = None):
		errors = {}
		if isPostCheck:
			errors = cls.post_check_add(data)
		else:
			errors = cls.pre_check_add(data)

		if expected_errors:
			self.assertTrue(bool(errors))
			self.assertDictEqual(expected_errors, errors)
		else:
			self.assertFalse(bool(errors))
