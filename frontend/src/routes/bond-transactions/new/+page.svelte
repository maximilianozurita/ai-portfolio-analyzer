<script>
	import { goto } from '$app/navigation';
	import { addBondTransaction } from '$lib/api.js';

	let error = '';
	let success = '';
	let submitting = false;

	let form = {
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

	$: isCupon = form.transaction_type === 'cupon';
	$: paridad = (form.unit_price && form.valor_tecnico && Number(form.valor_tecnico) > 0)
		? (Number(form.unit_price) / Number(form.valor_tecnico)).toFixed(6)
		: null;

	async function handleSubmit() {
		error = '';
		success = '';
		submitting = true;

		try {
			const dateTs = Math.floor(new Date(form.date).getTime() / 1000);

			const data = {
				bond_code: form.bond_code.trim().toUpperCase(),
				transaction_type: form.transaction_type,
				quantity: isCupon ? 0 : Number(form.quantity),
				unit_price: Number(form.unit_price),
				valor_tecnico: Number(form.valor_tecnico),
				interest_currency: form.interest_currency,
				amortization_currency: form.amortization_currency,
				usd_quote: Number(form.usd_quote),
				date: dateTs
			};

			if (form.broker_name.trim()) data.broker_name = form.broker_name.trim();

			await addBondTransaction(data);
			success = 'Operación registrada correctamente.';
			setTimeout(() => goto('/bonds'), 1200);
		} catch (e) {
			error = e.message;
		} finally {
			submitting = false;
		}
	}

	const inputCls = 'w-full border border-gray-700 bg-gray-800 text-gray-200 placeholder-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500';
</script>

<div class="max-w-lg space-y-6">
	<h1 class="text-2xl font-bold text-gray-100">Nueva Operación de Bono</h1>

	{#if error}
		<div class="bg-red-950 border border-red-800 text-red-300 rounded-lg px-4 py-3 text-sm">{error}</div>
	{/if}
	{#if success}
		<div class="bg-green-950 border border-green-800 text-green-300 rounded-lg px-4 py-3 text-sm">{success}</div>
	{/if}

	<form on:submit|preventDefault={handleSubmit} class="bg-gray-900 border border-gray-800 rounded-xl shadow p-6 space-y-5">

		<div>
			<label class="block text-sm font-medium text-gray-300 mb-1">Código del bono</label>
			<input
				type="text"
				bind:value={form.bond_code}
				required
				placeholder="Ej: AL30, GD35, AE38"
				class={inputCls}
			/>
		</div>

		<div>
			<label class="block text-sm font-medium text-gray-300 mb-1">Tipo de operación</label>
			<div class="flex flex-wrap gap-4">
				{#each ['compra', 'venta', 'cupon', 'amortizacion'] as tipo}
					<label class="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
						<input type="radio" bind:group={form.transaction_type} value={tipo} class="accent-indigo-500" />
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
				bind:value={form.quantity}
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
				<input type="number" bind:value={form.unit_price} min="0" step="any" required placeholder="Ej: 85.50" class={inputCls} />
			</div>
			<div>
				<label class="block text-sm font-medium text-gray-300 mb-1">Valor Técnico (VT)</label>
				<input type="number" bind:value={form.valor_tecnico} min="0.0001" step="any" required placeholder="Ej: 94.30" class={inputCls} />
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
				<select bind:value={form.interest_currency} class={inputCls}>
					<option value="USD">USD</option>
					<option value="ARS">ARS</option>
				</select>
			</div>
			<div>
				<label class="block text-sm font-medium text-gray-300 mb-1">Moneda de amortización</label>
				<select bind:value={form.amortization_currency} class={inputCls}>
					<option value="USD">USD</option>
					<option value="ARS">ARS</option>
				</select>
			</div>
		</div>

		<div>
			<label class="block text-sm font-medium text-gray-300 mb-1">Cotización USD</label>
			<input type="number" bind:value={form.usd_quote} min="0" step="1" required placeholder="Ej: 1000" class={inputCls} />
		</div>

		<div>
			<label class="block text-sm font-medium text-gray-300 mb-1">Fecha</label>
			<input type="date" bind:value={form.date} required class={inputCls} />
		</div>

		<div>
			<label class="block text-sm font-medium text-gray-300 mb-1">Broker <span class="text-gray-600">(opcional)</span></label>
			<input type="text" bind:value={form.broker_name} placeholder="Ej: IOL, Balanz..." class={inputCls} />
		</div>

		<div class="flex gap-3 pt-2">
			<button
				type="submit"
				disabled={submitting}
				class="px-5 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-500 disabled:opacity-50 transition-colors"
			>
				{submitting ? 'Guardando...' : 'Guardar'}
			</button>
			<a
				href="/bonds"
				class="px-5 py-2 border border-gray-700 text-gray-400 rounded-lg text-sm font-medium hover:bg-gray-800 transition-colors"
			>
				Cancelar
			</a>
		</div>
	</form>
</div>
