from flask import Blueprint, request
from src.routes.routes_base import create_response
from src.services import ai_service

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/ai/providers', methods=['GET'])
def get_providers():
	providers = ai_service.get_available_providers()
	return create_response({"ok": True, "data": providers})

@ai_bp.route('/ai/analyze', methods=['POST'])
def analyze():
	body = request.get_json() or {}
	provider_id = body.get("provider")
	model = body.get("model")

	if not provider_id or not model:
		return create_response({"ok": False, "msg": "Se requieren los campos 'provider' y 'model'"})

	market_stocks = body.get("market_prices_stocks") or None
	market_bonds = body.get("market_prices_bonds") or None
	result = ai_service.analyze_portfolio(provider_id, model, market_stocks, market_bonds)
	return create_response(result)
