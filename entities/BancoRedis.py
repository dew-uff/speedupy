import redis

#XXX: IMPLEMENTAR + TESTAR!!!!
class BancoRedis():
	def __init__(self):
		self.client = redis.Redis(host='localhost', port=6379, db=0)

	def flush_database(self):
		self.client.flushdb()

	def set(self, key, value):
		self.client.set(key, value)

	def get(self, key):
		return self.client.get(key)

	def dbsize(self):
		return self.client.dbsize()

	# def executarComandoSQLSemRetorno(self, sql, arguments=()):
	# 	self.cursor.execute(sql, arguments)

	# def executarComandoSQLSelect(self, sql, arguments=()):
	# 	self.cursor.execute(sql, arguments)
	# 	return self.cursor.fetchall()

	# def salvarAlteracoes(self):
	# 	self.conexao.commit()

	def close_connection(self):
		self.client.close()
