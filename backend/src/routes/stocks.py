from flask import Blueprint, request
import src.services.stock_service as stock_service
from src.routes.routes_base import create_response

stock = Blueprint('stocks', __name__)

@stock.route('/stocks', methods=['GET'])
def stock_holding():
	r = stock_service.get_stock_holding()
	code = 200 if r["ok"] else 500
	return create_response(r), code

@stock.route('/stocks/import', methods=['POST'])
def import_stock_csv():
	file = request.files.get('file')
	r = stock_service.import_stock_from_csv(file)
	code = 200 if r["ok"] else 500
	return create_response(r), code

@stock.route('/stocks/<string:ticket_code>/adjust', methods=['POST'])
def adjust_stock(ticket_code):
	data = request.json
	factor = data.get('factor')
	if factor is None:
		from src.routes.routes_base import create_response
		return create_response({"ok": False, "msg": "Falta el campo 'factor'"}), 400
	r = stock_service.adjust_stock(ticket_code, float(factor))
	code = 200 if r["ok"] else 500
	return create_response(r), code
