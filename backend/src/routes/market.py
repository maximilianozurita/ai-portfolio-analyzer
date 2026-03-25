from flask import Blueprint
from src.routes.routes_base import create_response
from src.services import market_service

market_bp = Blueprint('market', __name__)

@market_bp.route('/market/prices/stocks', methods=['GET'])
def stock_prices():
	result = market_service.get_stock_prices()
	return create_response(result)

@market_bp.route('/market/prices/bonds', methods=['GET'])
def bond_prices():
	result = market_service.get_bond_prices()
	return create_response(result)
