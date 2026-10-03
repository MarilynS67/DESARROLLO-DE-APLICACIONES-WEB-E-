import mysql.connector


def obtener_conexion():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="rubi21",
        database="ferreteria"
    )

    return conexion