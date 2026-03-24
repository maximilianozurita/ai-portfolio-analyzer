import csv
import io
from datetime import datetime
from src.models.stock import Stock
from src.models.transaction import Transaction
from src.utils.msgs_handler import msgsHandler

msgs = msgsHandler()

def get_stock_holding():
	data = []
	stocks = Stock.find_all()
	for stock in stocks:
		data.append(stock.get_attr_dict())
	return { "ok": True,"data": data}

def adjust_stock(ticket_code, factor):
	stock = Stock.find_by_ticket(ticket_code)
	if not stock:
		return {"ok": False, "msg": msgs.get_message("NOT_FOUND")}
	if factor <= 0:
		return {"ok": False, "msg": msgs.get_message("ERROR_FACTOR_INVALIDO")}

	new_data = {
		"quantity": round(stock.quantity * factor),
		"ppc": round(stock.ppc / factor, 4),
		"weighted_date": stock.weighted_date,
	}
	updated, errors = stock.update(new_data)
	if errors:
		return {"ok": False, "msg": msgs.get_message_masivo(errors)}
	return {"ok": True, "msg": msgs.get_message("STOCK_AJUSTADO", [ticket_code]), "data": updated.get_attr_dict()}

def import_stock_from_csv(file):
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
			for field in ('ticket_code', 'quantity', 'ppc', 'weighted_date'):
				if not row.get(field, '').strip():
					raise ValueError(f"Campo requerido '{field}' está vacío")

			ticket_code = row['ticket_code'].strip()
			if Stock.find_by_ticket(ticket_code):
				errors.append(f"Fila {i}: Ya existe stock para {ticket_code}")
				continue

			date_ts = int(datetime.strptime(row['weighted_date'].strip(), '%Y-%m-%d').timestamp())
			data = {
				'ticket_code': ticket_code,
				'quantity': int(row['quantity'].strip()),
				'ppc': float(row['ppc'].strip()),
				'weighted_date': date_ts,
			}

			stock, errs = Stock.add(data)
			if errs:
				errors.append(f"Fila {i}: {msgs.get_message_masivo(errs)}")
			else:
				ok_count += 1
		except Exception as e:
			errors.append(f"Fila {i}: {str(e)}")

	total = ok_count + len(errors)
	msg = msgs.get_message("CSV_STOCK_IMPORTADO", [ok_count, total])
	return {"ok": len(errors) == 0, "msg": msg, "data": {"ok": ok_count, "errors": errors}}

# =----------------------------ESTAS DEF SON DE EJEMPLO, NO SE USAN. SE USA LA PRIMERA
# def update_holding_stock(data):
# 	stock = Stock.find_by_ticket(data["ticket_code"])
# 	if stock:
# 		return stock.update_new_transaction(data)
# 	else:
# 		return {"ok": False, "msg": "No se encontro stock para ticket code"}
	# if stock['quantity'] + data['quantity'] < 0:
	# 	print('No hay suficientes acciones para eliminar')
	# 	return {'ok': False, 'msg': 'No hay suficientes acciones para eliminar, cantidad actual'}
	# else:
	# 	msg = ''
	# 	if stock['quantity'] + data['quantity'] == 0:
	# 		Stock.delete_stock_holding(stock['ticket_code'])
	# 		msg = {'message': 'eliminado'}
	# 	else:
	# 		new_stock_holding = stockHelper.get_new_stock_holding_data(stock, data)
	# 		Stock.set_stock_holding(new_stock_holding)
	# 		msg = {'message': 'eliminado'}
	# 	transactionModel.set_transaction(data)
	# 	return msg

# def set_new_transaction(data):
# 	stock = Stock.find_by_ticket(data['ticket_code'])
# 	if stock:
# 		errors = stock.update_new_transaction(data)
# 		if len(errors) == 0:
# 			data, errors = Transaction.add(data)
# 			if len(errors) == 0:
# 				response = { "ok": True, "msg": msgs.get_message("STOCK_UPDATED"), "data": stock.get_attr_dict()}
# 			else:
# 				response = { "ok": False, "msg": msgs.get_message_masivo(errors)}
# 		else:
# 			response = { "ok": False, "msg": msgs.get_message_masivo(errors), "data": stock.get_attr_dict()}
# 	else:
# 		if data["quantity"] > 0:
# 			stock, errors = Stock.add(data)
# 			if len(errors) == 0:
# 				response = { "ok": True, "msg": msgs.get_message("STOCK_ADDED"), "data": stock.get_attr_dict()}
# 			else:
# 				response = { "ok": False, "msg": msgs.get_message_masivo(errors)}
# 		else:
# 			response = { "ok": False, "msg": msgs.get_message("ERROR_ACCIONES_INSUFICIENTES", [0, data["quantity"]])}
# 	return response