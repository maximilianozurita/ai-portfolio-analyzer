from flask import Blueprint, request
from src.routes.routes_base import create_response
import src.services.bond_service as bond_service

bond_bp = Blueprint('bonds', __name__)

@bond_bp.route('/bond-holdings', methods=['GET'])
def get_bond_holdings():
	r = bond_service.get_bond_holding()
	return create_response(r), 200

@bond_bp.route('/bond-transactions', methods=['GET'])
def get_bond_transactions():
	bond_code = request.args.get('bond_code')
	id = request.args.get('id')
	if id:
		r = bond_service.get_bond_transaction_by_id(int(id))
		code = 200 if r["ok"] else 404
	else:
		r = bond_service.get_bond_transactions(bond_code)
		code = 200
	return create_response(r), code

@bond_bp.route('/bond-holdings/import', methods=['POST'])
def import_bond_holdings():
	file = request.files.get('file')
	r = bond_service.import_bond_holding_from_csv(file)
	code = 200 if r["ok"] else 500
	return create_response(r), code

@bond_bp.route('/bond-transactions', methods=['PUT'])
def add_bond_transaction():
	data = request.json
	r = bond_service.add_bond_transaction(data)
	code = 200 if r["ok"] else 500
	return create_response(r), code

@bond_bp.route('/bond-transactions/<int:txn_id>/delete', methods=['POST'])
def delete_bond_transaction(txn_id):
	r = bond_service.delete_bond_transaction(txn_id)
	code = 200 if r["ok"] else 500
	return create_response(r), code

@bond_bp.route('/bond-transactions/<int:txn_id>/revert', methods=['POST'])
def revert_bond_transaction(txn_id):
	r = bond_service.revert_bond_transaction(txn_id)
	code = 200 if r["ok"] else 404
	return create_response(r), code
