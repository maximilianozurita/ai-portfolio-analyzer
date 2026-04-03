<script>
	import { onMount, onDestroy } from 'svelte';
	import * as echarts from 'echarts';

	export let stocks = [];
	export let marketPrices = {};

	let el;
	let chart;

	function buildOption(stocks, marketPrices) {
		const items = stocks
			.filter(s => marketPrices[s.ticket_code]?.pnl_pct != null)
			.map(s => ({ name: s.ticket_code, value: marketPrices[s.ticket_code].pnl_pct }));

		return {
			backgroundColor: 'transparent',
			tooltip: {
				trigger: 'axis',
				backgroundColor: '#1f2937',
				borderColor: '#374151',
				textStyle: { color: '#e5e7eb' },
				formatter: (params) => {
					const v = params[0].value;
					return `${params[0].name}: ${v >= 0 ? '+' : ''}${v.toFixed(2)}%`;
				}
			},
			xAxis: {
				type: 'category',
				data: items.map(i => i.name),
				axisLabel: { color: '#9ca3af' },
				axisLine: { lineStyle: { color: '#374151' } }
			},
			yAxis: {
				type: 'value',
				axisLabel: { color: '#9ca3af', formatter: '{value}%' },
				axisLine: { lineStyle: { color: '#374151' } },
				splitLine: { lineStyle: { color: '#1f2937' } }
			},
			series: [{
				type: 'bar',
				data: items.map(i => ({
					value: i.value,
					itemStyle: { color: i.value >= 0 ? '#4ade80' : '#f87171' }
				}))
			}]
		};
	}

	onMount(() => {
		chart = echarts.init(el);
		chart.setOption(buildOption(stocks, marketPrices));
		window.addEventListener('resize', () => chart.resize());
	});

	$: if (chart) chart.setOption(buildOption(stocks, marketPrices));

	onDestroy(() => {
		window.removeEventListener('resize', () => chart?.resize());
		chart?.dispose();
	});
</script>

<div bind:this={el} class="w-full h-72"></div>
