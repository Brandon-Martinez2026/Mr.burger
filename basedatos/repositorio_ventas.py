"""
se enseña todo en un json
"""

import mysql.connector

from .conexion import obtener_conexion, ErrorBaseDatos


class ErrorVenta(ErrorBaseDatos):

    pass


# ================================================================
# REGISTRAR UNA VENTA (checkout real)
# ================================================================

def guardar_venta(venta):
    """venta: {
        "id_usuario": int (opcional si se manda "cajero"),
        "cajero": nombre (usado solo como respaldo),
        "tipo_pedido": "mesa" | "llevar",
        "mesa": int o None,
        "notas": str opcional,
        "metodo_pago": "efectivo" | "tarjeta" | "mixto",
        "detalle_pago": {...},
        "items": [{"id": id_producto, "nombre", "precio", "cantidad"}],
        "total": float
    }
    Crea el pedido, agrega cada producto, registra el/los pagos y
    confirma el pedido (todo dentro de una misma transacción).
    Devuelve la venta con su "id" (id_pedido) ya asignado."""

    items = venta.get("items", [])

    if not items:
        raise ErrorVenta("El pedido no tiene productos.")

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        id_usuario = venta.get("id_usuario")

        if id_usuario is None:
            id_usuario = _resolver_id_usuario(cursor, venta.get("cajero"))

        cursor.execute(
            """INSERT INTO pedidos (id_usuario, tipo_pedido, numero_mesa, notas)
               VALUES (%s, %s, %s, %s)""",
            (
                id_usuario,
                venta.get("tipo_pedido", "mesa"),
                venta.get("mesa"),
                venta.get("notas"),
            )
        )

        id_pedido = cursor.lastrowid

        for item in items:

            id_producto = item.get("id")

            if id_producto is None:
                raise ErrorVenta(
                    f"El producto \"{item.get('nombre', '?')}\" no tiene un id "
                    "válido; no se puede registrar en la base de datos."
                )

            cursor.callproc(
                "sp_agregar_producto_pedido",
                (id_pedido, id_producto, item.get("cantidad", 1))
            )

        metodo = venta.get("metodo_pago")
        detalle = venta.get("detalle_pago", {}) or {}

        if metodo == "efectivo":
            cursor.callproc(
                "sp_registrar_pago",
                (id_pedido, "efectivo", detalle.get("recibido", venta.get("total", 0)))
            )

        elif metodo == "tarjeta":
            cursor.callproc(
                "sp_registrar_pago",
                (id_pedido, "tarjeta", detalle.get("monto", venta.get("total", 0)))
            )

        elif metodo == "mixto":
            if detalle.get("efectivo", 0) > 0:
                cursor.callproc(
                    "sp_registrar_pago", (id_pedido, "efectivo", detalle["efectivo"])
                )
            if detalle.get("tarjeta", 0) > 0:
                cursor.callproc(
                    "sp_registrar_pago", (id_pedido, "tarjeta", detalle["tarjeta"])
                )

        else:
            raise ErrorVenta(f"Método de pago no reconocido: {metodo}")

        cursor.callproc("sp_confirmar_pedido", (id_pedido,))

        conexion.commit()

    except mysql.connector.Error as error:
        conexion.rollback()
        raise ErrorVenta(error.msg if hasattr(error, "msg") else str(error)) from error

    except ErrorVenta:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()

    resultado = dict(venta)
    resultado["id"] = id_pedido
    return resultado


def _resolver_id_usuario(cursor, nombre_cajero):
    """respaldo, se agarra el 1er usuario registradp"""

    if nombre_cajero:
        cursor.execute(
            "SELECT id_usuario FROM usuarios WHERE nombre_completo = %s LIMIT 1",
            (nombre_cajero,)
        )
        fila = cursor.fetchone()
        if fila:
            return fila[0]

    cursor.execute("SELECT id_usuario FROM usuarios ORDER BY id_usuario LIMIT 1")
    fila = cursor.fetchone()

    if fila is None:
        raise ErrorVenta(
            "No hay ningún usuario registrado en la base de datos. "
            "Crea al menos un usuario (por ejemplo, ejecutando sembrar_datos.py)."
        )

    return fila[0]

# CONSULTAS

def _reconstruir_detalle_pago(metodo, total, cambio, pagos):

    if metodo == "efectivo":
        recibido = sum(float(p["monto"]) for p in pagos) or float(total)
        return {"recibido": recibido, "cambio": float(cambio) if cambio is not None else 0.0}

    if metodo == "tarjeta":
        return {"monto": float(total)}

    if metodo == "mixto":
        efectivo = sum(float(p["monto"]) for p in pagos if p["metodo_pago"] == "efectivo")
        tarjeta = sum(float(p["monto"]) for p in pagos if p["metodo_pago"] == "tarjeta")
        return {"efectivo": efectivo, "tarjeta": tarjeta}

    return {}


def cargar_ventas():

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute(
            """SELECT p.id_pedido, p.fecha_hora, u.nombre_completo AS cajero,
                      p.tipo_pedido, p.numero_mesa, p.metodo_pago, p.total, p.cambio
                 FROM pedidos p
                 JOIN usuarios u ON u.id_usuario = p.id_usuario
                WHERE p.estado IN ('enviado_cocina', 'entregado')
                ORDER BY p.fecha_hora DESC"""
        )
        filas = cursor.fetchall()

        ventas = []

        for fila in filas:

            id_pedido = fila["id_pedido"]

            cursor.execute(
                "SELECT metodo_pago, monto FROM pedido_pagos WHERE id_pedido = %s",
                (id_pedido,)
            )
            pagos = cursor.fetchall()

            cursor.execute(
                """SELECT dp.id_producto, pr.nombre_producto AS nombre,
                          dp.precio_unitario AS precio, dp.cantidad
                     FROM detalle_pedido dp
                     JOIN productos pr ON pr.id_producto = dp.id_producto
                    WHERE dp.id_pedido = %s""",
                (id_pedido,)
            )
            items = cursor.fetchall()

            ventas.append({
                "id": id_pedido,
                "fecha": fila["fecha_hora"].strftime("%Y-%m-%d %H:%M:%S"),
                "cajero": fila["cajero"],
                "tipo_pedido": fila["tipo_pedido"],
                "mesa": fila["numero_mesa"],
                "metodo_pago": fila["metodo_pago"],
                "detalle_pago": _reconstruir_detalle_pago(
                    fila["metodo_pago"], fila["total"], fila["cambio"], pagos
                ),
                "items": [
                    {
                        "id": it["id_producto"],
                        "nombre": it["nombre"],
                        "precio": float(it["precio"]),
                        "cantidad": it["cantidad"],
                    }
                    for it in items
                ],
                "total": float(fila["total"]),
            })

        return ventas

    finally:
        cursor.close()
        conexion.close()


def ventas_por_cajero(cajero=None):

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
