import mysql.connector
from mysql.connector import Error

def crear_conexion():
    try:
        return mysql.connector.connect(
            host="168.138.91.190",  # Cambia esto por tu host
            user="USER_PRO_GTA5",   # Tu usuario de MySQL
            password="1234",         # Tu contraseña
            database="PRO_GTA5",    # Nombre de la base de datos
            ssl_disabled=False
        )
    except Error as e:
        print(f"Error de conexión: {e}")
        return None

def ejecutar_consulta(query, parametros=None):
    conn = crear_conexion()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, parametros)
            conn.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Error en consulta: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

def obtener_datos(query, parametros=None):
    conn = crear_conexion()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, parametros)
            return cursor.fetchall()
        except Error as e:
            print(f"Error en consulta: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    return []