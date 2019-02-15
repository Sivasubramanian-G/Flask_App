import pymysql as ms

def connection():
	conn = ms.connect(host = "localhost",
					  user = "siva",
					  passwd = "2842",
					  db = "pythonprogramming")

	c = conn.cursor()
	return c, conn