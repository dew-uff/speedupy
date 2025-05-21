import redis

#XXX: IMPLEMENTAR + TESTAR!!!!
class BancoRedis():
	def __init__(self):
		self.client = redis.Redis(host='localhost', port=6379, db=0)

	def flushDatabase(self):
		self.client.flushdb()

	# def executarComandoSQLSemRetorno(self, sql, arguments=()):
	# 	self.cursor.execute(sql, arguments)

	# def executarComandoSQLSelect(self, sql, arguments=()):
	# 	self.cursor.execute(sql, arguments)
	# 	return self.cursor.fetchall()

	# def salvarAlteracoes(self):
	# 	self.conexao.commit()

	def closeConnection(self):
		self.client.close()
