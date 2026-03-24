<script>
	import { onMount } from 'svelte';
	import { getTransactions, revertTransaction, deleteTransaction } from '$lib/api.js';
	import TransactionTable from '$lib/components/TransactionTable.svelte';

	let transactions = [];
	let error = '';
	let loading = true;
	let filter = '';

	async function load() {
		loading = true;
		error = '';
		try {
			transactions = (await getTransactions()) ?? [];
		} catch (e) {
			error = e.message;
		} finally {
			loading = false;
		}
	}

	onMount(load);

	$: tickers = [...new Set(transactions.map((t) => t.ticket_code))].sort();

	async function handleRevert(e) {
		try {
			await revertTransaction(e.detail);
			await load();
		} catch (err) {
			alert('Error al revertir: ' + err.message);
		}
	}

	async function handleDelete(e) {
		try {
			await deleteTransaction(e.detail);
			await load();
		} catch (err) {
			alert('Error al eliminar: ' + err.message);
		}
	}
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h1 class="text-2xl font-bold text-gray-100">Transacciones</h1>
		<a
			href="/transactions/new"
			class="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-500 transition-colors"
		>
			+ Nueva
		</a>
	</div>

	{#if !loading && transactions.length > 0}
		<div class="flex items-center gap-3">
			<label class="text-sm text-gray-400 font-medium">Filtrar por ticker:</label>
			<select
				bind:value={filter}
				class="border border-gray-700 bg-gray-800 text-gray-200 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
			>
				<option value="">Todos</option>
				{#each tickers as ticker}
					<option value={ticker}>{ticker}</option>
				{/each}
			</select>
		</div>
	{/if}

	{#if loading}
		<p class="text-gray-500">Cargando...</p>
	{:else if error}
		<p class="text-red-400">{error}</p>
	{:else}
		<TransactionTable {transactions} {filter} on:revert={handleRevert} on:delete={handleDelete} />
	{/if}
</div>
