from datetime import datetime
from src.models.stock import Stock
from src.models.bond_holding import BondHolding
from src.services.ai_providers.gemini_provider import GeminiProvider
from src.services.ai_providers.openai_provider import OpenAIProvider
from src.services.ai_providers.openrouter_provider import OpenRouterProvider

PROVIDERS = {
	"gemini": {
		"id": "gemini",
		"name": "Google Gemini",
		"instance": GeminiProvider(),
	},
	"openai": {
		"id": "openai",
		"name": "OpenAI GPT",
		"instance": OpenAIProvider(),
	},
	"openrouter": {
		"id": "openrouter",
		"name": "OpenRouter",
		"instance": OpenRouterProvider(),
	},
}

def get_available_providers():
	result = []
	for provider_id, provider in PROVIDERS.items():
		instance = provider["instance"]
		if instance.is_available():
			result.append({
				"id": provider_id,
				"name": provider["name"],
				"models": instance.get_models(),
			})
	return result

def _build_prompt(stocks, bonds, market_stocks=None, market_bonds=None):
	today = datetime.now().strftime("%d/%m/%Y")
	lines = [
		f"Hoy es {today}.",
		"Analizá el siguiente portfolio de inversiones y generá un informe en formato Markdown.",
		"Usá encabezados (#, ##, ###), negritas (**texto**) y listas donde corresponda.",
		"El tono debe ser el de un informe financiero profesional. No incluyas presentaciones, títulos sobre quién eres, ni frases como 'Como IA' o 'Como asesor'.",
		"Comenzá directamente con el contenido del informe.",
		"",
	]

	if stocks:
		lines.append("### DATOS: ACCIONES / CEDEARs")
		for s in stocks:
			ppc = s.get("ppc", 0)
			qty = s.get("quantity", 0)
			ticker = s['ticket_code']
			total_ppc = round(ppc * qty)
			line = f"- {ticker}: {qty} acciones, PPC ${ppc:,.2f}, invertido ${total_ppc:,.0f} ARS"
			if market_stocks and ticker in market_stocks:
				mp = market_stocks[ticker]
				if mp.get("price"):
					current_val = mp.get("current_value", 0)
					pnl_pct = mp.get("pnl_pct")
					pnl_ars = mp.get("pnl_ars", 0)
					sign_pct = "+" if pnl_pct and pnl_pct >= 0 else ""
					sign_ars = "+" if pnl_ars and pnl_ars >= 0 else ""
					line += (f", precio actual ${mp['price']:,.2f}, valor actual ${current_val:,.0f} ARS,"
							 f" P&L {sign_pct}{pnl_pct:.2f}% ({sign_ars}${pnl_ars:,.0f} ARS)")
			lines.append(line)
	else:
		lines.append("### DATOS: ACCIONES\n(sin posiciones abiertas)")

	lines.append("")

	if bonds:
		lines.append("### DATOS: BONOS")
		for b in bonds:
			ppc = b.get("ppc", 0)
			qty = b.get("quantity", 0)
			bond_code = b['bond_code']
			total_ppc = round(ppc * qty)
			paridad = b.get("ppc_paridad", 0)
			line = (f"- {bond_code}: {qty} láminas, PPC ${ppc:,.4f},"
					f" paridad {paridad:.4f}, invertido ${total_ppc:,.0f} ARS")
			if market_bonds and bond_code in market_bonds:
				mb = market_bonds[bond_code]
				if mb.get("price"):
					current_val = mb.get("current_value", 0)
					pnl_pct = mb.get("pnl_pct")
					pnl_ars = mb.get("pnl_ars", 0)
					sign_pct = "+" if pnl_pct and pnl_pct >= 0 else ""
					sign_ars = "+" if pnl_ars and pnl_ars >= 0 else ""
					line += (f", precio actual ${mb['price']:,.4f}, valor actual ${current_val:,.0f} ARS,"
							 f" P&L {sign_pct}{pnl_pct:.2f}% ({sign_ars}${pnl_ars:,.0f} ARS)")
			lines.append(line)
	else:
		lines.append("### DATOS: BONOS\n(sin posiciones abiertas)")

	lines += [
		"",
		"---",
		"Con los datos anteriores, generá un informe en Markdown con las siguientes secciones:",
		"1. **Resumen Ejecutivo** – composición del portfolio, valor total invertido y valor actual si hay datos de mercado",
		"2. **Análisis por Clase de Activo** – acciones y bonos por separado",
		"3. **Diversificación y Concentración** – balance entre activos, sectores y geografía",
		"4. **Rendimiento** – si hay datos de precio actual, analizá el P&L; si no, comentalo brevemente",
		"5. **Riesgos Identificados** – concentración, exposición cambiaria, riesgo soberano, liquidez",
		"6. **Contexto del Mercado Argentino** – factores macroeconómicos relevantes a la fecha",
		"7. **Conclusiones y Consideraciones** – puntos de atención y posibles acciones a evaluar",
		"",
		"Respondé únicamente con el contenido del informe en Markdown. No agregues comentarios previos ni posteriores al informe.",
	]

	return "\n".join(lines)

def analyze_portfolio(provider_id: str, model: str, market_stocks=None, market_bonds=None):
	provider = PROVIDERS.get(provider_id)
	if not provider:
		return {"ok": False, "msg": f"Provider '{provider_id}' no encontrado"}

	instance = provider["instance"]
	if not instance.is_available():
		return {"ok": False, "msg": f"API key para '{provider_id}' no configurada"}

	stocks = [s.get_attr_dict() for s in (Stock.find_all() or [])]
	bonds = [b.get_attr_dict() for b in (BondHolding.find_all() or [])]

	prompt = _build_prompt(stocks, bonds, market_stocks, market_bonds)

	try:
		analysis = instance.analyze(prompt, model)
		return {"ok": True, "data": {"analysis": analysis}}
	except Exception as e:
		return {"ok": False, "msg": str(e)}
