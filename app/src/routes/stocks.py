from flask import Blueprint
import src.services.stock_service as stock_service
from src.routes.routes_base import create_response

stock = Blueprint('stocks', __name__)

@stock.route('/stocks', methods=['GET'])
def stock_holding():
	r = stock_service.get_stock_holding()
	code = 200 if r["ok"] else 500
	return create_response(r), code
