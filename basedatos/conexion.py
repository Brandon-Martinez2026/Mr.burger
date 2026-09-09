"""
conexión principal de Mr. BUrger
------------------------------------------------------------
"""

try:
    import mysql.connector
    from mysql.connector import Error as ErrorMySQL
except ImportError as error:
    raise ImportError(
        "Falta instalar el conector de MySQL para Python.\n"
        "Ejecuta:  pip install mysql-connector-python"
    ) from error

from . import config


class ErrorBaseDatos(Exception):
    pass


def obtener_conexion():


    try:
        return mysql.connector.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            autocommit=False,
        )

    except ErrorMySQL as error:
        raise ErrorBaseDatos(
            "No se pudo conectar con la base de datos de Mr.Burger.\n\n"
            f"Detalle: {error}\n\n"
            "Verifica que el servidor MySQL esté encendido, que la base "
            f"\"{config.DB_NAME}\" exista (ejecuta el script SQL del "
            "proyecto) y que las credenciales en basedatos/config.py "
            "(o las variables de entorno MRBURGER_DB_*) sean correctas."
        ) from error
