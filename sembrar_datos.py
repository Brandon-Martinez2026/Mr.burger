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

    for nombre in ["hamburguesas", "extras", "bebidas", "desayunos", "combos"]:
        ok, error = productos.agregar_categoria(nombre)

        if ok:
            print(f"Categoría creada: {nombre}")
        elif error != "Esa categoría ya existe.":
            print(f"No se pudo crear la categoría '{nombre}': {error}")


# ============================================================
# PRODUCTOS DEL MENÚ (según Menu_MrBurger-tripleT67.docx)
# ============================================================
# emoji, nombre, descripcion, precio, stock, categoria, periodo
#
# La foto de cada producto NO se define aquí: se busca sola en
# Recursos/productos/ comparando el nombre del producto contra los
# nombres de los archivos de esa carpeta (ver imagenes_productos.py).
# Si no hay ninguna imagen parecida, el producto se muestra con su
# emoji, sin ningún problema.
# ============================================================

PRODUCTOS_EJEMPLO = [

    # --- Hamburguesas -----------------------------------------------
    ("🍔", "Hamburguesa Clásica", "Carne, queso, lechuga, tomate, cebolla",
     35.00, 40, "hamburguesas", "almuerzo"),
    ("🍔", "Hamburguesa Doble Carne", "Doble carne, doble queso, vegetales",
     48.00, 30, "hamburguesas", "almuerzo"),
    ("🍔", "Queso Burguesa", "Carne, doble queso, salsa especial",
     40.00, 30, "hamburguesas", "almuerzo"),
    ("🍔", "Hamburguesa BBQ", "Carne, queso, tocino, aro de cebolla, salsa BBQ",
     45.00, 30, "hamburguesas", "almuerzo"),
    ("🍔", "Hamburguesa Hawaiana", "Carne, queso, piña asada, tocino",
     42.00, 25, "hamburguesas", "almuerzo"),
    ("🥬", "Hamburguesa Vegetariana", "Base de vegetales/legumbres, queso, vegetales",
     38.00, 20, "hamburguesas", "almuerzo"),
    ("🍗", "Chicken Burger", "Pechuga de pollo empanizada, lechuga, mayonesa",
     40.00, 30, "hamburguesas", "almuerzo"),

    # --- Extras y acompañamientos ------------------------------------
    ("🍟", "Papas Fritas (individual)", "Porción mediana",
     15.00, 60, "extras", "almuerzo"),
    ("🍟", "Papas Fritas (grande)", "Porción grande",
     22.00, 50, "extras", "almuerzo"),
    ("🧀", "Papas con queso y tocino", "Papas bañadas en queso cheddar y tocino",
     28.00, 30, "extras", "almuerzo"),
    ("🧅", "Aros de cebolla", "Porción mediana",
     18.00, 30, "extras", "almuerzo"),
    ("🍪", "Galletas", "",
     15.00, 40, "extras", "almuerzo"),
    ("🍗", "Nuggets de pollo (6 pzas)", "Con salsa a elección",
     20.00, 40, "extras", "almuerzo"),

    # --- Bebidas -------------------------------------------------------
    ("🥤", "Gaseosa (12 oz)", "Coca-Cola, Fanta, Sprite, etc.",
     10.00, 80, "bebidas", "almuerzo"),
    ("🥤", "Gaseosa (22 oz)", "Tamaño grande",
     15.00, 60, "bebidas", "almuerzo"),
    ("🍋", "Limonada / Refresco natural", "",
     14.00, 40, "bebidas", "almuerzo"),
    ("🥛", "Malteada", "Vainilla, chocolate o fresa",
     22.00, 30, "bebidas", "almuerzo"),
    ("☕", "Café con leche", "",
     10.00, 40, "bebidas", "almuerzo"),
    ("☕", "Café", "",
     8.00, 40, "bebidas", "almuerzo"),
    ("💧", "Agua pura", "",
     8.00, 60, "bebidas", "almuerzo"),

    # --- Desayunos (06:00-11:00 según el menú) --------------------------
    ("🍳", "Desayuno Mr. Burger", "Huevos, tocino, pan, café",
     35.00, 30, "desayunos", "desayuno"),
    ("🥯", "Bagel con queso crema", "",
     25.00, 25, "desayunos", "desayuno"),
    ("🇬🇹", "Desayuno Chapín",
     "Huevos al gusto, frijoles volteados, plátanos fritos, crema y queso fresco",
     38.00, 25, "desayunos", "desayuno"),
    ("🥞", "Pan queque", "3 pancakes esponjosos acompañados de mantequilla y miel maple",
     30.00, 25, "desayunos", "desayuno"),
    ("🥪", "Sándwich de Huevos y Tocino", "Pan brioche con huevo frito, queso cheddar y tocino crocante",
     28.00, 25, "desayunos", "desayuno"),
    ("🧇", "Waffle Mr. Burger", "Waffle crujiente acompañado de tiras de pollo empanizado y miel maple",
     35.00, 20, "desayunos", "desayuno"),
    ("🍳", "Omelette Supremo", "Omelette de 3 huevos relleno de jamón, queso, pimientos y cebolla",
     36.00, 20, "desayunos", "desayuno"),

    # --- Combos para pareja ---------------------------------------------
    ("💑", "Combo Pareja Clásico", "2 Hamburguesas Clásicas + 1 Papas grande + 2 Gaseosas",
     95.00, 15, "combos", "almuerzo"),
    ("💑", "Combo Pareja BBQ", "2 Hamburguesas BBQ + 1 Aros de cebolla + 2 Gaseosas",
     110.00, 15, "combos", "almuerzo"),
    ("💑", "Combo Pareja Mixto", "1 Hamburguesa Clásica + 1 Chicken Burger + Papas grande + 2 Gaseosas",
     100.00, 15, "combos", "almuerzo"),

    # --- Combos individuales ---------------------------------------------
    ("🍽", "Combo Clásico", "Hamburguesa Clásica + Papas individual + Gaseosa",
     55.00, 25, "combos", "almuerzo"),
    ("🍽", "Combo Queso Burguesa", "Queso Burguesa + Papas individual + Gaseosa",
     58.00, 25, "combos", "almuerzo"),
    ("🍽", "Combo Doble Carne", "Hamburguesa Doble Carne + Papas grande + Gaseosa",
     68.00, 20, "combos", "almuerzo"),
    ("🍽", "Combo Chicken", "Chicken Burger + Papas individual + Gaseosa",
     58.00, 20, "combos", "almuerzo"),
    ("🧒", "Combo Infantil", "Hamburguesa pequeña + Nuggets (3 pzas) + Jugo",
     40.00, 20, "combos", "almuerzo"),

    # --- Combos familiares (4-5 personas) ---------------------------------
    ("👨‍👩‍👧‍👦", "Combo Familiar Clásico", "4 Hamburguesas Clásicas + 2 Papas grandes + 4 Gaseosas",
     175.00, 10, "combos", "almuerzo"),
    ("👨‍👩‍👧‍👦", "Combo Familiar BBQ", "4 Hamburguesas BBQ + 2 Papas grandes + Aros de cebolla + 4 Gaseosas",
     210.00, 10, "combos", "almuerzo"),
    ("🎉", "Combo Fiesta Mr. Burger", "5 Hamburguesas (mixtas a elección) + 2 Papas grandes + 6 Nuggets + 5 Gaseosas",
     260.00, 8, "combos", "almuerzo"),
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
