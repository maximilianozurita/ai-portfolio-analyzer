import { PUBLIC_API_URL } from '$env/static/public';

const API_URL = PUBLIC_API_URL || 'http://localhost:5001';

async function request(path, options = {}) {
	const res = await fetch(`${API_URL}${path}`, options);
	const json = await res.json();
	if (!res.ok || json.status === 'Error') {
		throw new Error(json.message || 'Error en la solicitud');
	}
	return json.data;
}

export function getStocks() {
	return request('/stocks');
}

export function getTransactions() {
	return request('/transactions');
}

export function addTransaction(data) {
	return request('/transactions', {
		method: 'PUT',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(data)
	});
}

export function deleteTransaction(id) {
	return request(`/transactions/${id}/delete`, { method: 'POST' });
}

export function revertTransaction(id) {
	return request(`/transactions/${id}/revert`, { method: 'POST' });
}

export function getTickets() {
	return request('/tickets');
}

export async function importTransactionsCsv(file) {
	const form = new FormData();
	form.append('file', file);
	const res = await fetch(`${API_URL}/transactions/import`, { method: 'POST', body: form });
	const json = await res.json();
	if (json.status === 'Error') throw new Error(json.message);
	return json;
}

export function adjustStock(ticket_code, factor) {
	return request(`/stocks/${ticket_code}/adjust`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ factor })
	});
}

export async function importStockCsv(file) {
	const form = new FormData();
	form.append('file', file);
	const res = await fetch(`${API_URL}/stocks/import`, { method: 'POST', body: form });
	const json = await res.json();
	if (json.status === 'Error') throw new Error(json.message);
	return json;
}

export async function importBondCsv(file) {
	const form = new FormData();
	form.append('file', file);
	const res = await fetch(`${API_URL}/bond-holdings/import`, { method: 'POST', body: form });
	const json = await res.json();
	if (json.status === 'Error') throw new Error(json.message);
	return json;
}

export function getBondHoldings() {
	return request('/bond-holdings');
}

export function getBondTransactions(bond_code) {
	const query = bond_code ? `?bond_code=${bond_code}` : '';
	return request(`/bond-transactions${query}`);
}

export function addBondTransaction(data) {
	return request('/bond-transactions', {
		method: 'PUT',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(data)
	});
}

export function deleteBondTransaction(id) {
	return request(`/bond-transactions/${id}/delete`, { method: 'POST' });
}

export function revertBondTransaction(id) {
	return request(`/bond-transactions/${id}/revert`, { method: 'POST' });
}

export function getMarketPricesStocks() {
	return request('/market/prices/stocks');
}

export function getMarketPricesBonds() {
	return request('/market/prices/bonds');
}

export function getAIProviders() {
	return request('/ai/providers');
}

export function analyzePortfolio(provider, model, marketPricesStocks = null, marketPricesBonds = null) {
	return request('/ai/analyze', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({
			provider,
			model,
			market_prices_stocks: marketPricesStocks,
			market_prices_bonds: marketPricesBonds
		})
	});
}
