<script>
	import { onMount, onDestroy } from 'svelte';
	import * as echarts from 'echarts';

	export let stocks = [];

	let el;
	let chart;

	function buildOption(stocks) {
		return {
			backgroundColor: 'transparent',
			tooltip: { trigger: 'axis', backgroundColor: '#1f2937', borderColor: '#374151', textStyle: { color: '#e5e7eb' } },
			xAxis: { type: 'category', data: stocks.map((s) => s.ticket_code), axisLabel: { color: '#9ca3af' }, axisLine: { lineStyle: { color: '#374151' } } },
			yAxis: { type: 'value', name: 'PPC', nameTextStyle: { color: '#9ca3af' }, axisLabel: { color: '#9ca3af' }, axisLine: { lineStyle: { color: '#374151' } }, splitLine: { lineStyle: { color: '#1f2937' } } },
			series: [{
				name: 'PPC',
				type: 'bar',
				data: stocks.map((s) => Number(s.ppc)),
				itemStyle: { color: '#6366f1' }
			}]
		};
	}

	onMount(() => {
		chart = echarts.init(el);
		chart.setOption(buildOption(stocks));
		window.addEventListener('resize', () => chart.resize());
	});

	$: if (chart) chart.setOption(buildOption(stocks));

	onDestroy(() => {
		window.removeEventListener('resize', () => chart?.resize());
		chart?.dispose();
	});
</script>

<div bind:this={el} class="w-full h-72"></div>
