from src.utils.msgs_handler import msgsHandler
from tests.unit_tests.base import TestBase, unittest

class TestMsgHandler(TestBase):
	def test_msg_with_args(self):
		msgs = msgsHandler()
		key = "peso"
		msg_parsed = msgs.get_message("test_msj1_params", [key])
		self.assertIsInstance(msg_parsed, str)
		self.assertIn(key, msg_parsed)

	def test_msg_without_args(self):
		msgs = msgsHandler()
		msg_parsed = msgs.get_message("test_msj_sin_params")
		self.assertIsInstance(msg_parsed, str)

	def test_msg_with_multiple_args(self):
		msgs = msgsHandler()
		key1 = "prueba"
		key2 = "prueba2"
		msg_parsed = msgs.get_message("test_msj2_params", [key1, key2])
		self.assertIsInstance(msg_parsed, str)
		self.assertIn(key1, msg_parsed)
		self.assertIn(key2, msg_parsed)

	def test_error_msg_without_args(self):
		msgs = msgsHandler()
		msg_parsed = msgs.get_message("test_msj1_params")
		self.assertIsInstance(msg_parsed, str)
		self.assertEqual(msg_parsed, "")

	def test_error_msg_with_extra_params(self):
		msgs = msgsHandler()
		msg_parsed = msgs.get_message("test_msj1_params", ["prueba", "prueba2"])
		self.assertIsInstance(msg_parsed, str)
		self.assertEqual(msg_parsed, "")

	def test_error_msg_with_less_params(self):
		msgs = msgsHandler()
		msg_parsed = msgs.get_message("test_msj2_params", ["prueba"])
		self.assertIsInstance(msg_parsed, str)
		self.assertEqual(msg_parsed, "")

	def test_error_msg_with_param_not_array(self):
		msgs = msgsHandler()
		msg_parsed = msgs.get_message("test_msj2_params", "prueba")
		self.assertIsInstance(msg_parsed, str)
		self.assertEqual(msg_parsed, "")

	def test_print_multiple_msg(self):
		msgs_params = {
			"test_msj_sin_params" : [[]],
			"test_msj1_params": [["prueba"]],
			"test_msj2_params": [["prueba", "prueba2"], ["prueb3", "prueba4"]]
		}
		msgs = msgsHandler.get_message_masivo(msgs_params)
		for msg in msgs:
			self.assertIsInstance(msg, str)
			self.assertNotEqual(msg, "")

if __name__ == '__main__':
	unittest.main()