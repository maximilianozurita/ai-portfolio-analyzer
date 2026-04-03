<script>
	import { createEventDispatcher } from 'svelte';

	export let transactions = [];
	export let filter = '';

	const dispatch = createEventDispatcher();

	$: filtered = filter
		? transactions.filter((t) => t.bond_code === filter)
		: transactions;

	const typeConfig = {
		compra:       { label: 'Compra',       cls: 'bg-green-900/60 text-green-300' },
		venta:        { label: 'Venta',         cls: 'bg-red-900/60 text-red-300' },
		cupon:        { label: 'Cupón',         cls: 'bg-blue-900/60 text-blue-300' },
		amortizacion: { label: 'Amortización',  cls: 'bg-orange-900/60 text-orange-300' },
	};

	function formatDate(ts) {
		if (!ts) return '-';
		return new Date(ts * 1000).toLocaleDateString('es-AR');
	}

	function formatNum(n, decimals = 2) {
		return Number(n).toLocaleString('es-AR', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
	}

	function paridad(t) {
		if (!t.valor_tecnico || t.valor_tecnico === 0) return '-';
		return formatNum(t.unit_price / t.valor_tecnico, 6);
	}

	function handleRevert(t) {
		if (confirm(`¿Revertir operación #${t.id}?`)) dispatch('revert', t.id);
	}

	function handleDelete(t) {
		if (confirm(`¿Eliminar operación #${t.id}? Esta acción no se puede deshacer.`)) dispatch('delete', t.id);
	}
</script>

<div class="overflow-x-auto rounded-xl shadow">
	<table class="min-w-full bg-gray-900 text-sm">
		<thead class="bg-gray-800 text-gray-400 uppercase text-xs">
			<tr>
				<th class="px-4 py-3 text-left">ID</th>
				<th class="px-4 py-3 text-left">Bono</th>
				<th class="px-4 py-3 text-left">Tipo</th>
				<th class="px-4 py-3 text-right">Cantidad</th>
				<th class="px-4 py-3 text-right">Precio</th>
				<th class="px-4 py-3 text-right">VT</th>
				<th class="px-4 py-3 text-right">Paridad</th>
				<th class="px-4 py-3 text-right">Cotiz. USD</th>
				<th class="px-4 py-3 text-right">Fecha</th>
				<th class="px-4 py-3 text-left">Broker</th>
				<th class="px-4 py-3 text-center">Acciones</th>
			</tr>
		</thead>
		<tbody>
			{#each filtered as t}
				{@const cfg = typeConfig[t.transaction_type] ?? { label: t.transaction_type, cls: 'bg-gray-700 text-gray-300' }}
				<tr class="border-t border-gray-800 hover:bg-gray-800 transition-colors">
					<td class="px-4 py-3 text-gray-500">#{t.id}</td>
					<td class="px-4 py-3 font-semibold text-indigo-400">{t.bond_code}</td>
					<td class="px-4 py-3">
						<span class="px-2 py-0.5 rounded-full text-xs font-medium {cfg.cls}">
							{cfg.label}
						</span>
					</td>
					<td class="px-4 py-3 text-right text-gray-200">{formatNum(t.quantity, 0)}</td>
					<td class="px-4 py-3 text-right text-gray-200">{formatNum(t.unit_price, 4)}</td>
					<td class="px-4 py-3 text-right text-gray-500">{formatNum(t.valor_tecnico, 4)}</td>
					<td class="px-4 py-3 text-right text-gray-200">{paridad(t)}</td>
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
					<td colspan="11" class="px-4 py-8 text-center text-gray-600">Sin operaciones de bonos</td>
				</tr>
			{/if}
		</tbody>
	</table>
</div>
