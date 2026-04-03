<script>
	import { createEventDispatcher } from 'svelte';

	export let transactions = [];
	export let filter = '';

	const dispatch = createEventDispatcher();

	$: filtered = filter
		? transactions.filter((t) => t.ticket_code === filter)
		: transactions;

	function formatDate(ts) {
		if (!ts) return '-';
		return new Date(ts * 1000).toLocaleDateString('es-AR');
	}

	function formatNum(n, decimals = 2) {
		return Number(n).toLocaleString('es-AR', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
	}

	function handleRevert(t) {
		if (confirm(`¿Revertir transacción #${t.id}?`)) dispatch('revert', t.id);
	}

	function handleDelete(t) {
		if (confirm(`¿Eliminar transacción #${t.id}? Esta acción no se puede deshacer.`)) dispatch('delete', t.id);
	}
</script>

<div class="overflow-x-auto rounded-xl shadow">
	<table class="min-w-full bg-gray-900 text-sm">
		<thead class="bg-gray-800 text-gray-400 uppercase text-xs">
			<tr>
				<th class="px-4 py-3 text-left">ID</th>
				<th class="px-4 py-3 text-left">Ticker</th>
				<th class="px-4 py-3 text-left">Tipo</th>
				<th class="px-4 py-3 text-right">Cantidad</th>
				<th class="px-4 py-3 text-right">Precio</th>
				<th class="px-4 py-3 text-right">Cotiz. USD</th>
				<th class="px-4 py-3 text-right">Fecha</th>
				<th class="px-4 py-3 text-left">Broker</th>
				<th class="px-4 py-3 text-center">Acciones</th>
			</tr>
		</thead>
		<tbody>
			{#each filtered as t}
				<tr class="border-t border-gray-800 hover:bg-gray-800 transition-colors">
					<td class="px-4 py-3 text-gray-500">#{t.id}</td>
					<td class="px-4 py-3 font-semibold text-indigo-400">{t.ticket_code}</td>
					<td class="px-4 py-3">
						<span class="px-2 py-0.5 rounded-full text-xs font-medium {t.quantity > 0 ? 'bg-green-900/60 text-green-300' : 'bg-red-900/60 text-red-300'}">
							{t.quantity > 0 ? 'Compra' : 'Venta'}
						</span>
					</td>
					<td class="px-4 py-3 text-right text-gray-200">{formatNum(Math.abs(t.quantity), 0)}</td>
					<td class="px-4 py-3 text-right text-gray-200">{formatNum(t.unit_price, 4)}</td>
					<td class="px-4 py-3 text-right text-gray-200">{formatNum(t.usd_quote, 0)}</td>
					<td class="px-4 py-3 text-right text-gray-500">{formatDate(t.date)}</td>
					<td class="px-4 py-3 text-gray-500">{t.broker_name ?? '-'}</td>
					<td class="px-4 py-3 text-center space-x-2">
						<button
							on:click={() => handleRevert(t)}
							class="text-xs px-2 py-1 rounded bg-yellow-900/60 text-yellow-300 hover:bg-yellow-900 transition-colors"
						>Revertir</button>
						<button
							on:click={() => handleDelete(t)}
							class="text-xs px-2 py-1 rounded bg-red-900/60 text-red-300 hover:bg-red-900 transition-colors"
						>Eliminar</button>
					</td>
				</tr>
			{/each}
			{#if filtered.length === 0}
				<tr>
					<td colspan="9" class="px-4 py-8 text-center text-gray-600">Sin transacciones</td>
				</tr>
			{/if}
		</tbody>
	</table>
</div>
