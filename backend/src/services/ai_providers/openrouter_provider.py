from config.config import OPENROUTER_API_KEY
from src.services.ai_providers.base_provider import BaseProvider

MODELS = [
	{"id": "meta-llama/llama-3.3-70b-instruct:free", "name": "Llama 3.3 70B (gratis)"},
	{"id": "deepseek/deepseek-r1:free", "name": "DeepSeek R1 (gratis)"},
	{"id": "mistralai/mistral-7b-instruct:free", "name": "Mistral 7B (gratis)"},
]

class OpenRouterProvider(BaseProvider):
	def is_available(self) -> bool:
		return bool(OPENROUTER_API_KEY)

	def get_models(self) -> list:
		return MODELS

	def analyze(self, prompt: str, model: str) -> str:
		from openai import OpenAI
		client = OpenAI(
			api_key=OPENROUTER_API_KEY,
			base_url="https://openrouter.ai/api/v1"
		)
		response = client.chat.completions.create(
			model=model,
			messages=[{"role": "user", "content": prompt}]
		)
		return response.choices[0].message.content
