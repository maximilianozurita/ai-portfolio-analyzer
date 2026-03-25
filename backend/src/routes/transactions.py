from flask import Blueprint, request
from src.routes.routes_base import create_response
import src.services.transaction_service as transaction_service

stock = Blueprint('stransactions', __name__)

@stock.route('/transactions', methods=['PUT'])
def set_new_transaction():
	data = request.json
	r = transaction_service.add_transaction(data)
	code = 200 if r["ok"] else 500
	return create_response(r), code

@stock.route('/transactions', methods=['GET'])
def transaction():
	id = request.args.get('id')
	r = transaction_service.get_transaction_by_id(id) if id else transaction_service.get_transaction_list()
	code = 200 if r["ok"] else 404
	return create_response(r), code

@stock.route('/transactions/<int:transaction_id>/delete', methods=['POST'])
def delete_transaction(transaction_id):
	r = transaction_service.delete_transaction(transaction_id)
	code = 200 if r["ok"] else 500
	return create_response(r), code

@stock.route('/transactions/import', methods=['POST'])
def import_transactions_csv():
	file = request.files.get('file')
	r = transaction_service.import_from_csv(file)
	code = 200 if r["ok"] else 500
	return create_response(r), code

@stock.route('/transactions/<int:transaction_id>/revert', methods=['POST'])
def revert_transaction(transaction_id):
	r = transaction_service.revert_transaction(transaction_id)
	code = 200 if r["ok"] else 404
	return create_response(r), code
