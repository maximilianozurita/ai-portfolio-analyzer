<script>
	import { onMount } from 'svelte';
	import { get } from 'svelte/store';
	import { marked } from 'marked';
	import { getAIProviders, analyzePortfolio } from '$lib/api.js';
	import { marketPricesStocksStore, marketPricesBondsStore } from '$lib/stores.js';

	marked.use({ breaks: true });

	let providers = [];
	let selectedProvider = null;
	let selectedModel = null;
	let analysis = '';
	let analysisHtml = '';
	let loading = false;
	let error = '';
	let loadingProviders = true;
	let reportDate = '';
	let reportProvider = '';
	let reportModel = '';

	$: models = selectedProvider ? (providers.find((p) => p.id === selectedProvider)?.models ?? []) : [];
	$: if (selectedProvider && models.length > 0) {
		selectedModel = models[0].id;
	}

	onMount(async () => {
		try {
			providers = await getAIProviders();
			if (providers.length > 0) selectedProvider = providers[0].id;
		} catch (e) {
			error = e.message;
		} finally {
			loadingProviders = false;
		}
	});

	async function handleAnalyze() {
		if (!selectedProvider || !selectedModel) return;
		loading = true;
		analysis = '';
		analysisHtml = '';
		error = '';
		try {
			const marketPricesStocks = get(marketPricesStocksStore);
			const marketPricesBonds = get(marketPricesBondsStore);
			const result = await analyzePortfolio(
				selectedProvider,
				selectedModel,
				Object.keys(marketPricesStocks).length > 0 ? marketPricesStocks : null,
				Object.keys(marketPricesBonds).length > 0 ? marketPricesBonds : null
			);
			analysis = result.analysis;
			analysisHtml = marked.parse(analysis);
			reportDate = new Date().toLocaleDateString('es-AR');
			reportProvider = providers.find((p) => p.id === selectedProvider)?.name ?? selectedProvider;
			reportModel = models.find((m) => m.id === selectedModel)?.name ?? selectedModel;
		} catch (e) {
			error = e.message;
		} finally {
			loading = false;
		}
	}

	function downloadMd() {
		const date = reportDate.replace(/\//g, '-');
		const header = `# Informe de Portfolio — ${reportDate}\n\n> Generado con ${reportProvider} / ${reportModel}\n\n---\n\n`;
		const blob = new Blob([header + analysis], { type: 'text/markdown;charset=utf-8' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = `informe-portfolio-${date}.md`;
		a.click();
		URL.revokeObjectURL(url);
	}

	function downloadPdf() {
		const win = window.open('', '_blank');
		win.document.write(`<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Informe de Portfolio — ${reportDate}</title>
<style>
  *, *::before, *::after { box-sizing: border-box; }
  body { font-family: Georgia, 'Times New Roman', serif; max-width: 820px; margin: 48px auto; color: #111; line-height: 1.75; padding: 0 32px; font-size: 15px; }
  h1 { font-size: 1.9em; font-weight: 700; border-bottom: 2px solid #222; padding-bottom: 0.35em; margin-bottom: 0.2em; }
  h2 { font-size: 1.45em; font-weight: 700; margin-top: 2em; border-bottom: 1px solid #bbb; padding-bottom: 0.2em; }
  h3 { font-size: 1.15em; font-weight: 700; margin-top: 1.5em; }
  p { margin: 0.75em 0; }
  ul, ol { padding-left: 1.6em; margin: 0.5em 0; }
  li { margin-bottom: 0.3em; }
  strong { font-weight: 700; }
  em { font-style: italic; }
  hr { border: none; border-top: 1px solid #ccc; margin: 1.8em 0; }
  .meta { color: #555; font-size: 0.88em; margin: 0.4em 0 2em; font-family: sans-serif; }
  @media print { body { margin: 0; } }
</style>
</head>
<body>
<h1>Informe de Portfolio — ${reportDate}</h1>
<p class="meta">Generado con <strong>${reportProvider} / ${reportModel}</strong></p>
<hr>
${analysisHtml}
<script>window.onload = function(){ window.print(); }<\/script>
</body>
</html>`);
		win.document.close();
	}
</script>

<div class="space-y-6">
	<div>
		<h1 class="text-2xl font-bold text-white">Analizador de Portfolio con IA</h1>
		<p class="text-indigo-300 text-sm mt-1">
			Usá inteligencia artificial para obtener un análisis de tu portfolio actual.
		</p>
	</div>

	{#if loadingProviders}
		<p class="text-indigo-300 text-sm">Cargando providers disponibles...</p>
	{:else if providers.length === 0}
		<div class="bg-yellow-900/40 border border-yellow-700 rounded-lg p-4 text-yellow-200 text-sm">
			<strong>No hay providers configurados.</strong> Agregá al menos una API key en el archivo
			<code class="bg-yellow-900/60 px-1 rounded">.env</code> del backend:
			<pre class="mt-2 text-xs text-yellow-300">GEMINI_API_KEY=...
OPENAI_API_KEY=...
OPENROUTER_API_KEY=...</pre>
		</div>
	{:else}
		<div class="bg-indigo-950/60 border border-indigo-800 rounded-xl p-6 space-y-5">
			<div class="flex flex-wrap gap-4 items-end">
				<div class="flex flex-col gap-1.5">
					<label for="provider" class="text-indigo-200 text-sm font-medium">Provider</label>
					<select
						id="provider"
						bind:value={selectedProvider}
						class="bg-indigo-900 border border-indigo-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 min-w-[180px]"
					>
						{#each providers as provider}
							<option value={provider.id}>{provider.name}</option>
						{/each}
					</select>
				</div>

				<div class="flex flex-col gap-1.5">
					<label for="model" class="text-indigo-200 text-sm font-medium">Modelo</label>
					<select
						id="model"
						bind:value={selectedModel}
						class="bg-indigo-900 border border-indigo-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 min-w-[220px]"
					>
						{#each models as model}
							<option value={model.id}>{model.name}</option>
						{/each}
					</select>
				</div>

				<button
					on:click={handleAnalyze}
					disabled={loading || !selectedProvider || !selectedModel}
					class="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium rounded-lg text-sm transition-colors"
				>
					{loading ? 'Analizando...' : 'Analizar Portfolio'}
				</button>

				{#if analysis}
					<button
						on:click={downloadMd}
						class="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white font-medium rounded-lg text-sm transition-colors flex items-center gap-2"
					>
						<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
						</svg>
						Descargar .md
					</button>
					<button
						on:click={downloadPdf}
						class="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white font-medium rounded-lg text-sm transition-colors flex items-center gap-2"
					>
						<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
						</svg>
						Descargar PDF
					</button>
				{/if}
			</div>

			{#if error}
				<div class="bg-red-900/40 border border-red-700 rounded-lg p-3 text-red-300 text-sm">
					{error}
				</div>
			{/if}
		</div>

		{#if loading}
			<div class="flex items-center gap-3 text-indigo-300 text-sm py-4">
				<svg class="animate-spin h-5 w-5 text-indigo-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
					<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
					<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
				</svg>
				Generando informe, esto puede tardar unos segundos...
			</div>
		{/if}

		{#if analysis}
			<div class="bg-gray-900 border border-gray-700 rounded-xl p-8">
				<div class="flex items-center justify-between mb-6">
					<span class="text-indigo-400 text-xs font-semibold uppercase tracking-widest">Informe generado</span>
					<span class="text-gray-500 text-xs">{reportProvider} · {reportModel} · {reportDate}</span>
				</div>
				<div class="markdown-body">
					{@html analysisHtml}
				</div>
			</div>
		{/if}
	{/if}
</div>

<style>
	.markdown-body :global(h1) {
		font-size: 1.6em;
		font-weight: 700;
		color: #f1f5f9;
		border-bottom: 1px solid #374151;
		padding-bottom: 0.4em;
		margin: 1.2em 0 0.6em;
	}
	.markdown-body :global(h2) {
		font-size: 1.25em;
		font-weight: 700;
		color: #e2e8f0;
		border-bottom: 1px solid #1f2937;
		padding-bottom: 0.25em;
		margin: 1.6em 0 0.5em;
	}
	.markdown-body :global(h3) {
		font-size: 1.05em;
		font-weight: 600;
		color: #cbd5e1;
		margin: 1.3em 0 0.4em;
	}
	.markdown-body :global(p) {
		color: #d1d5db;
		line-height: 1.75;
		margin: 0.6em 0;
	}
	.markdown-body :global(ul),
	.markdown-body :global(ol) {
		color: #d1d5db;
		padding-left: 1.5em;
		margin: 0.5em 0;
	}
	.markdown-body :global(li) {
		margin-bottom: 0.3em;
		line-height: 1.65;
	}
	.markdown-body :global(strong) {
		color: #f8fafc;
		font-weight: 600;
	}
	.markdown-body :global(em) {
		color: #94a3b8;
	}
	.markdown-body :global(hr) {
		border: none;
		border-top: 1px solid #374151;
		margin: 1.5em 0;
	}
	.markdown-body :global(blockquote) {
		border-left: 3px solid #4f46e5;
		padding-left: 1em;
		margin: 1em 0;
		color: #94a3b8;
		font-style: italic;
	}
	.markdown-body :global(code) {
		background: #1f2937;
		color: #a5b4fc;
		padding: 0.1em 0.4em;
		border-radius: 4px;
		font-size: 0.875em;
	}
</style>
