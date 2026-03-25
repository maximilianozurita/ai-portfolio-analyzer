from config.config import OPENAI_API_KEY
from src.services.ai_providers.base_provider import BaseProvider

MODELS = [
	{"id": "gpt-4o", "name": "GPT-4o"},
	{"id": "gpt-4o-mini", "name": "GPT-4o Mini"},
	{"id": "gpt-4-turbo", "name": "GPT-4 Turbo"},
]

class OpenAIProvider(BaseProvider):
	def is_available(self) -> bool:
		return bool(OPENAI_API_KEY)

	def get_models(self) -> list:
		return MODELS

	def analyze(self, prompt: str, model: str) -> str:
		from openai import OpenAI
		client = OpenAI(api_key=OPENAI_API_KEY)
		response = client.chat.completions.create(
			model=model,
			messages=[{"role": "user", "content": prompt}]
		)
		return response.choices[0].message.content
