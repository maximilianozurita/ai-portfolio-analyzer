import json
import requests
import urllib3
import yfinance as yf
from src.models.stock import Stock
from src.models.bond_holding import BondHolding

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _fetch_bond_prices_byma() -> dict:
	"""Obtiene precios de bonos desde BYMA Open Data (sin auth, ~20 min delay).
	Retorna {bond_code_upper: price_ars} o {} si la API falla."""
	url = "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/public-bonds"
	payload = json.dumps({"excludeZeroPxAndQty": False, "T2": True, "T1": False, "T0": False})
	headers = {
		"Content-Type": "application/json",
		"Accept": "application/json, text/plain, */*",
		"Origin": "https://open.bymadata.com.ar",
		"Referer": "https://open.bymadata.com.ar/",
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
	}
	try:
		resp = requests.post(url, data=payload, headers=headers, timeout=15, verify=False)
		resp.raise_for_status()
		items = resp.json().get("data") or []
		prices = {}
		for item in items:
			symbol = item.get("simbolo") or item.get("symbol") or ""
			price = item.get("ultimoPrecio") or item.get("precioPromedioPonderado")
			if symbol and price:
				prices[symbol.strip().upper()] = float(price)
		return prices
	except Exception:
		return {}


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
	Intenta BYMA Open Data primero (cobertura completa, ~20 min delay).
	Para los no encontrados en BYMA, usa Yahoo Finance como fallback."""
	holdings = BondHolding.find_all() or []
	if not holdings:
		return {"ok": True, "data": {}}

	byma_prices = _fetch_bond_prices_byma()

	missing_tickers_ba = [
		f"{h.bond_code}.BA"
		for h in holdings
		if h.bond_code.upper() not in byma_prices
	]
	yf_raw = _fetch_prices(missing_tickers_ba) if missing_tickers_ba else {}

	result = {}
	for h in holdings:
		code_upper = h.bond_code.upper()
		if code_upper in byma_prices:
			raw_price = byma_prices[code_upper]
		else:
			raw_price = yf_raw.get(f"{h.bond_code}.BA")

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
