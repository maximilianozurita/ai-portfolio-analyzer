<script>
	import { onMount, onDestroy } from 'svelte';
	import * as echarts from 'echarts';

	export let holdings = [];

	let el;
	let chart;

	function buildOption(holdings) {
		return {
			backgroundColor: 'transparent',
			tooltip: { trigger: 'axis', backgroundColor: '#1f2937', borderColor: '#374151', textStyle: { color: '#e5e7eb' } },
			xAxis: { type: 'category', data: holdings.map((h) => h.bond_code), axisLabel: { color: '#9ca3af' }, axisLine: { lineStyle: { color: '#374151' } } },
			yAxis: { type: 'value', name: 'PPC Paridad', nameTextStyle: { color: '#9ca3af' }, axisLabel: { color: '#9ca3af' }, axisLine: { lineStyle: { color: '#374151' } }, splitLine: { lineStyle: { color: '#1f2937' } } },
			series: [{
				name: 'PPC Paridad',
				type: 'bar',
				data: holdings.map((h) => Number(h.ppc_paridad)),
				itemStyle: { color: '#6366f1' }
			}]
		};
	}

	onMount(() => {
		chart = echarts.init(el);
		chart.setOption(buildOption(holdings));
		window.addEventListener('resize', () => chart.resize());
	});

	$: if (chart) chart.setOption(buildOption(holdings));

	onDestroy(() => {
		window.removeEventListener('resize', () => chart?.resize());
		chart?.dispose();
	});
</script>

<div bind:this={el} class="w-full h-72"></div>
