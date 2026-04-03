<script>
	import { onMount, onDestroy } from 'svelte';
	import * as echarts from 'echarts';

	export let holdings = [];
	export let marketPrices = {};

	let el;
	let chart;
	let mode = 'ppc';

	$: hasMarket = Object.values(marketPrices).some(p => p?.current_value != null);

	function buildOption(holdings, marketPrices, mode) {
		const data = holdings.map((h) => {
			const mp = marketPrices[h.bond_code];
			const value = (mode === 'market' && mp?.current_value != null)
				? Number(mp.current_value.toFixed(2))
				: Number((h.ppc * h.quantity).toFixed(2));
			return { name: h.bond_code, value };
		});
		return {
			backgroundColor: 'transparent',
			tooltip: { trigger: 'item', formatter: '{b}: {d}%', backgroundColor: '#1f2937', borderColor: '#374151', textStyle: { color: '#e5e7eb' } },
			legend: { bottom: 0, type: 'scroll', textStyle: { color: '#9ca3af' } },
			series: [{
				name: 'Distribución',
				type: 'pie',
				radius: ['45%', '70%'],
				data,
				emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.5)' } }
			}]
		};
	}

	onMount(() => {
		chart = echarts.init(el);
		chart.setOption(buildOption(holdings, marketPrices, mode));
		window.addEventListener('resize', () => chart.resize());
	});

	$: if (chart) chart.setOption(buildOption(holdings, marketPrices, mode));

	onDestroy(() => {
		window.removeEventListener('resize', () => chart?.resize());
		chart?.dispose();
	});
</script>

{#if hasMarket}
	<div class="flex gap-2 mb-3">
		<button
			on:click={() => { mode = 'ppc'; }}
			class="px-3 py-1 text-xs rounded-md font-medium transition-colors {mode === 'ppc' ? 'bg-indigo-700 text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'}"
		>
			Por PPC
		</button>
		<button
			on:click={() => { mode = 'market'; }}
			class="px-3 py-1 text-xs rounded-md font-medium transition-colors {mode === 'market' ? 'bg-indigo-700 text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'}"
		>
			Por precio actual
		</button>
	</div>
{/if}
<div bind:this={el} class="w-full h-72"></div>
