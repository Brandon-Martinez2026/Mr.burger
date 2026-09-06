"""
repositorio_cocina.py
------------------------------------------------------------
Consultas para la pantalla de Cocina (Cocina.py / cocina/):

    pedidos_pendientes()          -> pedidos ya pagados y
                                      enviados a cocina, todavía
                                      sin entregar (los más
                                      antiguos primero).
    pedidos_entregados_recientes() -> últimos pedidos ya
                                      entregados, para la
                                      pestaña de historial.
    marcar_entregado(id_pedido)   -> pasa un pedido de
                                      'enviado_cocina' a
                                      'entregado' mediante
                                      sp_marcar_pedido_entregado
                                      (nunca se salta el paso de
                                      cocina).
------------------------------------------------------------
"""

import mysql.connector

from .conexion import obtener_conexion, ErrorBaseDatos


class ErrorCocina(ErrorBaseDatos):
    pass


def _cargar_pedidos_por_estado(estados, orden="ASC", limite=None):

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        marcadores = ", ".join(["%s"] * len(estados))

        consulta = f"""
            SELECT p.id_pedido, p.fecha_hora, p.estado, u.nombre_completo AS cajero,
                   p.tipo_pedido, p.numero_mesa, p.notas, p.total
              FROM pedidos p
              JOIN usuarios u ON u.id_usuario = p.id_usuario
             WHERE p.estado IN ({marcadores})
             ORDER BY p.fecha_hora {orden}
        """

        parametros = list(estados)

        if limite:
            consulta += " LIMIT %s"
            parametros.append(limite)

        cursor.execute(consulta, parametros)
        filas = cursor.fetchall()

        pedidos = []

        for fila in filas:

            id_pedido = fila["id_pedido"]

            cursor.execute(
                """SELECT dp.cantidad, pr.nombre_producto AS nombre
                     FROM detalle_pedido dp
                     JOIN productos pr ON pr.id_producto = dp.id_producto
                    WHERE dp.id_pedido = %s
                    ORDER BY dp.id_detalle""",
                (id_pedido,)
            )
            items = cursor.fetchall()

            pedidos.append({
                "id": id_pedido,
                "fecha": fila["fecha_hora"].strftime("%Y-%m-%d %H:%M:%S"),
                "estado": fila["estado"],
                "cajero": fila["cajero"],
                "tipo_pedido": fila["tipo_pedido"],
                "mesa": fila["numero_mesa"],
                "notas": fila["notas"] or "",
                "total": float(fila["total"]),
                "items": [
                    {"nombre": it["nombre"], "cantidad": it["cantidad"]}
                    for it in items
                ],
            })

        return pedidos

    finally:
        cursor.close()
        conexion.close()


def pedidos_pendientes():
    """Pedidos ya pagados y enviados a cocina, todavía sin
    entregar. Los más antiguos primero (FIFO), para que el
    cocinero atienda en orden de llegada."""

    return _cargar_pedidos_por_estado(["enviado_cocina"], orden="ASC")


def pedidos_entregados_recientes(limite=20):
    """Últimos pedidos ya entregados, para que cocina pueda ver
    lo que acaba de completar."""

    return _cargar_pedidos_por_estado(["entregado"], orden="DESC", limite=limite)


def marcar_entregado(id_pedido):
    """Marca un pedido como entregado. Solo funciona si el pedido
    está en estado 'enviado_cocina' (lo valida
    sp_marcar_pedido_entregado); de lo contrario lanza
    ErrorCocina."""

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.callproc("sp_marcar_pedido_entregado", (id_pedido,))
        conexion.commit()

    except mysql.connector.Error as error:
        conexion.rollback()
        raise ErrorCocina(error.msg if hasattr(error, "msg") else str(error)) from error

    finally:
        cursor.close()
        conexion.close()
