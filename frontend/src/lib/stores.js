import { writable } from 'svelte/store';

// Cache de precios de mercado — persiste entre navegaciones hasta que el usuario refresca
export const marketPricesStocksStore = writable({});
export const marketPricesBondsStore = writable({});
