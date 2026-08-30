"""
catalogo.py
------------------------------------------------------------
Capa de datos del Punto de Venta.

<<<<<<< HEAD
Antes este catálogo estaba escrito directamente aquí (listas en
memoria) solo para poder mostrar y probar la interfaz. Ahora
cada función consulta la base de datos real (a través de
basedatos/repositorio_productos.py): el resto del programa
(vista_productos.py, panel_carrito.py, app.py) sigue
=======
NOTA PARA EL EQUIPO DE DESARROLLO:
Este catálogo está escrito directamente aquí (en memoria) solo
para poder mostrar y probar la interfaz. No se guarda en ningún
archivo ni base de datos. Cuando se conecte el backend real,
las funciones de este archivo (obtener_productos_de,
buscar_producto_por_id, etc.) son las únicas que deberán
cambiar para consultar la base de datos: el resto del programa
(vista_productos.py, panel_carrito.py, app.py) seguirá
>>>>>>> 3af9e03b097cc6b36f9ba114fa6774e55e00e44f
funcionando igual porque solo habla con estas funciones.
------------------------------------------------------------
"""

import datetime

<<<<<<< HEAD
from basedatos import repositorio_productos as _repo

=======
>>>>>>> 3af9e03b097cc6b36f9ba114fa6774e55e00e44f

# ============================================================
# CATEGORÍAS
# ============================================================
<<<<<<< HEAD
# Se leen de la base de datos (tabla "categorias"). Si todavía
# no hay ninguna categoría registrada, se usa esta lista de
# respaldo para que la interfaz no se quede vacía.
# ============================================================

_CATEGORIAS_RESPALDO = ["comida", "bebidas", "postres", "combos"]

CATEGORIAS = _repo.listar_categorias() or _CATEGORIAS_RESPALDO

ICONOS_CATEGORIA = _repo.ICONOS_CATEGORIA
=======

CATEGORIAS = ["comida", "bebidas", "postres", "combos"]

ICONOS_CATEGORIA = {
    "comida": "🍔",
    "bebidas": "🥤",
    "postres": "🍰",
    "combos": "🍟",
}
>>>>>>> 3af9e03b097cc6b36f9ba114fa6774e55e00e44f


# ============================================================
# HORARIOS DEL MENÚ
# ============================================================
# De 7:00 a 10:59 se muestra únicamente el menú de desayunos.
# Del resto del día (11:00 a 6:59, es decir tarde, noche y
# madrugada) se muestra únicamente el menú de almuerzo.
# ============================================================

HORA_INICIO_DESAYUNO = 7
HORA_FIN_DESAYUNO = 11


def obtener_periodo_actual():
    """Devuelve 'desayuno' o 'almuerzo' según la hora del sistema."""

    hora = datetime.datetime.now().hour

    if HORA_INICIO_DESAYUNO <= hora < HORA_FIN_DESAYUNO:
        return "desayuno"

    return "almuerzo"


<<<<<<< HEAD
# ============================================================
# FUNCIONES DE CONSULTA
# ============================================================
# Estas son las funciones que usa el resto del programa; todas
# consultan la base de datos en vivo.
=======
# ------------------------------------------------------------
# PRODUCTOS - MENÚ DE DESAYUNO (7:00 - 10:59)
# ------------------------------------------------------------

PRODUCTOS_DESAYUNO = [
    {"id": 1, "nombre": "Desayuno\nClásico", "descripcion": "Huevos, tocino,\npan tostado", "precio": 45, "categoria": "comida", "emoji": "🍳", "stock": 25},
    {"id": 2, "nombre": "Pancakes", "descripcion": "Con miel y\nmantequilla", "precio": 35, "categoria": "comida", "emoji": "🥞", "stock": 25},
    {"id": 3, "nombre": "Sandwich\nde Huevo", "descripcion": "Pan artesanal", "precio": 30, "categoria": "comida", "emoji": "🥪", "stock": 25},
    {"id": 4, "nombre": "Café\nAmericano", "descripcion": "", "precio": 15, "categoria": "bebidas", "emoji": "☕", "stock": 50},
    {"id": 5, "nombre": "Jugo de\nNaranja", "descripcion": "Natural", "precio": 18, "categoria": "bebidas", "emoji": "🧃", "stock": 40},
    {"id": 6, "nombre": "Chocolate\nCaliente", "descripcion": "", "precio": 20, "categoria": "bebidas", "emoji": "🍫", "stock": 40},
    {"id": 7, "nombre": "Muffin de\nArándanos", "descripcion": "", "precio": 20, "categoria": "postres", "emoji": "🧁", "stock": 30},
    {"id": 8, "nombre": "Fruta\nPicada", "descripcion": "De temporada", "precio": 18, "categoria": "postres", "emoji": "🍓", "stock": 30},
    {"id": 9, "nombre": "Combo\nDesayuno", "descripcion": "Desayuno +\ncafé + jugo", "precio": 70, "categoria": "combos", "emoji": "🍽", "stock": 20},
]


# ------------------------------------------------------------
# PRODUCTOS - MENÚ DE ALMUERZO (11:00 - 6:59)
# ------------------------------------------------------------

PRODUCTOS_ALMUERZO = [
    {"id": 10, "nombre": "Hamburguesa\nClásica", "descripcion": "Lechuga,\ntomate, cebolla", "precio": 85, "categoria": "comida", "emoji": "🍔", "stock": 30},
    {"id": 11, "nombre": "Hamburguesa\nDoble", "descripcion": "Doble carne,\ndoble queso", "precio": 105, "categoria": "comida", "emoji": "🍔", "stock": 30},
    {"id": 12, "nombre": "Papas\nFritas", "descripcion": "", "precio": 25, "categoria": "comida", "emoji": "🍟", "stock": 50},
    {"id": 13, "nombre": "Alitas\nBBQ", "descripcion": "8 unidades", "precio": 55, "categoria": "comida", "emoji": "🍗", "stock": 25},
    {"id": 14, "nombre": "Limonada\nNatural", "descripcion": "", "precio": 25, "categoria": "bebidas", "emoji": "🍋", "stock": 40},
    {"id": 15, "nombre": "Gaseosa", "descripcion": "", "precio": 15, "categoria": "bebidas", "emoji": "🥤", "stock": 60},
    {"id": 16, "nombre": "Malteada", "descripcion": "Vainilla o\nchocolate", "precio": 28, "categoria": "bebidas", "emoji": "🥛", "stock": 35},
    {"id": 17, "nombre": "Helado", "descripcion": "", "precio": 22, "categoria": "postres", "emoji": "🍨", "stock": 30},
    {"id": 18, "nombre": "Brownie", "descripcion": "Con nuez", "precio": 24, "categoria": "postres", "emoji": "🍰", "stock": 30},
    {"id": 19, "nombre": "Combo\nMr.Burger", "descripcion": "Burger + papas\n+ bebida", "precio": 120, "categoria": "combos", "emoji": "🍔", "stock": 20},
    {"id": 20, "nombre": "Combo\nDoble", "descripcion": "2 burgers +\n2 papas + 2 bebidas", "precio": 210, "categoria": "combos", "emoji": "🍽", "stock": 15},
]


# ============================================================
# FUNCIONES DE CONSULTA
# ============================================================
# Estas son las funciones que usa el resto del programa. Cuando
# haya base de datos, cambia SOLO lo de adentro de estas
# funciones (por ejemplo, un SELECT a la tabla "productos").
>>>>>>> 3af9e03b097cc6b36f9ba114fa6774e55e00e44f
# ============================================================

def obtener_todos_los_productos():
    """Todos los productos, sin importar el periodo (desayuno o
    almuerzo). Útil para buscar un producto por id sin importar
    en qué momento del día se vendió."""

<<<<<<< HEAD
    return _repo.listar_productos()


def obtener_productos_del_periodo(periodo):
    """Devuelve los productos habilitados y dentro de su horario
    que corresponden al periodo indicado ('desayuno' o
    'almuerzo')."""

    return _repo.listar_disponibles(periodo)
=======
    return PRODUCTOS_DESAYUNO + PRODUCTOS_ALMUERZO


def obtener_productos_del_periodo(periodo):
    """Devuelve la lista de productos que corresponde al periodo
    indicado ('desayuno' o 'almuerzo')."""

    if periodo == "desayuno":
        return PRODUCTOS_DESAYUNO

    return PRODUCTOS_ALMUERZO
>>>>>>> 3af9e03b097cc6b36f9ba114fa6774e55e00e44f


def buscar_producto_por_id(id_producto):

<<<<<<< HEAD
    return _repo.buscar_producto_por_id(id_producto)


def descontar_stock(id_producto, cantidad):
    """El descuento real del inventario ocurre de forma
    transaccional dentro de la base de datos (procedimiento
    sp_confirmar_pedido) al confirmarse el pago de la venta. Esta
    función se conserva solo por compatibilidad con el resto del
    programa y no necesita hacer nada adicional aquí."""

    pass
=======
    for producto in obtener_todos_los_productos():
        if producto.get("id") == id_producto:
            return producto

    return None


def descontar_stock(id_producto, cantidad):
    """Descuenta stock del producto indicado (solo en memoria por
    ahora; con base de datos esto sería un UPDATE)."""

    producto = buscar_producto_por_id(id_producto)

    if producto is not None and producto.get("stock") is not None:
        producto["stock"] = max(0, producto["stock"] - cantidad)
>>>>>>> 3af9e03b097cc6b36f9ba114fa6774e55e00e44f
