<script>
	import { onMount } from 'svelte';
	import { get } from 'svelte/store';
	import { getStocks, getBondHoldings, getMarketPricesStocks, getMarketPricesBonds } from '$lib/api.js';
	import { marketPricesStocksStore, marketPricesBondsStore } from '$lib/stores.js';
	import MetricCard from '$lib/components/MetricCard.svelte';
	import CombinedDistributionChart from '$lib/components/charts/CombinedDistributionChart.svelte';
	import RendimientoChart from '$lib/components/charts/RendimientoChart.svelte';

	let stocks = [];
	let bonds = [];
	let marketPricesStocks = {};
	let marketPricesBonds = {};
	let loadingRV = false;
	let loadingRF = false;
	let error = '';
	let loading = true;

	marketPricesStocksStore.subscribe(v => { marketPricesStocks = v; });
	marketPricesBondsStore.subscribe(v => { marketPricesBonds = v; });

	onMount(async () => {
		marketPricesStocks = get(marketPricesStocksStore);
		marketPricesBonds = get(marketPricesBondsStore);
		try {
			[stocks, bonds] = await Promise.all([
				getStocks().then(d => d ?? []),
				getBondHoldings().then(d => d ?? [])
			]);
		} catch (e) {
			error = e.message;
		} finally {
			loading = false;
		}
	});

	async function fetchRV() {
		loadingRV = true;
		try {
			const prices = (await getMarketPricesStocks()) ?? {};
			marketPricesStocksStore.set(prices);
		} catch (e) { error = e.message; }
		finally { loadingRV = false; }
	}

	async function fetchRF() {
		loadingRF = true;
		try {
			const prices = (await getMarketPricesBonds()) ?? {};
			marketPricesBondsStore.set(prices);
		} catch (e) { error = e.message; }
		finally { loadingRF = false; }
	}

	// Renta Variable
	$: rvInvertido = stocks.reduce((sum, s) => sum + s.ppc * s.quantity, 0);
	$: rvActual = stocks.reduce((sum, s) => sum + (marketPricesStocks[s.ticket_code]?.current_value ?? s.ppc * s.quantity), 0);
	$: rvHasMarket = Object.values(marketPricesStocks).some(p => p?.current_value != null);

	// Renta Fija
	$: rfInvertido = bonds.reduce((sum, h) => sum + h.ppc * h.quantity, 0);
	$: rfActual = bonds.reduce((sum, h) => sum + (marketPricesBonds[h.bond_code]?.current_value ?? h.ppc * h.quantity), 0);
	$: rfHasMarket = Object.values(marketPricesBonds).some(p => p?.current_value != null);

	// Globales
	$: totalInvertido = rvInvertido + rfInvertido;
	$: totalActual = rvActual + rfActual;
	$: hasAnyMarket = rvHasMarket || rfHasMarket;
	$: pnlTotal = totalActual - totalInvertido;
	$: pnlPct = totalInvertido > 0 ? pnlTotal / totalInvertido * 100 : 0;

	$: hasRendimiento = stocks.some(s => marketPricesStocks[s.ticket_code]?.pnl_pct != null);
	$: hasAssets = stocks.length > 0 || bonds.length > 0;

	function formatNum(n, dec = 2) {
		return Number(n).toLocaleString('es-AR', { minimumFractionDigits: dec, maximumFractionDigits: dec });
	}
	function pnlColor(val) { return val >= 0 ? 'text-green-400' : 'text-red-400'; }
</script>

<div class="space-y-8">
	<h1 class="text-2xl font-bold text-gray-100">Dashboard</h1>

	{#if loading}
		<p class="text-gray-500">Cargando...</p>
	{:else if error}
		<p class="text-red-400">{error}</p>
	{:else}

		<!-- Métricas globales -->
		<div class="grid grid-cols-2 {hasAnyMarket ? 'lg:grid-cols-4' : ''} gap-4">
			<MetricCard title="Total Invertido" value="$ {formatNum(totalInvertido)}" subtitle="acciones + bonos" />
			<MetricCard title="Posiciones" value={stocks.length + bonds.length} subtitle="{stocks.length} tickers · {bonds.length} bonos" />
			{#if hasAnyMarket}
				<MetricCard title="Valor Actual" value="$ {formatNum(totalActual)}" />
				<MetricCard
					title="P&L Total"
					value="{pnlTotal >= 0 ? '+' : ''}$ {formatNum(pnlTotal)}"
					subtitle="{pnlTotal >= 0 ? '+' : ''}{formatNum(pnlPct)}%"
				/>
			{/if}
		</div>

		<!-- Resumen por categoría con botones de actualización -->
		{#if hasAssets}
			<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
				<!-- Renta Variable -->
				<div class="bg-gray-900 border border-gray-800 rounded-xl p-5 space-y-3">
					<div class="flex items-center justify-between">
						<h2 class="text-sm font-semibold text-gray-300 uppercase tracking-wide">Renta Variable</h2>
						<span class="text-xs text-gray-500">{stocks.length} ticker{stocks.length !== 1 ? 's' : ''}</span>
					</div>
					<div class="space-y-1">
						<div class="flex justify-between text-sm">
							<span class="text-gray-500">Invertido</span>
							<span class="text-gray-200 font-medium">$ {formatNum(rvInvertido)}</span>
						</div>
						{#if rvHasMarket}
							<div class="flex justify-between text-sm">
								<span class="text-gray-500">Valor actual</span>
								<span class="text-gray-100 font-medium">$ {formatNum(rvActual)}</span>
							</div>
							<div class="flex justify-between text-sm">
								<span class="text-gray-500">P&L</span>
								<span class="font-semibold {pnlColor(rvActual - rvInvertido)}">
									{rvActual - rvInvertido >= 0 ? '+' : ''}$ {formatNum(rvActual - rvInvertido)}
									<span class="text-xs ml-1">({rvActual - rvInvertido >= 0 ? '+' : ''}{formatNum(rvInvertido > 0 ? (rvActual - rvInvertido) / rvInvertido * 100 : 0)}%)</span>
								</span>
							</div>
						{/if}
					</div>
					<button
						on:click={fetchRV}
						disabled={loadingRV}
						class="w-full mt-1 px-3 py-1.5 bg-indigo-700 hover:bg-indigo-600 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition-colors"
					>
						{loadingRV ? 'Actualizando...' : rvHasMarket ? 'Refrescar precios' : 'Actualizar precios'}
					</button>
				</div>

				<!-- Renta Fija -->
				<div class="bg-gray-900 border border-gray-800 rounded-xl p-5 space-y-3">
					<div class="flex items-center justify-between">
						<h2 class="text-sm font-semibold text-gray-300 uppercase tracking-wide">Renta Fija</h2>
						<span class="text-xs text-gray-500">{bonds.length} bono{bonds.length !== 1 ? 's' : ''}</span>
					</div>
					<div class="space-y-1">
						<div class="flex justify-between text-sm">
							<span class="text-gray-500">Invertido</span>
							<span class="text-gray-200 font-medium">$ {formatNum(rfInvertido)}</span>
						</div>
						{#if rfHasMarket}
							<div class="flex justify-between text-sm">
								<span class="text-gray-500">Valor actual</span>
								<span class="text-gray-100 font-medium">$ {formatNum(rfActual)}</span>
							</div>
							<div class="flex justify-between text-sm">
								<span class="text-gray-500">P&L</span>
								<span class="font-semibold {pnlColor(rfActual - rfInvertido)}">
									{rfActual - rfInvertido >= 0 ? '+' : ''}$ {formatNum(rfActual - rfInvertido)}
									<span class="text-xs ml-1">({rfActual - rfInvertido >= 0 ? '+' : ''}{formatNum(rfInvertido > 0 ? (rfActual - rfInvertido) / rfInvertido * 100 : 0)}%)</span>
								</span>
							</div>
						{/if}
					</div>
					<button
						on:click={fetchRF}
						disabled={loadingRF}
						class="w-full mt-1 px-3 py-1.5 bg-indigo-700 hover:bg-indigo-600 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition-colors"
					>
						{loadingRF ? 'Actualizando...' : rfHasMarket ? 'Refrescar precios' : 'Actualizar precios'}
					</button>
				</div>
			</div>

			<!-- Gráficos: siempre 2 columnas para evitar layout shift -->
			<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
				<div class="bg-gray-900 border border-gray-800 rounded-xl shadow p-6">
					<h2 class="text-base font-semibold text-gray-300 mb-4">Distribución global</h2>
					<CombinedDistributionChart {stocks} {bonds} {marketPricesStocks} {marketPricesBonds} />
				</div>

				<div class="bg-gray-900 border border-gray-800 rounded-xl shadow p-6">
					{#if hasRendimiento}
						<h2 class="text-base font-semibold text-gray-300 mb-4">Rendimiento — Renta Variable</h2>
						<RendimientoChart {stocks} marketPrices={marketPricesStocks} />
					{:else}
						<h2 class="text-base font-semibold text-gray-300 mb-4">Rendimiento</h2>
						<p class="text-sm text-gray-600 mt-8 text-center">Actualizá los precios para ver el rendimiento por ticker.</p>
					{/if}
				</div>
			</div>
		{:else}
			<p class="text-gray-600">Sin posiciones abiertas.</p>
		{/if}
	{/if}
</div>
