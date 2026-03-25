from config.config import GEMINI_API_KEY
from src.services.ai_providers.base_provider import BaseProvider

MODELS = [
	{"id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash"},
	{"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash"},
	{"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro"},
]

class GeminiProvider(BaseProvider):
	def is_available(self) -> bool:
		return bool(GEMINI_API_KEY)

	def get_models(self) -> list:
		return MODELS

	def analyze(self, prompt: str, model: str) -> str:
		import google.generativeai as genai
		genai.configure(api_key=GEMINI_API_KEY)
		client = genai.GenerativeModel(model)
		response = client.generate_content(prompt)
		return response.text
