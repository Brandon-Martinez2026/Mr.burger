"""
repositorio_compras.py
------------------------------------------------------------
Registro de compras (reabastecimiento de inventario) hechas por
el administrador a proveedores. Cada línea de una compra aumenta
el stock real del producto comprado (ver
sp_agregar_producto_compra en migraciones/003_cocina_y_compras.sql).
------------------------------------------------------------
"""

import mysql.connector

from .conexion import obtener_conexion, ErrorBaseDatos


class ErrorCompra(ErrorBaseDatos):
    pass


def registrar_compra(compra):
    """compra: {
        "id_usuario": int,
        "proveedor": str o None,
        "notas": str o None,
        "items": [{"id_producto": int, "cantidad": int, "costo_unitario": float}, ...]
    }

    Crea la compra, agrega cada línea (lo que también aumenta el
    stock real vía sp_agregar_producto_compra) y devuelve la
    compra ya guardada, con su id y total."""

    items = compra.get("items", [])

    if not items:
        raise ErrorCompra("La compra no tiene productos.")

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute(
            """INSERT INTO compras (id_usuario, proveedor, notas)
               VALUES (%s, %s, %s)""",
            (
                compra.get("id_usuario"),
                compra.get("proveedor") or None,
                compra.get("notas") or None
            )
        )

        id_compra = cursor.lastrowid

        for item in items:

            cursor.callproc(
                "sp_agregar_producto_compra",
                (
                    id_compra,
                    item["id_producto"],
                    item["cantidad"],
                    item["costo_unitario"]
                )
            )

        conexion.commit()

    except mysql.connector.Error as error:
        conexion.rollback()
        raise ErrorCompra(error.msg if hasattr(error, "msg") else str(error)) from error

    finally:
        cursor.close()
        conexion.close()

    return obtener_compra(id_compra)


def listar_compras(limite=100):
    """Últimas compras registradas, más recientes primero."""

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute(
            """SELECT c.id_compra, c.fecha_hora, c.proveedor, c.notas, c.total,
                      u.nombre_completo AS usuario
                 FROM compras c
                 JOIN usuarios u ON u.id_usuario = c.id_usuario
                ORDER BY c.fecha_hora DESC
                LIMIT %s""",
            (limite,)
        )
        filas = cursor.fetchall()

        return [_fila_a_compra(cursor, fila) for fila in filas]

    finally:
        cursor.close()
        conexion.close()


def obtener_compra(id_compra):

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute(
            """SELECT c.id_compra, c.fecha_hora, c.proveedor, c.notas, c.total,
                      u.nombre_completo AS usuario
                 FROM compras c
                 JOIN usuarios u ON u.id_usuario = c.id_usuario
                WHERE c.id_compra = %s""",
            (id_compra,)
        )
        fila = cursor.fetchone()

        return _fila_a_compra(cursor, fila) if fila else None

    finally:
        cursor.close()
        conexion.close()


def _fila_a_compra(cursor, fila):

    cursor.execute(
        """SELECT cd.cantidad, cd.costo_unitario, p.nombre_producto AS nombre
             FROM compra_detalle cd
             JOIN productos p ON p.id_producto = cd.id_producto
            WHERE cd.id_compra = %s
            ORDER BY cd.id_compra_detalle""",
        (fila["id_compra"],)
    )
    items = cursor.fetchall()

    return {
        "id": fila["id_compra"],
        "fecha": fila["fecha_hora"].strftime("%Y-%m-%d %H:%M:%S"),
        "proveedor": fila["proveedor"] or "",
        "notas": fila["notas"] or "",
        "usuario": fila["usuario"],
        "total": float(fila["total"]),
        "items": [
            {
                "nombre": it["nombre"],
                "cantidad": it["cantidad"],
                "costo_unitario": float(it["costo_unitario"])
            }
            for it in items
        ],
    }
