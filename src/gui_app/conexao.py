import pymysql

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "db_provapython",
    "cursorclass": pymysql.cursors.DictCursor
}

def conectar_bd():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print("Erro ao conectar ao banco:", e)
        return None
