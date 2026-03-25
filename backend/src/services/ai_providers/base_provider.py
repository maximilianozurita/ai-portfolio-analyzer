class BaseProvider:
	def analyze(self, prompt: str, model: str) -> str:
		raise NotImplementedError

	def get_models(self) -> list:
		raise NotImplementedError

	def is_available(self) -> bool:
		raise NotImplementedError
