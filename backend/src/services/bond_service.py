import csv
import io
from datetime import datetime
from src.models.bond_holding import BondHolding
from src.models.bond_transaction import BondTransaction
from src.utils.msgs_handler import msgsHandler

msgs = msgsHandler()

def delete_bond_transaction(id):
	rowcount = BondTransaction.delete_by_id(id)
	if rowcount:
		return {"ok": True, "msg": msgs.get_message("ELEMENTO_ELIMINADO", [id])}
	return {"ok": False, "msg": msgs.get_message("ERROR_ELIMINAR", [id])}

def get_bond_transaction_by_id(id):
	txn = BondTransaction.find_by_id(id)
	if txn:
		return {"ok": True, "msg": msgs.get_message("ELEMENTO_ENCONTRADO", [id]), "data": txn.get_attr_dict()}
	return {"ok": False, "msg": msgs.get_message("NOT_FOUND")}

def get_bond_transactions(bond_code=None):
	if bond_code:
		txns = BondTransaction.find_all_by_bond(bond_code)
	else:
		txns = BondTransaction.find_all()
	return {"ok": True, "data": [t.get_attr_dict() for t in txns]}

def get_bond_holding():
	holdings = BondHolding.find_all()
	return {"ok": True, "data": [h.get_attr_dict() for h in holdings]}

def calculate_by_bond_transaction(bond_txn, holding=None):
	if bond_txn.transaction_type == 'cupon':
		return None

	if holding is None:
		return {
			"bond_code": bond_txn.bond_code,
			"quantity": bond_txn.quantity,
			"ppc": round(bond_txn.unit_price / 100, 6),
			"ppc_paridad": round(bond_txn.unit_price / bond_txn.valor_tecnico, 6),
			"weighted_date": bond_txn.date
		}

	paridad = round(bond_txn.unit_price / bond_txn.valor_tecnico, 6)
	unit_price_norm = bond_txn.unit_price / 100

	if bond_txn.transaction_type == 'compra':
		new_qty = holding.quantity + bond_txn.quantity
		new_ppc = round((holding.ppc * holding.quantity + unit_price_norm * bond_txn.quantity) / new_qty, 6)
		new_ppc_paridad = round((holding.ppc_paridad * holding.quantity + paridad * bond_txn.quantity) / new_qty, 6)
		new_date = int((holding.weighted_date * holding.quantity + bond_txn.date * bond_txn.quantity) / new_qty)
		return {"bond_code": bond_txn.bond_code, "quantity": new_qty,
				"ppc": new_ppc, "ppc_paridad": new_ppc_paridad, "weighted_date": new_date}

	# venta o amortizacion: PPC y paridad sin cambio
	return {
		"bond_code": holding.bond_code,
		"quantity": holding.quantity - bond_txn.quantity,
		"ppc": holding.ppc,
		"ppc_paridad": holding.ppc_paridad,
		"weighted_date": holding.weighted_date
	}

def calculate_revert_bond_transaction(bond_txn, holding):
	if bond_txn.transaction_type == 'cupon':
		return None

	if bond_txn.transaction_type == 'compra':
		new_qty = holding.quantity - bond_txn.quantity
		if new_qty == 0:
			return {"quantity": 0}
		paridad = round(bond_txn.unit_price / bond_txn.valor_tecnico, 6)
		unit_price_norm = bond_txn.unit_price / 100
		new_ppc = round((holding.ppc * holding.quantity - unit_price_norm * bond_txn.quantity) / new_qty, 6)
		new_ppc_paridad = round((holding.ppc_paridad * holding.quantity - paridad * bond_txn.quantity) / new_qty, 6)
		new_date = int((holding.weighted_date * holding.quantity - bond_txn.date * bond_txn.quantity) / new_qty)
		return {"bond_code": holding.bond_code, "quantity": new_qty,
				"ppc": new_ppc, "ppc_paridad": new_ppc_paridad, "weighted_date": new_date}

	# revert de venta o amortizacion: restaura cantidad
	return {
		"bond_code": holding.bond_code,
		"quantity": holding.quantity + bond_txn.quantity,
		"ppc": holding.ppc,
		"ppc_paridad": holding.ppc_paridad,
		"weighted_date": holding.weighted_date
	}

def add_bond_transaction(data):
	holding = BondHolding.find_by_bond(data["bond_code"])
	txn_type = data.get("transaction_type")
	qty = data.get("quantity", 0)
	current_qty = holding.quantity if holding else 0

	if txn_type in ('venta', 'amortizacion') and (current_qty - qty) < 0:
		return {"ok": False, "msg": msgs.get_message("ERROR_LAMINAS_INSUFICIENTES", [current_qty, qty])}

	if holding is None and txn_type != 'compra':
		return {"ok": False, "msg": msgs.get_message("ERROR_LAMINAS_INSUFICIENTES", [0, qty])}

	bond_txn, errors = BondTransaction.add(data)
	if errors:
		return {"ok": False, "msg": msgs.get_message_masivo(errors)}

	new_data = calculate_by_bond_transaction(bond_txn, holding)

	if new_data is None:
		return {"ok": True, "msg": msgs.get_message("BONO_CUPON_REGISTRADO")}

	if holding is None:
		new_holding, errors = BondHolding.add(new_data)
		if errors:
			return {"ok": False, "msg": msgs.get_message_masivo(errors)}
		return {"ok": True, "msg": msgs.get_message("BONO_HOLDING_ADDED"), "data": new_holding.get_attr_dict()}

	if new_data["quantity"] == 0:
		holding.delete()
		return {"ok": True, "msg": msgs.get_message("BONO_HOLDING_DELETED")}

	updated, errors = holding.update(new_data)
	if errors:
		return {"ok": False, "msg": msgs.get_message_masivo(errors)}
	return {"ok": True, "msg": msgs.get_message("BONO_HOLDING_UPDATED"), "data": updated.get_attr_dict()}

def import_bond_holding_from_csv(file):
	if not file:
		return {"ok": False, "msg": msgs.get_message("CSV_SIN_ARCHIVO")}

	content = file.stream.read().decode('utf-8-sig')
	dialect = csv.Sniffer().sniff(content.splitlines()[0], delimiters=',;')
	stream = io.StringIO(content)
	reader = csv.DictReader(stream, dialect=dialect)

	ok_count = 0
	errors = []

	for i, row in enumerate(reader, start=2):
		try:
			for field in ('bond_code', 'quantity', 'ppc', 'ppc_paridad', 'weighted_date'):
				if not row.get(field, '').strip():
					raise ValueError(f"Campo requerido '{field}' está vacío")

			bond_code = row['bond_code'].strip().upper()
			if BondHolding.find_by_bond(bond_code):
				errors.append(f"Fila {i}: Ya existe posición para {bond_code}")
				continue

			date_ts = int(datetime.strptime(row['weighted_date'].strip(), '%Y-%m-%d').timestamp())
			data = {
				'bond_code': bond_code,
				'quantity': int(row['quantity'].strip()),
				'ppc': round(float(row['ppc'].strip()) / 100, 6),
				'ppc_paridad': float(row['ppc_paridad'].strip()),
				'weighted_date': date_ts,
			}

			holding, errs = BondHolding.add(data)
			if errs:
				errors.append(f"Fila {i}: {msgs.get_message_masivo(errs)}")
			else:
				ok_count += 1
		except Exception as e:
			errors.append(f"Fila {i}: {str(e)}")

	total = ok_count + len(errors)
	msg = msgs.get_message("CSV_BONO_IMPORTADO", [ok_count, total])
	return {"ok": len(errors) == 0, "msg": msg, "data": {"ok": ok_count, "errors": errors}}


def revert_bond_transaction(id):
	bond_txn = BondTransaction.find_by_id(id)
	if not bond_txn:
		return {"ok": False, "msg": msgs.get_message("NOT_FOUND")}

	if bond_txn.transaction_type == 'cupon':
		BondTransaction.delete_by_id(id)
		return {"ok": True, "msg": msgs.get_message("TRANSACCION_REVERTIDA")}

	holding = BondHolding.find_by_bond(bond_txn.bond_code)
	new_data = calculate_revert_bond_transaction(bond_txn, holding)

	if new_data["quantity"] == 0:
		holding.delete()
	else:
		holding.update(new_data)

	BondTransaction.delete_by_id(id)
	return {"ok": True, "msg": msgs.get_message("TRANSACCION_REVERTIDA")}
