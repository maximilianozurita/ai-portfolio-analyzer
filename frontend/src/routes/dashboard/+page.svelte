<script>
	import { onMount } from 'svelte';
	import { getStocks } from '$lib/api.js';
	import MetricCard from '$lib/components/MetricCard.svelte';
	import DistributionChart from '$lib/components/charts/DistributionChart.svelte';
	import PpcBarChart from '$lib/components/charts/PpcBarChart.svelte';

	let stocks = [];
	let error = '';
	let loading = true;

	onMount(async () => {
		try {
			stocks = (await getStocks()) ?? [];
		} catch (e) {
			error = e.message;
		} finally {
			loading = false;
		}
	});

	$: totalInvertido = stocks.reduce((sum, s) => sum + s.ppc * s.quantity, 0);
	$: posicionesAbiertas = stocks.length;

	function formatNum(n) {
		return Number(n).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
	}
</script>

<div class="space-y-8">
	<h1 class="text-2xl font-bold text-gray-800">Dashboard</h1>

	{#if loading}
		<p class="text-gray-400">Cargando...</p>
	{:else if error}
		<p class="text-red-500">{error}</p>
	{:else}
		<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
			<MetricCard title="Total Invertido" value="$ {formatNum(totalInvertido)}" />
			<MetricCard title="Posiciones Abiertas" value={posicionesAbiertas} subtitle="tickers activos" />
		</div>

		{#if stocks.length > 0}
			<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
				<div class="bg-white rounded-xl shadow p-6">
					<h2 class="text-base font-semibold text-gray-700 mb-4">Distribución por ticker</h2>
					<DistributionChart {stocks} />
				</div>
				<div class="bg-white rounded-xl shadow p-6">
					<h2 class="text-base font-semibold text-gray-700 mb-4">PPC por ticker</h2>
					<PpcBarChart {stocks} />
				</div>
			</div>
		{:else}
			<p class="text-gray-400">Sin posiciones abiertas.</p>
		{/if}
	{/if}
</div>
