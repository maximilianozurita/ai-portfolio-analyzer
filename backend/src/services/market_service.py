import yfinance as yf
from src.models.stock import Stock
from src.models.bond_holding import BondHolding


def _fetch_prices(tickers_ba: list[str]) -> dict:
	"""Descarga el ultimo precio de cierre para una lista de tickers .BA via Yahoo Finance."""
	if not tickers_ba:
		return {}

	prices = {}
	try:
		data = yf.Tickers(" ".join(tickers_ba))
		for ticker in tickers_ba:
			try:
				info = data.tickers[ticker].fast_info
				price = None
				try:
					price = info.last_price
				except Exception:
					pass
				if not price:
					try:
						price = info.previous_close
					except Exception:
						pass
				prices[ticker] = round(float(price), 2) if price else None
			except Exception:
				prices[ticker] = None
	except Exception:
		for t in tickers_ba:
			prices[t] = None

	return prices


def get_stock_prices():
	"""Retorna precios actuales en ARS para todas las posiciones de acciones abiertas."""
	stocks = Stock.find_all() or []
	if not stocks:
		return {"ok": True, "data": {}}

	tickers_ba = [f"{s.ticket_code}.BA" for s in stocks]
	raw = _fetch_prices(tickers_ba)

	result = {}
	for s in stocks:
		ba_ticker = f"{s.ticket_code}.BA"
		price = raw.get(ba_ticker)
		entry = {"price": price, "currency": "ARS"}
		if price is not None:
			pnl_pct = round((price - s.ppc) / s.ppc * 100, 2)
			current_value = round(price * s.quantity, 2)
			invested_value = round(s.ppc * s.quantity, 2)
			entry.update({
				"pnl_pct": pnl_pct,
				"current_value": current_value,
				"invested_value": invested_value,
				"pnl_ars": round(current_value - invested_value, 2),
			})
		result[s.ticket_code] = entry

	return {"ok": True, "data": result}


def get_bond_prices():
	"""Retorna precios actuales en ARS para todas las posiciones de bonos abiertas.
	La cobertura de bonos soberanos en Yahoo Finance es parcial; los no disponibles
	se retornan con price=null."""
	holdings = BondHolding.find_all() or []
	if not holdings:
		return {"ok": True, "data": {}}

	tickers_ba = [f"{h.bond_code}.BA" for h in holdings]
	raw = _fetch_prices(tickers_ba)

	result = {}
	for h in holdings:
		ba_ticker = f"{h.bond_code}.BA"
		raw_price = raw.get(ba_ticker)
		price = round(raw_price / 100, 6) if raw_price is not None else None
		entry = {"price": price, "currency": "ARS"}
		if price is not None:
			pnl_pct = round((price - h.ppc) / h.ppc * 100, 2) if h.ppc else None
			current_value = round(price * h.quantity, 2)
			invested_value = round(h.ppc * h.quantity, 2)
			entry.update({
				"pnl_pct": pnl_pct,
				"current_value": current_value,
				"invested_value": invested_value,
				"pnl_ars": round(current_value - invested_value, 2),
			})
		result[h.bond_code] = entry

	return {"ok": True, "data": result}
