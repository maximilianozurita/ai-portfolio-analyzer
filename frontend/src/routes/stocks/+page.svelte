<script>
	import { onMount } from 'svelte';
	import { getStocks } from '$lib/api.js';
	import StockTable from '$lib/components/StockTable.svelte';

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
</script>

<div class="space-y-6">
	<h1 class="text-2xl font-bold text-gray-800">Holdings</h1>

	{#if loading}
		<p class="text-gray-400">Cargando...</p>
	{:else if error}
		<p class="text-red-500">{error}</p>
	{:else}
		<StockTable {stocks} />
	{/if}
</div>
