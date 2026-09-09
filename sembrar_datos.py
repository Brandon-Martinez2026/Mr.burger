"""
sembrar_datos.py
------------------------------------------------------------
Script de un solo uso para dejar la base de datos lista para
probar el programa: crea/actualiza el usuario administrador,
crea un usuario cajero, y agrega categorías y productos de
ejemplo (solo si todavía no existen).

Ambos usuarios se manejan ÚNICAMENTE con usuario + contraseña
(sin correo electrónico, tal como pide el sistema):

    usuario: admin    contraseña: admin123      (rol administrador)
    usuario: cajero   contraseña: cajero123     (rol usuario/cajero)

*** Cambia estas contraseñas después de la primera vez que
    inicies sesión, especialmente en un entorno real. ***

Uso:
    1. Crea la base de datos con el script SQL original.
    2. Ejecuta la migración:
       mysql -u root -p mr_burguer_db < migraciones/002_extension_app.sql
    3. Ejecuta:  python sembrar_datos.py
------------------------------------------------------------
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mysql.connector

from basedatos.conexion import obtener_conexion, ErrorBaseDatos
from basedatos.seguridad import generar_hash
from basedatos import repositorio_productos as productos


# ============================================================
# USUARIOS (solo credenciales, nada de correo)
# ============================================================

def sembrar_usuarios():

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        # --- admin: si ya existe, solo le aseguramos una
        #     contraseña válida (por si tenía el placeholder del
        #     script SQL original, "CAMBIAR_POR_HASH_REAL") ---
        cursor.execute("SELECT id_usuario FROM usuarios WHERE usuario = 'admin'")
        fila = cursor.fetchone()

        if fila is None:
            cursor.execute(
                """INSERT INTO usuarios (nombre_completo, usuario, contrasena_hash, id_rol)
                   VALUES ('Administrador', 'admin', %s,
                           (SELECT id_rol FROM roles WHERE nombre_rol = 'administrador'))""",
                (generar_hash("admin123"),)
            )
            print("Usuario creado -> usuario: admin | contraseña: admin123 | rol: administrador")
        else:
            cursor.execute(
                "UPDATE usuarios SET contrasena_hash = %s WHERE id_usuario = %s",
                (generar_hash("admin123"), fila[0])
            )
            print("Usuario 'admin' ya existía: se actualizó su contraseña a admin123")

        # --- cajero: se crea solo si no existe ---
        cursor.execute("SELECT id_usuario FROM usuarios WHERE usuario = 'cajero'")

        if cursor.fetchone() is None:
            cursor.execute(
                """INSERT INTO usuarios (nombre_completo, usuario, contrasena_hash, id_rol)
                   VALUES ('Carlos', 'cajero', %s,
                           (SELECT id_rol FROM roles WHERE nombre_rol = 'usuario'))""",
                (generar_hash("cajero123"),)
            )
            print("Usuario creado -> usuario: cajero | contraseña: cajero123 | rol: usuario (cajero)")
        else:
            print("Usuario 'cajero' ya existía: no se modificó.")

        # --- cocina: se crea solo si no existe (requiere haber
        #     corrido migraciones/003_cocina_y_compras.sql, que es
        #     la que agrega el rol 'cocinero') ---
        cursor.execute("SELECT id_usuario FROM usuarios WHERE usuario = 'cocina'")

        if cursor.fetchone() is None:

            cursor.execute("SELECT id_rol FROM roles WHERE nombre_rol = 'cocinero'")
            fila_rol_cocinero = cursor.fetchone()

            if fila_rol_cocinero is None:
                print(
                    "No existe el rol 'cocinero' todavía: ejecuta "
                    "migraciones/003_cocina_y_compras.sql y vuelve a correr "
                    "sembrar_datos.py para crear el usuario de cocina."
                )
            else:
                cursor.execute(
                    """INSERT INTO usuarios (nombre_completo, usuario, contrasena_hash, id_rol)
                       VALUES ('Cocina', 'cocina', %s, %s)""",
                    (generar_hash("cocina123"), fila_rol_cocinero[0])
                )
                print("Usuario creado -> usuario: cocina | contraseña: cocina123 | rol: cocinero")
        else:
            print("Usuario 'cocina' ya existía: no se modificó.")

        conexion.commit()

    except mysql.connector.Error as error:
        conexion.rollback()
        print(f"No se pudieron crear los usuarios: {error}")

    finally:
        cursor.close()
        conexion.close()


# ============================================================
# CATEGORÍAS
# ============================================================

def sembrar_categorias():

    for nombre in ["comida", "bebidas", "postres", "combos"]:
        ok, error = productos.agregar_categoria(nombre)

        if ok:
            print(f"Categoría creada: {nombre}")
        elif error != "Esa categoría ya existe.":
            print(f"No se pudo crear la categoría '{nombre}': {error}")


# ============================================================
# PRODUCTOS DE EJEMPLO
# ============================================================
# emoji, nombre, descripcion, precio, stock, categoria, periodo
# ============================================================

PRODUCTOS_EJEMPLO = [
    ("🍳", "Desayuno Mr.Burger", "Huevos, tocino, pan y café", 35.00, 30, "comida", "desayuno"),
    ("🥞", "Pancakes",           "3 panqueques con miel",       28.00, 25, "comida", "desayuno"),
    ("🥪", "Sandwich de Jamón",  "Jamón, queso y vegetales",     22.00, 20, "comida", "desayuno"),
    ("☕", "Café Americano",     "12 oz",                        12.00, 50, "bebidas", "desayuno"),
    ("🍔", "Hamburguesa Clásica", "Lechuga, tomate, cebolla",    85.00, 40, "comida", "almuerzo"),
    ("🍔", "Hamburguesa Doble",  "Doble carne, doble queso",     105.00, 30, "comida", "almuerzo"),
    ("🍟", "Papas Fritas",       "Porción mediana",              25.00, 60, "comida", "almuerzo"),
    ("🍗", "Alitas BBQ",         "8 unidades",                   55.00, 25, "comida", "almuerzo"),
    ("🥤", "Gaseosa",            "12 oz",                        10.00, 80, "bebidas", "almuerzo"),
    ("🍦", "Helado",             "Vainilla o chocolate",         18.00, 20, "postres", "almuerzo"),
    ("🍟", "Combo Clásico",      "Hamburguesa + papas + gaseosa", 110.00, 20, "combos", "almuerzo"),
]


def sembrar_productos():

    existentes = {p["nombre"] for p in productos.listar_productos()}

    for emoji, nombre, descripcion, precio, stock, categoria, periodo in PRODUCTOS_EJEMPLO:

        if nombre in existentes:
            continue

        try:
            productos.agregar_producto({
                "nombre": nombre,
                "descripcion": descripcion,
                "emoji": emoji,
                "precio": precio,
                "stock": stock,
                "categoria": categoria,
                "periodo": periodo,
            })
            print(f"Producto creado: {nombre}")

        except ErrorBaseDatos as error:
            print(f"No se pudo crear '{nombre}': {error}")


if __name__ == "__main__":

    print("Sembrando datos iniciales de Mr.Burger...\n")

    try:
        sembrar_usuarios()
        print()
        sembrar_categorias()
        print()
        sembrar_productos()
        print("\nListo. Ya puedes ejecutar IniciarSesion.py")

    except ErrorBaseDatos as error:
        print(f"\n{error}")
        sys.exit(1)
