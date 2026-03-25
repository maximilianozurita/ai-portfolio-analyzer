import mysql.connector
from config.config import DB_HOST, DB_USER, DB_PASSWORD

class ConectorBase:
	def __init__(self):
		self.connection = mysql.connector.connect(
			host=DB_HOST,
			user=DB_USER,
			password=DB_PASSWORD,
			database="stats"
		)
		self.cursor = self.connection.cursor()
		self.columnas_name = []

	def execute_query(self, query, values = None):
		self.cursor.execute(query, values)
		self.connection.commit()
		id = self.cursor.lastrowid
		self.close()
		return id

	def query_delete(self, query, values = None):
		self.cursor.execute(query, values)
		self.connection.commit()
		row_count = self.cursor.rowcount
		self.close()
		return row_count

	def select(self, query, values = None, select_one = False):
		if select_one:
			#Para evitar problemas al traer mas de un resultado con fetchone
			if "limit 1" not in query.lower():
				query += " limit 1"

			self.cursor.execute(query, values)
			results = self.cursor.fetchone()
			datos_dict = None
		else:
			self.cursor.execute(query, values)
			results = self.cursor.fetchall()
			datos_dict = []

		if results:
			# Cargar los nombres de las columnas
			self.load_column_attr()
			# Mapear los resultados a un diccionario
			if select_one:
				datos_dict = dict(zip(self.columnas_name, results))
			else:
				datos_dict = [dict(zip(self.columnas_name, fila)) for fila in results]
			self.close()
		return datos_dict

	def load_column_attr(self):
		description_tabla = self.cursor.description
		for columna_desc in description_tabla:
			col_name = columna_desc[0]
			self.columnas_name.append(col_name)

	def select_one(self, query, values = None):
		return self.select(query, values, True)

	def close(self):
		self.cursor.close()
		self.connection.close()
