"""
catalogo.py
------------------------------------------------------------
Capa de datos del Punto de Venta.

Antes este catálogo estaba escrito directamente aquí (listas en
memoria) solo para poder mostrar y probar la interfaz. Ahora
cada función consulta la base de datos real (a través de
basedatos/repositorio_productos.py): el resto del programa
(vista_productos.py, panel_carrito.py, app.py) sigue
funcionando igual porque solo habla con estas funciones.
------------------------------------------------------------
"""

import datetime

from basedatos import repositorio_productos as _repo


# ============================================================
# CATEGORÍAS
# ============================================================
# Se leen de la base de datos (tabla "categorias"). Si todavía
# no hay ninguna categoría registrada, se usa esta lista de
# respaldo para que la interfaz no se quede vacía.
# ============================================================

_CATEGORIAS_RESPALDO = [
    "Hamburguesas", "Extras ", "Bebidas", "Desayunos",
    "Combos Pareja", "Combos Individuales", "Combos Familiares",
]

CATEGORIAS = _repo.listar_categorias() or _CATEGORIAS_RESPALDO

ICONOS_CATEGORIA = _repo.ICONOS_CATEGORIA
icono_de_categoria = _repo.icono_de_categoria


# ============================================================
# HORARIOS DEL MENÚ
# ============================================================
# El límite real (06:00 a 10:59 = desayuno; el resto del día =
# almuerzo) se toma de basedatos/repositorio_productos.py, que
# es la misma constante que usa la base de datos para decidir
# qué productos son "Desayunos" (ver mr_burguer_db.sql). Antes
# este archivo tenía su propio "7" fijo por separado, que ya no
# coincidía con el horario real (06:00) de la base de datos.
# ============================================================

HORA_INICIO_DESAYUNO = int(_repo.HORA_INICIO_DESAYUNO.split(":")[0])
HORA_FIN_DESAYUNO = int(_repo.HORA_FIN_DESAYUNO.split(":")[0])


def obtener_periodo_actual():
    """Devuelve 'desayuno' o 'almuerzo' según la hora del sistema."""

    hora = datetime.datetime.now().hour

    if HORA_INICIO_DESAYUNO <= hora < HORA_FIN_DESAYUNO:
        return "desayuno"

    return "almuerzo"


# ============================================================
# FUNCIONES DE CONSULTA
# ============================================================
# Estas son las funciones que usa el resto del programa; todas
# consultan la base de datos en vivo.
# ============================================================

def obtener_todos_los_productos():
    """Todos los productos, sin importar el periodo (desayuno o
    almuerzo). Útil para buscar un producto por id sin importar
    en qué momento del día se vendió."""

    return _repo.listar_productos()


def obtener_productos_del_periodo(periodo):
    """Devuelve los productos habilitados y dentro de su horario
    que corresponden al periodo indicado ('desayuno' o
    'almuerzo')."""

    return _repo.listar_disponibles(periodo)


def buscar_producto_por_id(id_producto):

    return _repo.buscar_producto_por_id(id_producto)


def categorias_disponibles(periodo):
    """Devuelve, en el mismo orden que CATEGORIAS, únicamente las
    categorías que tienen al menos un producto disponible para el
    periodo indicado ('desayuno' o 'almuerzo'). Así el sidebar del
    cajero no muestra pestañas vacías (por ejemplo, no muestra
    "Desayunos" mientras está activo el menú de almuerzo)."""

    disponibles = obtener_productos_del_periodo(periodo)
    categorias_con_productos = {p["categoria"] for p in disponibles}

    return [c for c in CATEGORIAS if c in categorias_con_productos]


def descontar_stock(id_producto, cantidad):
    """El descuento real del inventario ocurre de forma
    transaccional dentro de la base de datos (procedimiento
    sp_confirmar_pedido) al confirmarse el pago de la venta. Esta
    función se conserva solo por compatibilidad con el resto del
    programa y no necesita hacer nada adicional aquí."""

    pass
