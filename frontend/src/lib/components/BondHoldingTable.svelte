<script>
	export let holdings = [];
	export let marketPrices = {};

	function formatDate(ts) {
		if (!ts) return '-';
		return new Date(ts * 1000).toLocaleDateString('es-AR');
	}

	function formatNum(n, decimals = 2) {
		return Number(n).toLocaleString('es-AR', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
	}

	$: hasMarketData = Object.keys(marketPrices).length > 0;
</script>

<div class="overflow-x-auto rounded-xl shadow">
	<table class="min-w-full bg-gray-900 text-sm">
		<thead class="bg-gray-800 text-gray-400 uppercase text-xs">
			<tr>
				<th class="px-4 py-3 text-left">Bono</th>
				<th class="px-4 py-3 text-right">Cantidad</th>
				<th class="px-4 py-3 text-right">PPC</th>
				<th class="px-4 py-3 text-right">PPC Paridad</th>
				<th class="px-4 py-3 text-right">Invertido</th>
				{#if hasMarketData}
					<th class="px-4 py-3 text-right">Precio actual</th>
					<th class="px-4 py-3 text-right">Valor actual</th>
					<th class="px-4 py-3 text-right">P&amp;L %</th>
					<th class="px-4 py-3 text-right">P&amp;L ARS</th>
				{/if}
				<th class="px-4 py-3 text-right">Fecha pond.</th>
			</tr>
		</thead>
		<tbody>
			{#each holdings as h}
				{@const mp = marketPrices[h.bond_code]}
				<tr class="border-t border-gray-800 hover:bg-gray-800 transition-colors">
					<td class="px-4 py-3 font-semibold text-indigo-400">{h.bond_code}</td>
					<td class="px-4 py-3 text-right text-gray-200">{formatNum(h.quantity, 0)}</td>
					<td class="px-4 py-3 text-right text-gray-200">{formatNum(h.ppc, 4)}</td>
					<td class="px-4 py-3 text-right text-gray-200">{formatNum(h.ppc_paridad, 6)}</td>
					<td class="px-4 py-3 text-right font-medium text-gray-100">{formatNum(h.ppc * h.quantity)}</td>
					{#if hasMarketData}
						<td class="px-4 py-3 text-right text-gray-200">
							{mp?.price != null ? formatNum(mp.price, 2) : '—'}
						</td>
						<td class="px-4 py-3 text-right text-gray-100 font-medium">
							{mp?.current_value != null ? formatNum(mp.current_value) : '—'}
						</td>
						<td class="px-4 py-3 text-right font-semibold {mp?.pnl_pct != null ? (mp.pnl_pct >= 0 ? 'text-green-400' : 'text-red-400') : 'text-gray-600'}">
							{#if mp?.pnl_pct != null}
								{mp.pnl_pct >= 0 ? '+' : ''}{formatNum(mp.pnl_pct, 2)}%
							{:else}
								—
							{/if}
						</td>
						<td class="px-4 py-3 text-right font-medium {mp?.pnl_ars != null ? (mp.pnl_ars >= 0 ? 'text-green-400' : 'text-red-400') : 'text-gray-600'}">
							{#if mp?.pnl_ars != null}
								{mp.pnl_ars >= 0 ? '+' : ''}{formatNum(mp.pnl_ars)}
							{:else}
								—
							{/if}
						</td>
					{/if}
					<td class="px-4 py-3 text-right text-gray-500">{formatDate(h.weighted_date)}</td>
				</tr>
			{/each}
			{#if holdings.length === 0}
				<tr>
					<td colspan={hasMarketData ? 10 : 6} class="px-4 py-8 text-center text-gray-600">Sin posiciones de bonos</td>
				</tr>
			{/if}
		</tbody>
	</table>
</div>
