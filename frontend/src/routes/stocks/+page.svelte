<script>
	import { onMount } from 'svelte';
	import { get } from 'svelte/store';
	import { getStocks, importStockCsv, adjustStock, getMarketPricesStocks } from '$lib/api.js';
	import { marketPricesStocksStore } from '$lib/stores.js';
	import StockTable from '$lib/components/StockTable.svelte';
	import MetricCard from '$lib/components/MetricCard.svelte';
	import DistributionChart from '$lib/components/charts/DistributionChart.svelte';
	import RendimientoChart from '$lib/components/charts/RendimientoChart.svelte';

	let stocks = [];
	let marketPrices = {};
	let loadingPrices = false;
	let error = '';
	let loading = true;
	let tab = 'holdings';

	// Import CSV
	let csvFile = null;
	let csvResult = null;
	let csvUploading = false;

	// Adjust
	let adjTicket = '';
	let adjFactor = '';
	let adjResult = null;
	let adjSubmitting = false;

	$: adjPreview = adjTicket && adjFactor > 0
		? stocks.find(s => s.ticket_code === adjTicket)
		: null;

	$: totalInvertido = stocks.reduce((sum, s) => sum + s.ppc * s.quantity, 0);
	$: posicionesAbiertas = stocks.length;
	$: hasMarketData = Object.keys(marketPrices).length > 0;
	$: totalActual = stocks.reduce((sum, s) => sum + (marketPrices[s.ticket_code]?.current_value ?? s.ppc * s.quantity), 0);
	$: pnlTotal = totalActual - totalInvertido;
	$: pnlPct = totalInvertido > 0 ? pnlTotal / totalInvertido * 100 : 0;

	// Suscribirse al store para que el componente reaccione a cambios externos
	marketPricesStocksStore.subscribe(v => { marketPrices = v; });

	onMount(async () => {
		// Restaurar precios cacheados
		marketPrices = get(marketPricesStocksStore);
		try {
			stocks = (await getStocks()) ?? [];
		} catch (e) {
			error = e.message;
		} finally {
			loading = false;
		}
	});

	async function fetchMarketPrices() {
		loadingPrices = true;
		try {
			const prices = (await getMarketPricesStocks()) ?? {};
			marketPricesStocksStore.set(prices);
		} catch (e) {
			error = e.message;
		} finally {
			loadingPrices = false;
		}
	}

	async function handleCsvUpload() {
		if (!csvFile) return;
		csvResult = null;
		csvUploading = true;
		try {
			const res = await importStockCsv(csvFile);
			csvResult = { ok: res.status !== 'Error', msg: res.message, data: res.data };
		} catch (e) {
			csvResult = { ok: false, msg: e.message, data: null };
		} finally {
			csvUploading = false;
		}
	}

	async function handleAdjust() {
		if (!adjTicket || !adjFactor) return;
		adjResult = null;
		adjSubmitting = true;
		try {
			await adjustStock(adjTicket, Number(adjFactor));
			stocks = (await getStocks()) ?? [];
			adjResult = { ok: true, msg: `Stock de ${adjTicket} ajustado correctamente.` };
			adjFactor = '';
		} catch (e) {
			adjResult = { ok: false, msg: e.message };
		} finally {
			adjSubmitting = false;
		}
	}

	function formatNum(n, decimals = 2) {
		return Number(n).toLocaleString('es-AR', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
	}
</script>

<div class="space-y-6">
	<h1 class="text-2xl font-bold text-gray-100">Renta Variable</h1>

	<div class="flex border-b border-gray-700">
		<button
			on:click={() => { tab = 'holdings'; }}
			class="px-4 py-2 text-sm font-medium border-b-2 transition-colors
				{tab === 'holdings' ? 'border-indigo-400 text-indigo-400' : 'border-transparent text-gray-500 hover:text-gray-300'}"
		>
			Portfolio
		</button>
		<button
			on:click={() => { tab = 'adjust'; adjResult = null; }}
			class="px-4 py-2 text-sm font-medium border-b-2 transition-colors
				{tab === 'adjust' ? 'border-indigo-400 text-indigo-400' : 'border-transparent text-gray-500 hover:text-gray-300'}"
		>
			Ajustar posición
		</button>
		<button
			on:click={() => { tab = 'import'; csvResult = null; csvFile = null; }}
			class="px-4 py-2 text-sm font-medium border-b-2 transition-colors
				{tab === 'import' ? 'border-indigo-400 text-indigo-400' : 'border-transparent text-gray-500 hover:text-gray-300'}"
		>
			Importar posición inicial
		</button>
	</div>

	{#if tab === 'holdings'}
		{#if loading}
			<p class="text-gray-500">Cargando...</p>
		{:else if error}
			<p class="text-red-400">{error}</p>
		{:else}
			<div class="grid grid-cols-2 {hasMarketData ? 'lg:grid-cols-4' : ''} gap-4">
				<MetricCard title="Total Invertido" value="$ {formatNum(totalInvertido)}" />
				<MetricCard title="Posiciones Abiertas" value={posicionesAbiertas} subtitle="tickers activos" />
				{#if hasMarketData}
					<MetricCard title="Valor Actual" value="$ {formatNum(totalActual)}" />
					<MetricCard
						title="P&L Total"
						value="{pnlTotal >= 0 ? '+' : ''}$ {formatNum(pnlTotal)}"
						subtitle="{pnlTotal >= 0 ? '+' : ''}{formatNum(pnlPct)}%"
					/>
				{/if}
			</div>

			{#if stocks.length > 0}
				<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
					<div class="bg-gray-900 border border-gray-800 rounded-xl shadow p-6">
						<h2 class="text-base font-semibold text-gray-300 mb-4">Distribución por ticker</h2>
						<DistributionChart {stocks} {marketPrices} />
					</div>
					<div class="bg-gray-900 border border-gray-800 rounded-xl shadow p-6">
						{#if hasMarketData && stocks.some(s => marketPrices[s.ticket_code]?.pnl_pct != null)}
							<h2 class="text-base font-semibold text-gray-300 mb-4">Rendimiento por ticker</h2>
							<RendimientoChart {stocks} {marketPrices} />
						{:else}
							<h2 class="text-base font-semibold text-gray-300 mb-4">Rendimiento</h2>
							<p class="text-sm text-gray-600 mt-8 text-center">Actualizá los precios para ver el rendimiento por ticker.</p>
						{/if}
					</div>
				</div>
			{/if}

			<div class="flex items-center justify-between">
				<p class="text-xs text-gray-500">Precios via Yahoo Finance (BYMA · ARS)</p>
				<button
					on:click={fetchMarketPrices}
					disabled={loadingPrices}
					class="px-3 py-1.5 bg-indigo-700 hover:bg-indigo-600 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition-colors"
				>
					{loadingPrices ? 'Actualizando...' : 'Actualizar precios'}
				</button>
			</div>
			<StockTable {stocks} {marketPrices} />
		{/if}

	{:else if tab === 'adjust'}
		<div class="max-w-lg">
			<div class="bg-gray-900 border border-gray-800 rounded-xl shadow p-6 space-y-5">
				<div>
					<p class="text-sm text-gray-400 mb-1">
						Aplicá un factor multiplicador a la cantidad y al PPC de una posición.
					</p>
					<p class="text-xs text-gray-600">
						Usalo para splits (ej. split 2:1 → factor 2) o cambios de ratio de CEDEARs (ej. ratio cambia de 10 a 25 → factor 2.5).
					</p>
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-300 mb-1">Ticker</label>
					<select
						bind:value={adjTicket}
						class="w-full border border-gray-700 bg-gray-800 text-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
					>
						<option value="">— Seleccioná un ticker —</option>
						{#each stocks as s}
							<option value={s.ticket_code}>{s.ticket_code} — {s.name}</option>
						{/each}
					</select>
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-300 mb-1">Factor</label>
					<input
						type="number"
						bind:value={adjFactor}
						min="0.0001"
						step="any"
						placeholder="Ej: 2 para split 2:1"
						class="w-full border border-gray-700 bg-gray-800 text-gray-200 placeholder-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
					/>
				</div>

				{#if adjPreview && adjFactor > 0}
					<div class="bg-gray-800 border border-gray-700 rounded-lg p-4 text-sm space-y-2">
						<p class="font-medium text-gray-300">Vista previa</p>
						<div class="grid grid-cols-3 gap-2 text-xs text-gray-500">
							<span></span>
							<span class="text-center font-medium text-gray-400">Antes</span>
							<span class="text-center font-medium text-gray-400">Después</span>

							<span class="text-gray-400">Cantidad</span>
							<span class="text-center">{formatNum(adjPreview.quantity, 0)}</span>
							<span class="text-center text-indigo-400 font-medium">{formatNum(Math.round(adjPreview.quantity * adjFactor), 0)}</span>

							<span class="text-gray-400">PPC</span>
							<span class="text-center">{formatNum(adjPreview.ppc, 4)}</span>
							<span class="text-center text-indigo-400 font-medium">{formatNum(adjPreview.ppc / adjFactor, 4)}</span>
						</div>
					</div>
				{/if}

				{#if adjResult}
					<div class="rounded-lg px-4 py-3 text-sm {adjResult.ok ? 'bg-green-950 border border-green-800 text-green-300' : 'bg-red-950 border border-red-800 text-red-300'}">
						{adjResult.msg}
					</div>
				{/if}

				<div class="pt-2">
					<button
						on:click={handleAdjust}
						disabled={!adjTicket || !adjFactor || adjFactor <= 0 || adjSubmitting}
						class="px-5 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-500 disabled:opacity-50 transition-colors"
					>
						{adjSubmitting ? 'Aplicando...' : 'Aplicar ajuste'}
					</button>
				</div>
			</div>
		</div>

	{:else}
		<div class="max-w-lg">
			<div class="bg-gray-900 border border-gray-800 rounded-xl shadow p-6 space-y-5">
				<div>
					<p class="text-sm text-gray-400 mb-1">
						Usá esta opción para cargar tu portfolio actual sin necesidad de ingresar el historial de transacciones.
					</p>
					<p class="text-xs text-gray-600 mb-3">
						Solo se puede importar una vez por ticker. Si ya existe stock para un ticker, esa fila se saltea.
					</p>
					<pre class="bg-gray-800 border border-gray-700 rounded-lg p-3 text-xs text-gray-300 overflow-x-auto">ticket_code,quantity,ppc,weighted_date
AAPL,10,150.50,2023-06-15
MSFT,5,320.00,2022-11-01</pre>
					<p class="text-xs text-gray-600 mt-2">
						<code class="text-gray-400">weighted_date</code>: fecha promedio de compra en formato <code class="text-gray-400">YYYY-MM-DD</code>.
					</p>
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-300 mb-1">Archivo CSV</label>
					<input
						type="file"
						accept=".csv"
						on:change={(e) => { csvFile = e.target.files[0]; csvResult = null; }}
						class="w-full text-sm text-gray-500 file:mr-3 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-indigo-900 file:text-indigo-300 hover:file:bg-indigo-800"
					/>
				</div>

				{#if csvResult}
					<div class="rounded-lg px-4 py-3 text-sm {csvResult.ok ? 'bg-green-950 border border-green-800 text-green-300' : 'bg-red-950 border border-red-800 text-red-300'}">
						<p class="font-medium">{csvResult.msg}</p>
						{#if csvResult.data?.errors?.length > 0}
							<ul class="mt-2 space-y-1 list-disc list-inside">
								{#each csvResult.data.errors as err}
									<li>{err}</li>
								{/each}
							</ul>
						{/if}
					</div>
				{/if}

				<div class="flex gap-3 pt-2">
					<button
						on:click={handleCsvUpload}
						disabled={!csvFile || csvUploading}
						class="px-5 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-500 disabled:opacity-50 transition-colors"
					>
						{csvUploading ? 'Importando...' : 'Importar'}
					</button>
				</div>
			</div>
		</div>
	{/if}
</div>
