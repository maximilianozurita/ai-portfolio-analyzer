<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { getTickets, addTransaction, importTransactionsCsv, addBondTransaction } from '$lib/api.js';

	let outerTab = 'accion'; // 'accion' | 'bono'

	// ---- Acción / CEDEAR ----
	let tickets = [];
	let innerTab = 'manual'; // 'manual' | 'csv'
	let stockError = '';
	let stockSuccess = '';
	let stockSubmitting = false;
	let csvFile = null;
	let csvResult = null;
	let csvUploading = false;

	let stockForm = {
		ticket_code: '',
		tipo: 'compra',
		quantity: '',
		unit_price: '',
		usd_quote: '',
		date: '',
		broker_name: ''
	};

	onMount(async () => {
		try {
			tickets = (await getTickets()) ?? [];
			if (tickets.length > 0) stockForm.ticket_code = tickets[0].ticket_code;
		} catch (e) {
			stockError = 'Error al cargar tickers: ' + e.message;
		}
	});

	async function handleStockSubmit() {
		stockError = '';
		stockSuccess = '';
		stockSubmitting = true;
		try {
			const qty = Number(stockForm.quantity);
			const dateTs = Math.floor(new Date(stockForm.date).getTime() / 1000);
			const data = {
				ticket_code: stockForm.ticket_code,
				quantity: stockForm.tipo === 'venta' ? -qty : qty,
				unit_price: Number(stockForm.unit_price),
				usd_quote: Number(stockForm.usd_quote),
				date: dateTs
			};
			if (stockForm.broker_name.trim()) data.broker_name = stockForm.broker_name.trim();
			await addTransaction(data);
			stockSuccess = 'Transacción registrada correctamente.';
			setTimeout(() => goto('/transactions'), 1200);
		} catch (e) {
			stockError = e.message;
		} finally {
			stockSubmitting = false;
		}
	}

	async function handleCsvUpload() {
		if (!csvFile) return;
		csvResult = null;
		csvUploading = true;
		try {
			const res = await importTransactionsCsv(csvFile);
			csvResult = { ok: res.status !== 'Error', msg: res.message, data: res.data };
		} catch (e) {
			csvResult = { ok: false, msg: e.message, data: null };
		} finally {
			csvUploading = false;
		}
	}

	// ---- Bono ----
	let bondError = '';
	let bondSuccess = '';
	let bondSubmitting = false;

	let bondForm = {
		bond_code: '',
		transaction_type: 'compra',
		quantity: '',
		unit_price: '',
		valor_tecnico: '',
		interest_currency: 'USD',
		amortization_currency: 'USD',
		usd_quote: '',
		date: '',
		broker_name: ''
	};

	$: isCupon = bondForm.transaction_type === 'cupon';
	$: paridad = (bondForm.unit_price && bondForm.valor_tecnico && Number(bondForm.valor_tecnico) > 0)
		? (Number(bondForm.unit_price) / Number(bondForm.valor_tecnico)).toFixed(6)
		: null;

	async function handleBondSubmit() {
		bondError = '';
		bondSuccess = '';
		bondSubmitting = true;
		try {
			const dateTs = Math.floor(new Date(bondForm.date).getTime() / 1000);
			const data = {
				bond_code: bondForm.bond_code.trim().toUpperCase(),
				transaction_type: bondForm.transaction_type,
				quantity: isCupon ? 0 : Number(bondForm.quantity),
				unit_price: Number(bondForm.unit_price),
				valor_tecnico: Number(bondForm.valor_tecnico),
				interest_currency: bondForm.interest_currency,
				amortization_currency: bondForm.amortization_currency,
				usd_quote: Number(bondForm.usd_quote),
				date: dateTs
			};
			if (bondForm.broker_name.trim()) data.broker_name = bondForm.broker_name.trim();
			await addBondTransaction(data);
			bondSuccess = 'Operación registrada correctamente.';
			setTimeout(() => goto('/bonds'), 1200);
		} catch (e) {
			bondError = e.message;
		} finally {
			bondSubmitting = false;
		}
	}

	const inputCls = 'w-full border border-gray-700 bg-gray-800 text-gray-200 placeholder-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500';
</script>

<div class="max-w-lg space-y-6">
	<h1 class="text-2xl font-bold text-gray-100">Nueva Operación</h1>

	<!-- Tabs externos: Acción / Bono -->
	<div class="flex border-b border-gray-700">
		<button
			on:click={() => { outerTab = 'accion'; stockError = ''; stockSuccess = ''; }}
			class="px-4 py-2 text-sm font-medium border-b-2 transition-colors
				{outerTab === 'accion' ? 'border-indigo-400 text-indigo-400' : 'border-transparent text-gray-500 hover:text-gray-300'}"
		>
			Acción / CEDEAR
		</button>
		<button
			on:click={() => { outerTab = 'bono'; bondError = ''; bondSuccess = ''; }}
			class="px-4 py-2 text-sm font-medium border-b-2 transition-colors
				{outerTab === 'bono' ? 'border-indigo-400 text-indigo-400' : 'border-transparent text-gray-500 hover:text-gray-300'}"
		>
			Bono
		</button>
	</div>

	<!-- === ACCIÓN / CEDEAR === -->
	{#if outerTab === 'accion'}
		<div class="flex border-b border-gray-700">
			<button
				on:click={() => { innerTab = 'manual'; stockError = ''; stockSuccess = ''; }}
				class="px-4 py-2 text-sm font-medium border-b-2 transition-colors
					{innerTab === 'manual' ? 'border-indigo-400 text-indigo-400' : 'border-transparent text-gray-500 hover:text-gray-300'}"
			>
				Manual
			</button>
			<button
				on:click={() => { innerTab = 'csv'; stockError = ''; stockSuccess = ''; csvResult = null; }}
				class="px-4 py-2 text-sm font-medium border-b-2 transition-colors
					{innerTab === 'csv' ? 'border-indigo-400 text-indigo-400' : 'border-transparent text-gray-500 hover:text-gray-300'}"
			>
				Importar CSV
			</button>
		</div>

		{#if innerTab === 'manual'}
			{#if stockError}
				<div class="bg-red-950 border border-red-800 text-red-300 rounded-lg px-4 py-3 text-sm">{stockError}</div>
			{/if}
			{#if stockSuccess}
				<div class="bg-green-950 border border-green-800 text-green-300 rounded-lg px-4 py-3 text-sm">{stockSuccess}</div>
			{/if}

			<form on:submit|preventDefault={handleStockSubmit} class="bg-gray-900 border border-gray-800 rounded-xl shadow p-6 space-y-5">
				<div>
					<label class="block text-sm font-medium text-gray-300 mb-1">Ticker</label>
					<select bind:value={stockForm.ticket_code} required class={inputCls}>
						{#each tickets as t}
							<option value={t.ticket_code}>{t.ticket_code} — {t.name}</option>
						{/each}
					</select>
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-300 mb-1">Tipo</label>
					<div class="flex gap-6">
						<label class="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
							<input type="radio" bind:group={stockForm.tipo} value="compra" class="accent-indigo-500" />
							Compra
						</label>
						<label class="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
							<input type="radio" bind:group={stockForm.tipo} value="venta" class="accent-indigo-500" />
							Venta
						</label>
					</div>
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-300 mb-1">Cantidad</label>
					<input type="number" bind:value={stockForm.quantity} min="1" step="1" required placeholder="Ej: 100" class={inputCls} />
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-300 mb-1">Precio unitario</label>
					<input type="number" bind:value={stockForm.unit_price} min="0" step="any" required placeholder="Ej: 1250.50" class={inputCls} />
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-300 mb-1">Cotización USD</label>
					<input type="number" bind:value={stockForm.usd_quote} min="0" step="1" required placeholder="Ej: 1000" class={inputCls} />
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-300 mb-1">Fecha</label>
					<input type="date" bind:value={stockForm.date} required class={inputCls} />
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-300 mb-1">Broker <span class="text-gray-600">(opcional)</span></label>
					<input type="text" bind:value={stockForm.broker_name} placeholder="Ej: IOL, Balanz..." class={inputCls} />
				</div>

				<div class="flex gap-3 pt-2">
					<button
						type="submit"
						disabled={stockSubmitting}
						class="px-5 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-500 disabled:opacity-50 transition-colors"
					>
						{stockSubmitting ? 'Guardando...' : 'Guardar'}
					</button>
					<a href="/transactions" class="px-5 py-2 border border-gray-700 text-gray-400 rounded-lg text-sm font-medium hover:bg-gray-800 transition-colors">
						Cancelar
					</a>
				</div>
			</form>

		{:else}
			<div class="bg-gray-900 border border-gray-800 rounded-xl shadow p-6 space-y-5">
				<div>
					<p class="text-sm text-gray-400 mb-3">El archivo CSV debe tener el siguiente formato:</p>
					<pre class="bg-gray-800 border border-gray-700 rounded-lg p-3 text-xs text-gray-300 overflow-x-auto">ticket_code,quantity,unit_price,usd_quote,date,transaction_key,broker_name
GGAL,100,450.50,1050,2024-03-15,,IOL
MSFT,-10,380.00,1050,2024-03-20,,</pre>
					<p class="text-xs text-gray-600 mt-2">
						Cantidad negativa = venta. <code class="text-gray-400">transaction_key</code> y <code class="text-gray-400">broker_name</code> son opcionales.
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
					<a href="/transactions" class="px-5 py-2 border border-gray-700 text-gray-400 rounded-lg text-sm font-medium hover:bg-gray-800 transition-colors">
						Cancelar
					</a>
				</div>
			</div>
		{/if}

	<!-- === BONO === -->
	{:else}
		{#if bondError}
			<div class="bg-red-950 border border-red-800 text-red-300 rounded-lg px-4 py-3 text-sm">{bondError}</div>
		{/if}
		{#if bondSuccess}
			<div class="bg-green-950 border border-green-800 text-green-300 rounded-lg px-4 py-3 text-sm">{bondSuccess}</div>
		{/if}

		<form on:submit|preventDefault={handleBondSubmit} class="bg-gray-900 border border-gray-800 rounded-xl shadow p-6 space-y-5">
			<div>
				<label class="block text-sm font-medium text-gray-300 mb-1">Código del bono</label>
				<input type="text" bind:value={bondForm.bond_code} required placeholder="Ej: AL30, GD35, AE38" class={inputCls} />
			</div>

			<div>
				<label class="block text-sm font-medium text-gray-300 mb-1">Tipo de operación</label>
				<div class="flex flex-wrap gap-4">
					{#each ['compra', 'venta', 'cupon', 'amortizacion'] as tipo}
						<label class="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
							<input type="radio" bind:group={bondForm.transaction_type} value={tipo} class="accent-indigo-500" />
							{tipo.charAt(0).toUpperCase() + tipo.slice(1)}
						</label>
					{/each}
				</div>
			</div>

			<div>
				<label class="block text-sm font-medium text-gray-300 mb-1">
					Cantidad {#if isCupon}<span class="text-gray-600">(no aplica para cupón)</span>{/if}
				</label>
				<input
					type="number"
					bind:value={bondForm.quantity}
					min="1"
					step="1"
					required={!isCupon}
					disabled={isCupon}
					placeholder="Ej: 10"
					class="{inputCls} {isCupon ? 'opacity-40 cursor-not-allowed' : ''}"
				/>
			</div>

			<div class="grid grid-cols-2 gap-4">
				<div>
					<label class="block text-sm font-medium text-gray-300 mb-1">Precio unitario</label>
					<input type="number" bind:value={bondForm.unit_price} min="0" step="any" required placeholder="Ej: 85.50" class={inputCls} />
				</div>
				<div>
					<label class="block text-sm font-medium text-gray-300 mb-1">Valor Técnico (VT)</label>
					<input type="number" bind:value={bondForm.valor_tecnico} min="0.0001" step="any" required placeholder="Ej: 94.30" class={inputCls} />
				</div>
			</div>

			{#if paridad}
				<div class="bg-indigo-950 border border-indigo-800 rounded-lg px-4 py-2 text-sm text-indigo-300">
					Paridad calculada: <span class="font-semibold">{paridad}</span>
					<span class="text-indigo-500 ml-1">({(Number(paridad) * 100).toFixed(2)}%)</span>
				</div>
			{/if}

			<div class="grid grid-cols-2 gap-4">
				<div>
					<label class="block text-sm font-medium text-gray-300 mb-1">Moneda de interés</label>
					<select bind:value={bondForm.interest_currency} class={inputCls}>
						<option value="USD">USD</option>
						<option value="ARS">ARS</option>
					</select>
				</div>
				<div>
					<label class="block text-sm font-medium text-gray-300 mb-1">Moneda de amortización</label>
					<select bind:value={bondForm.amortization_currency} class={inputCls}>
						<option value="USD">USD</option>
						<option value="ARS">ARS</option>
					</select>
				</div>
			</div>

			<div>
				<label class="block text-sm font-medium text-gray-300 mb-1">Cotización USD</label>
				<input type="number" bind:value={bondForm.usd_quote} min="0" step="1" required placeholder="Ej: 1000" class={inputCls} />
			</div>

			<div>
				<label class="block text-sm font-medium text-gray-300 mb-1">Fecha</label>
				<input type="date" bind:value={bondForm.date} required class={inputCls} />
			</div>

			<div>
				<label class="block text-sm font-medium text-gray-300 mb-1">Broker <span class="text-gray-600">(opcional)</span></label>
				<input type="text" bind:value={bondForm.broker_name} placeholder="Ej: IOL, Balanz..." class={inputCls} />
			</div>

			<div class="flex gap-3 pt-2">
				<button
					type="submit"
					disabled={bondSubmitting}
					class="px-5 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-500 disabled:opacity-50 transition-colors"
				>
					{bondSubmitting ? 'Guardando...' : 'Guardar'}
				</button>
				<a href="/bonds" class="px-5 py-2 border border-gray-700 text-gray-400 rounded-lg text-sm font-medium hover:bg-gray-800 transition-colors">
					Cancelar
				</a>
			</div>
		</form>
	{/if}
</div>
