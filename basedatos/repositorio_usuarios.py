"""
------------------------------------------------------------
Acá fue donde más se modificó por el cambio del correo electrónico
------------------------------------------------------------
"""

import mysql.connector

from .conexion import obtener_conexion, ErrorBaseDatos
from .seguridad import generar_hash, verificar_password


def autenticar(usuario, password):

    usuario = (usuario or "").strip()

    if not usuario or not password:
        return None

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute(
            """SELECT u.id_usuario, u.nombre_completo, u.usuario,
                      u.contrasena_hash, r.nombre_rol
                 FROM usuarios u
                 JOIN roles r ON r.id_rol = u.id_rol
                WHERE u.usuario = %s""",
            (usuario,)
        )

        fila = cursor.fetchone()

        if fila is None:
            return None

        if fila["nombre_rol"] == "inhabilitado":
            return None

        if not verificar_password(password, fila["contrasena_hash"]):
            return None

        return {
            "id_usuario": fila["id_usuario"],
            "nombre_completo": fila["nombre_completo"],
            "usuario": fila["usuario"],
            "rol": fila["nombre_rol"],
        }

    finally:
        cursor.close()
        conexion.close()


def listar_usuarios():

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute(
            """SELECT u.id_usuario, u.nombre_completo, u.usuario,
                      r.nombre_rol AS rol, u.fecha_registro
                 FROM usuarios u
                 JOIN roles r ON r.id_rol = u.id_rol
                ORDER BY u.nombre_completo"""
        )
        return cursor.fetchall()

    finally:
        cursor.close()
        conexion.close()


def crear_usuario(nombre_completo, usuario, password, rol="usuario"):

    nombre_completo = (nombre_completo or "").strip()
    usuario = (usuario or "").strip()

    if not nombre_completo or not usuario or not password:
        return False, "Completa nombre, usuario y contraseña."

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("SELECT id_rol FROM roles WHERE nombre_rol = %s", (rol,))
        fila_rol = cursor.fetchone()

        if fila_rol is None:
            return False, f"El rol \"{rol}\" no existe."

        cursor.execute(
            """INSERT INTO usuarios (nombre_completo, usuario, contrasena_hash, id_rol)
               VALUES (%s, %s, %s, %s)""",
            (nombre_completo, usuario, generar_hash(password), fila_rol[0])
        )

        conexion.commit()
        return True, None

    except mysql.connector.Error as error:
        conexion.rollback()

        if error.errno == 1062:
            return False, "Ese nombre de usuario ya existe."

        return False, f"No se pudo crear el usuario: {error}"

    finally:
        cursor.close()
        conexion.close()


def cambiar_rol(id_usuario, nuevo_rol):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.callproc("sp_actualizar_rol_usuario", (id_usuario, nuevo_rol))
        conexion.commit()
        return True, None

    except mysql.connector.Error as error:
        conexion.rollback()
        return False, f"No se pudo actualizar el rol: {error}"

    finally:
        cursor.close()
        conexion.close()


def cambiar_password(id_usuario, password_nueva):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute(
            "UPDATE usuarios SET contrasena_hash = %s WHERE id_usuario = %s",
            (generar_hash(password_nueva), id_usuario)
        )
        conexion.commit()
        return True, None

    except mysql.connector.Error as error:
        conexion.rollback()
        return False, f"No se pudo actualizar la contraseña: {error}"

    finally:
        cursor.close()
        conexion.close()
