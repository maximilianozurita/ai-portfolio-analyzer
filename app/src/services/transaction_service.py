from src.models.stock import Stock
from src.models.transaction import Transaction
from src.utils.msgs_handler import msgsHandler

msgs = msgsHandler()

def delete_transaction(id):
	rowcount = Transaction.delete_by_id(id)
	if rowcount:
		return {"ok": True, "msg": msgs.get_message("ELEMENTO_ELIMINADO", [id])}
	return {"ok": False, "msg": msgs.get_message("ERROR_ELIMINAR", [id])}

def get_transaction_by_id(id):
	transaction = Transaction.find_by_id(id)
	if transaction:
		return {"ok": True, "msg": msgs.get_message("ELEMENTO_ENCONTRADO", [id]), "data": transaction.get_attr_dict()}
	return {"ok": False, "msg": msgs.get_message("NOT_FOUND")}

def get_transaction_list():
	transactions = Transaction.find_all()
	return {"ok": True, "data": [t.get_attr_dict() for t in transactions]}

def get_transaction_list_by_ticket(ticket_code):
	transactions = Transaction.find_all_by_ticket(ticket_code)
	return {"ok": True, "data": [t.get_attr_dict() for t in transactions]}

def calculate_by_transaction(transaction, stock=None):
	if stock is None:
		return {"ticket_code": transaction.ticket_code, "quantity": transaction.quantity,
				"ppc": transaction.unit_price, "weighted_date": transaction.date}
	new_qty = stock.quantity + transaction.quantity
	if transaction.quantity > 0:
		new_ppc = round((stock.ppc * stock.quantity + transaction.quantity * transaction.unit_price) / new_qty, 4)
		new_date = int((stock.weighted_date * stock.quantity + transaction.quantity * transaction.date) / new_qty)
	else:
		new_ppc = stock.ppc
		new_date = stock.weighted_date
	return {"ticket_code": stock.ticket_code, "quantity": new_qty, "ppc": new_ppc, "weighted_date": new_date}

def calculate_revert_transaction(transaction, stock):
	if transaction.quantity > 0:
		new_qty = stock.quantity - transaction.quantity
		if new_qty == 0:
			return {"ticket_code": stock.ticket_code, "quantity": 0, "ppc": stock.ppc, "weighted_date": stock.weighted_date}
		new_ppc = round((stock.ppc * stock.quantity - transaction.quantity * transaction.unit_price) / new_qty, 4)
		new_date = int((stock.weighted_date * stock.quantity - transaction.quantity * transaction.date) / new_qty)
		return {"ticket_code": stock.ticket_code, "quantity": new_qty, "ppc": new_ppc, "weighted_date": new_date}
	else:
		return {"ticket_code": stock.ticket_code, "quantity": stock.quantity - transaction.quantity,
				"ppc": stock.ppc, "weighted_date": stock.weighted_date}

def add_transaction(data):
	stock = Stock.find_by_ticket(data["ticket_code"])
	qty = data["quantity"]
	current_qty = stock.quantity if stock else 0

	if qty < 0 and (current_qty + qty) < 0:
		return {"ok": False, "msg": msgs.get_message("ERROR_ACCIONES_INSUFICIENTES", [current_qty, qty])}

	transaction, errors = Transaction.add(data)
	if errors:
		return {"ok": False, "msg": msgs.get_message_masivo(errors)}

	if stock is None:
		new_stock_data = calculate_by_transaction(transaction)
		new_stock, errors = Stock.add(new_stock_data)
		if errors:
			return {"ok": False, "msg": msgs.get_message_masivo(errors)}
		return {"ok": True, "msg": msgs.get_message("STOCK_ADDED"), "stock": new_stock.get_attr_dict()}

	new_data = calculate_by_transaction(transaction, stock)
	if new_data["quantity"] == 0:
		stock.delete()
		return {"ok": True, "msg": msgs.get_message("STOCK_DELETED")}

	updated_stock, errors = stock.update(new_data)
	if errors:
		return {"ok": False, "msg": msgs.get_message_masivo(errors)}
	return {"ok": True, "msg": msgs.get_message("STOCK_UPDATED"), "data": updated_stock.get_attr_dict()}

def revert_transaction(id):
	transaction = Transaction.find_by_id(id)
	if not transaction:
		return {"ok": False, "msg": msgs.get_message("NOT_FOUND")}
	stock = Stock.find_by_ticket(transaction.ticket_code)
	new_data = calculate_revert_transaction(transaction, stock)
	if new_data["quantity"] == 0:
		stock.delete()
	else:
		stock.update(new_data)
	Transaction.delete_by_id(id)
	return {"ok": True, "msg": msgs.get_message("TRANSACCION_REVERTIDA")}
