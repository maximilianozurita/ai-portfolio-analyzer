import requests
from datetime import datetime
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from src.models.conector import ConectorBase

AUTH_URL = 'https://api.invertironline.com/token'
PORTFOLIO_URL = 'https://api.invertironline.com/api/v2/estadocuenta'
TOKEN_FILE = 'token_data.json'
load_dotenv()
cipher = Fernet(os.getenv('KEY'))

def _get_new_token():
	print('Obteniendo nuevo token')
	headers = {'Content-Type': 'application/x-www-form-urlencoded'}
	response = requests.post(AUTH_URL, data={
		'username': cipher.decrypt(os.getenv('API_USER')).decode(),
		'password': cipher.decrypt(os.getenv('API_PASSWORD')).decode(),
		'grant_type': 'password'
	}, headers=headers)

	if response.status_code != 200:
		raise Exception(f"Error en la autenticación: {response.status_code} - {response.text}")

	data = response.json()
	_save_token(data)
	return data.get('access_token')


def _get_access_token(refresh_token):
	print('Obteniendo access token a traves de refresh token')
	headers = {
		'Host': 'api.invertironline.com',
		'Content-Type': 'application/x-www-form-urlencoded'
	}
	data_auth = {
		'refresh_token': refresh_token,
		'grant_type': 'refresh_token'
	}
	response = requests.post(AUTH_URL, data=data_auth, headers=headers)
	if response.status_code != 200:
		raise Exception(f"Error en la autenticación: {response.status_code}")
	data = response.json()

	refresh_token = data.get('refresh_token')
	print('refresh token:', refresh_token)

	access_token = data.get('access_token')
	print('access token:', access_token)
	if not access_token:
		raise Exception("No se pudo obtener el access_token")
	print('token obtenido')

	expire_in = data.get('expires_in')
	print('expire in:', expire_in)

	_save_token(data)
	return access_token


def _save_token(data):
	print('Guardando token')
	access_token = cipher.encrypt(data.get('access_token').encode())
	refresh_token = cipher.encrypt(data.get('refresh_token').encode())
	token_expires = datetime.strptime(data.get('.expires'), "%a, %d %b %Y %H:%M:%S GMT").timestamp()
	refresh_expires = datetime.strptime(data.get('.refreshexpires'), "%a, %d %b %Y %H:%M:%S GMT").timestamp()

	query = "INSERT INTO tokens (id, access_token, refresh_token, token_expires, refresh_expires) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE id=VALUES(id), access_token=VALUES(access_token), refresh_token=VALUES(refresh_token), token_expires=VALUES(token_expires), refresh_expires=VALUES(refresh_expires)"
	values = [1, access_token, refresh_token, int(token_expires), int(refresh_expires)]
	conector = ConectorBase()
	conector.execute_query(query, values)


def _get_token():
	print('obteniendo token')
	conector = ConectorBase()
	query = 'SELECT * FROM tokens WHERE id = 1'
	data = conector.select_one(query)
	if data:
		access_token = cipher.decrypt(data.get('access_token')).decode()
		refresh_token = cipher.decrypt(data.get('refresh_token')).decode()
		token_expires = data.get('token_expires')
		refresh_expires = data.get('refresh_expires')

		# Si 'expires' es mayor a fecha actual devolver access token
		if datetime.now().timestamp() < token_expires:
			print('Token no expiro, usando token guardado')
			return access_token

		# Si refreshexpires es mayor a fecha actual obtener access token y refresh token
		if datetime.now().timestamp() < refresh_expires:
			print('refresh token no expiro, usando refresh token guardado')
			return _get_access_token(refresh_token)

	# Si no todos los token espiraron volver a refrescar todos los tokens
	print('Todos los tokens expiraron')
	return _get_new_token()


def get_data(url):
	access_token = _get_token()
	headers = {
		'Authorization': f'Bearer {access_token}',
		'Accept': 'application/json'
	}
	portfolio_response = requests.get(url, headers=headers)
	if portfolio_response.status_code != 200:
		raise Exception(f"Error al obtener el portafolio: {portfolio_response.status_code} - {portfolio_response.text}")
	return portfolio_response.json()


if __name__ == '__main__':
	get_data(PORTFOLIO_URL)



# post /api/v2/Asesor/Movimientos
# AsesoresOperarShow/HideList OperationsExpand Operations
# post /api/v2/asesores/operar/VenderEspecieD
# AsesoresTestInversorShow/HideList OperationsExpand Operations
# get /api/v2/asesores/test-inversor
# post /api/v2/asesores/test-inversor
# post /api/v2/asesores/test-inversor/{idClienteAsesorado}
# MiCuentaShow/HideList OperationsExpand Operations
# NotificacionShow/HideList OperationsExpand Operations
# get /api/v2/Notificacion
# OperarShow/HideList OperationsExpand Operations
# get /api/v2/operar/CPD/PuedeOperar
# get /api/v2/operar/CPD/{estado}/{segmento}
# get /api/v2/operar/CPD/Comisiones/{importe}/{plazo}/{tasa}
# post /api/v2/operar/CPD
# post /api/v2/operar/Token
# post /api/v2/operar/Vender
# post /api/v2/operar/Comprar
# post /api/v2/operar/rescate/fci
# post /api/v2/operar/VenderEspecieD
# post /api/v2/operar/ComprarEspecieD
# post /api/v2/operar/suscripcion/fci
# OperatoriaSimplificadaShow/HideList OperationsExpand Operations
# get /api/v2/OperatoriaSimplificada/MontosEstimados/{monto}
# get /api/v2/OperatoriaSimplificada/{idTipoOperatoria}/Parametros
# get /api/v2/OperatoriaSimplificada/Validar/{monto}/{idTipoOperatoria}
# get /api/v2/OperatoriaSimplificada/VentaMepSimple/MontosEstimados/{monto}
# post /api/v2/Cotizaciones/MEP
# post /api/v2/OperatoriaSimplificada/Comprar
# PerfilShow/HideList OperationsExpand Operations
# get /api/v2/datos-perfil
# TitulosShow/HideList OperationsExpand Operations
# get /api/v2/Titulos/FCI
# get /api/v2/Titulos/FCI/{simbolo}
# get /api/v2/Titulos/FCI/TipoFondos
# get /api/v2/Cotizaciones/MEP/{simbolo}
# get /api/v2/Titulos/FCI/Administradoras
# get /api/v2/{mercado}/Titulos/{simbolo}
# get /api/v2/{mercado}/Titulos/{simbolo}/Opciones
# get /api/v2/{pais}/Titulos/Cotizacion/Instrumentos
# get /api/v2/Cotizaciones/{Instrumento}/{Pais}/Todos
# get /api/v2/Cotizaciones/{Instrumento}/{Panel}/{Pais}
# get /api/v2/{mercado}/Titulos/{simbolo}/CotizacionDetalle
# get /api/v2/cotizaciones-orleans/{Instrumento}/{Pais}/Todos
# get /api/v2/{pais}/Titulos/Cotizacion/Paneles/{instrumento}
# get /api/v2/cotizaciones-orleans/{Instrumento}/{Pais}/Operables
# get /api/v2/{Mercado}/Titulos/{Simbolo}/Cotizacion
# get /api/v2/cotizaciones-orleans-panel/{Instrumento}/{Pais}/Todos
# get /api/v2/Titulos/FCI/Administradoras/{administradora}/TipoFondos
# get /api/v2/cotizaciones-orleans-panel/{Instrumento}/{Pais}/Operables
# get /api/v2/{mercado}/Titulos/{simbolo}/CotizacionDetalleMobile/{plazo}
# get /api/v2/Titulos/FCI/Administradoras/{administradora}/TipoFondos/{tipoFondo}
# get /api/v2/{mercado}/Titulos/{simbolo}/Cotizacion/seriehistorica/{fechaDesde}/{fechaHasta}/{ajustada}