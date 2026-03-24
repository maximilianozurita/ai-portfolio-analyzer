<script>
	import { onMount } from 'svelte';
	import { getBondHoldings, getBondTransactions, revertBondTransaction, deleteBondTransaction, importBondCsv } from '$lib/api.js';
	import MetricCard from '$lib/components/MetricCard.svelte';
	import BondDistributionChart from '$lib/components/charts/BondDistributionChart.svelte';
	import BondPpcParidadChart from '$lib/components/charts/BondPpcParidadChart.svelte';
	import BondHoldingTable from '$lib/components/BondHoldingTable.svelte';
	import BondTransactionTable from '$lib/components/BondTransactionTable.svelte';

	let holdings = [];
	let transactions = [];
	let error = '';
	let loading = true;
	let tab = 'holdings';

	// Import CSV
	let csvFile = null;
	let csvResult = null;
	let csvUploading = false;

	$: totalInvertido = holdings.reduce((sum, h) => sum + (h.ppc * h.quantity) / 100, 0);
	$: posicionesAbiertas = holdings.length;

	function formatNum(n) {
		return Number(n).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
	}

	onMount(async () => {
		try {
			[holdings, transactions] = await Promise.all([
				getBondHoldings().then(d => d ?? []),
				getBondTransactions().then(d => d ?? [])
			]);
		} catch (e) {
			error = e.message;
		} finally {
			loading = false;
		}
	});

	async function refresh() {
		try {
			[holdings, transactions] = await Promise.all([
				getBondHoldings().then(d => d ?? []),
				getBondTransactions().then(d => d ?? [])
			]);
		} catch (e) {
			error = e.message;
		}
	}

	async function handleRevert(event) {
		try {
			await revertBondTransaction(event.detail);
			await refresh();
		} catch (e) {
			error = e.message;
		}
	}

	async function handleDelete(event) {
		try {
			await deleteBondTransaction(event.detail);
			await refresh();
		} catch (e) {
			error = e.message;
		}
	}

	async function handleCsvUpload() {
		if (!csvFile) return;
		csvResult = null;
		csvUploading = true;
		try {
			const res = await importBondCsv(csvFile);
			csvResult = { ok: res.status !== 'Error', msg: res.message, data: res.data };
			if (csvResult.ok) holdings = (await getBondHoldings()) ?? [];
		} catch (e) {
			csvResult = { ok: false, msg: e.message, data: null };
		} finally {
			csvUploading = false;
		}
	}
</script>

<div class="space-y-6">
	<h1 class="text-2xl font-bold text-gray-100">Bonos</h1>

	{#if error}
		<div class="bg-red-950 border border-red-800 text-red-300 rounded-lg px-4 py-3 text-sm">{error}</div>
	{/if}

	<div class="flex border-b border-gray-700">
		<button
			on:click={() => { tab = 'holdings'; }}
			class="px-4 py-2 text-sm font-medium border-b-2 transition-colors
				{tab === 'holdings' ? 'border-indigo-400 text-indigo-400' : 'border-transparent text-gray-500 hover:text-gray-300'}"
		>
			Holdings
		</button>
		<button
			on:click={() => { tab = 'transactions'; }}
			class="px-4 py-2 text-sm font-medium border-b-2 transition-colors
				{tab === 'transactions' ? 'border-indigo-400 text-indigo-400' : 'border-transparent text-gray-500 hover:text-gray-300'}"
		>
			Operaciones
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
		{:else}
			<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
				<MetricCard title="Total Invertido" value="$ {formatNum(totalInvertido)}" />
				<MetricCard title="Posiciones Abiertas" value={posicionesAbiertas} subtitle="bonos activos" />
			</div>

			{#if holdings.length > 0}
				<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
					<div class="bg-gray-900 border border-gray-800 rounded-xl shadow p-6">
						<h2 class="text-base font-semibold text-gray-300 mb-4">Distribución por bono</h2>
						<BondDistributionChart {holdings} />
					</div>
					<div class="bg-gray-900 border border-gray-800 rounded-xl shadow p-6">
						<h2 class="text-base font-semibold text-gray-300 mb-4">PPC Paridad por bono</h2>
						<BondPpcParidadChart {holdings} />
					</div>
				</div>
			{/if}

			<BondHoldingTable {holdings} />
		{/if}

	{:else if tab === 'transactions'}
		{#if loading}
			<p class="text-gray-500">Cargando...</p>
		{:else}
			<BondTransactionTable {transactions} on:revert={handleRevert} on:delete={handleDelete} />
		{/if}

	{:else}
		<div class="max-w-lg">
			<div class="bg-gray-900 border border-gray-800 rounded-xl shadow p-6 space-y-5">
				<div>
					<p class="text-sm text-gray-400 mb-1">
						Usá esta opción para cargar tu posición actual sin necesidad de ingresar el historial de operaciones.
					</p>
					<p class="text-xs text-gray-600 mb-3">
						Solo se puede importar una vez por bono. Si ya existe posición para un código, esa fila se saltea.
					</p>
					<pre class="bg-gray-800 border border-gray-700 rounded-lg p-3 text-xs text-gray-300 overflow-x-auto">bond_code,quantity,ppc,ppc_paridad,weighted_date
AL30,10,85.5000,0.906681,2024-03-24
GD35,5,72.0000,0.813559,2024-04-10</pre>
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
