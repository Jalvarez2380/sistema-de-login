import mysql.connector

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Pantera2380$",  # Cambia esto por tu contraseña
            database="desarrollo_web"
        )
        return conexion
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
