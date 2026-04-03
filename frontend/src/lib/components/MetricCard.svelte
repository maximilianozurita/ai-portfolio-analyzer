<script>
	export let title;
	export let value;
	export let subtitle = '';
</script>

<div class="bg-gray-900 border border-gray-800 rounded-xl shadow p-6 flex flex-col gap-1">
	<span class="text-sm text-gray-400 font-medium uppercase tracking-wide">{title}</span>
	<span class="text-3xl font-bold text-gray-100">{value}</span>
	{#if subtitle}
		<span class="text-sm text-gray-500">{subtitle}</span>
	{/if}
</div>
