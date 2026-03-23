<script>
	import '../app.css';
	import { page } from '$app/stores';

	const links = [
		{ href: '/dashboard', label: 'Dashboard' },
		{ href: '/stocks', label: 'Holdings' },
		{ href: '/transactions', label: 'Transacciones' },
		{ href: '/transactions/new', label: 'Nueva Transacción' }
	];
</script>

<div class="min-h-screen bg-gray-50 flex flex-col">
	<nav class="bg-indigo-700 text-white shadow">
		<div class="max-w-7xl mx-auto px-4 py-3 flex items-center gap-8">
			<span class="font-bold text-lg tracking-tight">Portfolio</span>
			<div class="flex gap-4">
				{#each links as link}
					<a
						href={link.href}
						class="px-3 py-1.5 rounded-md text-sm font-medium transition-colors
							{$page.url.pathname === link.href
								? 'bg-white/20 text-white'
								: 'text-indigo-100 hover:bg-white/10'}"
					>
						{link.label}
					</a>
				{/each}
			</div>
		</div>
	</nav>
	<main class="flex-1 max-w-7xl w-full mx-auto px-4 py-8">
		<slot />
	</main>
</div>
