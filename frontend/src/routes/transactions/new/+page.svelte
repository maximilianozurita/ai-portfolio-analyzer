<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { getTickets, addTransaction } from '$lib/api.js';

	let tickets = [];
	let error = '';
	let success = '';
	let submitting = false;

	let form = {
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
			if (tickets.length > 0) form.ticket_code = tickets[0].ticket_code;
		} catch (e) {
			error = 'Error al cargar tickers: ' + e.message;
		}
	});

	async function handleSubmit() {
		error = '';
		success = '';
		submitting = true;

		try {
			const qty = Number(form.quantity);
			const dateTs = Math.floor(new Date(form.date).getTime() / 1000);

			const data = {
				ticket_code: form.ticket_code,
				quantity: form.tipo === 'venta' ? -qty : qty,
				unit_price: Number(form.unit_price),
				usd_quote: Number(form.usd_quote),
				date: dateTs
			};

			if (form.broker_name.trim()) data.broker_name = form.broker_name.trim();

			await addTransaction(data);
			success = 'Transacción registrada correctamente.';
			setTimeout(() => goto('/transactions'), 1200);
		} catch (e) {
			error = e.message;
		} finally {
			submitting = false;
		}
	}
</script>

<div class="max-w-lg space-y-6">
	<h1 class="text-2xl font-bold text-gray-800">Nueva Transacción</h1>

	{#if error}
		<div class="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 text-sm">{error}</div>
	{/if}
	{#if success}
		<div class="bg-green-50 border border-green-200 text-green-700 rounded-lg px-4 py-3 text-sm">{success}</div>
	{/if}

	<form on:submit|preventDefault={handleSubmit} class="bg-white rounded-xl shadow p-6 space-y-5">
		<div>
			<label class="block text-sm font-medium text-gray-700 mb-1">Ticker</label>
			<select
				bind:value={form.ticket_code}
				required
				class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
			>
				{#each tickets as t}
					<option value={t.ticket_code}>{t.ticket_code} — {t.name}</option>
				{/each}
			</select>
		</div>

		<div>
			<label class="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
			<div class="flex gap-6">
				<label class="flex items-center gap-2 text-sm cursor-pointer">
					<input type="radio" bind:group={form.tipo} value="compra" class="accent-indigo-600" />
					Compra
				</label>
				<label class="flex items-center gap-2 text-sm cursor-pointer">
					<input type="radio" bind:group={form.tipo} value="venta" class="accent-indigo-600" />
					Venta
				</label>
			</div>
		</div>

		<div>
			<label class="block text-sm font-medium text-gray-700 mb-1">Cantidad</label>
			<input
				type="number"
				bind:value={form.quantity}
				min="1"
				step="1"
				required
				placeholder="Ej: 100"
				class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
			/>
		</div>

		<div>
			<label class="block text-sm font-medium text-gray-700 mb-1">Precio unitario</label>
			<input
				type="number"
				bind:value={form.unit_price}
				min="0"
				step="any"
				required
				placeholder="Ej: 1250.50"
				class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
			/>
		</div>

		<div>
			<label class="block text-sm font-medium text-gray-700 mb-1">Cotización USD</label>
			<input
				type="number"
				bind:value={form.usd_quote}
				min="0"
				step="1"
				required
				placeholder="Ej: 1000"
				class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
			/>
		</div>

		<div>
			<label class="block text-sm font-medium text-gray-700 mb-1">Fecha</label>
			<input
				type="date"
				bind:value={form.date}
				required
				class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
			/>
		</div>

		<div>
			<label class="block text-sm font-medium text-gray-700 mb-1">Broker <span class="text-gray-400">(opcional)</span></label>
			<input
				type="text"
				bind:value={form.broker_name}
				placeholder="Ej: IOL, Balanz..."
				class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
			/>
		</div>

		<div class="flex gap-3 pt-2">
			<button
				type="submit"
				disabled={submitting}
				class="px-5 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors"
			>
				{submitting ? 'Guardando...' : 'Guardar'}
			</button>
			<a
				href="/transactions"
				class="px-5 py-2 border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
			>
				Cancelar
			</a>
		</div>
	</form>
</div>
