import json
import os

# ============================================================
# datos_ventas.py
# ------------------------------------------------------------
# Módulo compartido entre MenuPrincipal.py (que registra cada
# venta al cobrar un pedido) y MenuAdministrador.py (que
# consulta las ventas por cajero, el historial completo de
# ventas, los pedidos y los reportes).
#
# Cada venta se guarda como un diccionario con esta forma:
#
# {
#     "id": 1,
#     "fecha": "2026-08-21 13:45:02",
#     "cajero": "Carlos",
#     "tipo_pedido": "mesa" | "llevar",
#     "mesa": 4,               (None si es "para llevar")
#     "metodo_pago": "efectivo" | "tarjeta" | "mixto",
#     "detalle_pago": { ... datos específicos del método ... },
#     "items": [
#         {"nombre": "Hamburguesa Clásica", "precio": 85, "cantidad": 2}
#     ],
#     "total": 170.0
# }
# ============================================================

CARPETA_BASE = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_VENTAS = os.path.join(CARPETA_BASE, "ventas.json")


def cargar_ventas():
    """Devuelve la lista completa de ventas registradas."""

    if not os.path.isfile(ARCHIVO_VENTAS):
        return []

    try:

        with open(ARCHIVO_VENTAS, "r", encoding="utf-8") as archivo:
            return json.load(archivo)

    except Exception as error:

        print("No se pudo leer ventas.json:", error)
        return []


def _guardar_todas(ventas):

    try:

        with open(ARCHIVO_VENTAS, "w", encoding="utf-8") as archivo:
            json.dump(ventas, archivo, ensure_ascii=False, indent=2)

        return True

    except Exception as error:

        print("No se pudo guardar ventas.json:", error)
        return False


def guardar_venta(venta):
    """Agrega una nueva venta al historial y la guarda en disco.
    Le asigna automáticamente un id consecutivo."""

    ventas = cargar_ventas()

    id_nuevo = (ventas[-1]["id"] + 1) if ventas else 1
    venta["id"] = id_nuevo

    ventas.append(venta)

    _guardar_todas(ventas)

    return venta


def ventas_por_cajero(cajero=None):
    """Devuelve las ventas de un cajero en particular, o un
    diccionario {cajero: [ventas]} si no se especifica ninguno."""

    ventas = cargar_ventas()

    if cajero is not None:
        return [v for v in ventas if v.get("cajero") == cajero]

    agrupadas = {}

    for venta in ventas:
        nombre = venta.get("cajero", "Desconocido")
        agrupadas.setdefault(nombre, []).append(venta)

    return agrupadas


def total_de(ventas):

    return sum(v.get("total", 0) for v in ventas)
