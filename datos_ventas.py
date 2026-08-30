"""
datos_ventas.py
------------------------------------------------------------
Módulo compartido entre MenuPrincipal.py (que registra cada
venta al cobrar un pedido) y MenuAdministrador.py (que consulta
las ventas por cajero, el historial completo de ventas, los
pedidos y los reportes).

Antes esto guardaba todo en un archivo ventas.json; ahora es
solo una capa delgada de compatibilidad que delega en
basedatos/repositorio_ventas.py, el cual sí guarda y lee cada
venta directamente de MySQL (tablas pedidos, detalle_pedido y
pedido_pagos). Se conservan las mismas funciones y la misma
forma de diccionario por venta para que ninguna vista del
programa tuviera que cambiar cómo pide los datos:

{
    "id": 1,
    "fecha": "2026-08-21 13:45:02",
    "cajero": "Carlos",
    "tipo_pedido": "mesa" | "llevar",
    "mesa": 4,               (None si es "para llevar")
    "metodo_pago": "efectivo" | "tarjeta" | "mixto",
    "detalle_pago": { ... datos específicos del método ... },
    "items": [
        {"id": 10, "nombre": "Hamburguesa Clásica", "precio": 85, "cantidad": 2}
    ],
    "total": 170.0
}
------------------------------------------------------------
"""

from basedatos import repositorio_ventas as _repo
from basedatos.conexion import ErrorBaseDatos  # noqa: F401  (re-exportado para quien lo necesite)
from basedatos.repositorio_ventas import ErrorVenta  # noqa: F401


def cargar_ventas():
    """Devuelve la lista completa de ventas ya confirmadas."""
    return _repo.cargar_ventas()


def guardar_venta(venta):
    """Registra una venta completa en la base de datos: crea el
    pedido, agrega cada producto, registra el/los pagos y
    confirma el pedido. Puede lanzar ErrorVenta si, por ejemplo,
    no hay inventario suficiente."""
    return _repo.guardar_venta(venta)


def ventas_por_cajero(cajero=None):
    """Devuelve las ventas de un cajero en particular, o un
    diccionario {cajero: [ventas]} si no se especifica ninguno."""
    return _repo.ventas_por_cajero(cajero)


def total_de(ventas):
    return _repo.total_de(ventas)
