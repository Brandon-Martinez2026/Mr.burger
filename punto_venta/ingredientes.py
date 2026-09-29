"""Consultas de ingredientes para personalizar productos.

La receta base vive en producto_insumo/inventario. Los extras opcionales
se configuran en producto_modificador. No se mantiene una lista fija en Python.
"""
from basedatos.conexion import obtener_conexion


def obtener_ingredientes_editables(producto):
    id_producto = producto.get("id")
    if not id_producto:
        return []

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT inv.id_insumo, inv.nombre_insumo, pi.cantidad_requerida AS cantidad_base,
                   1 AS incluido, 1 AS permite_quitar, 1 AS permite_extra
              FROM producto_insumo pi
              JOIN inventario inv ON inv.id_insumo = pi.id_insumo
             WHERE pi.id_producto = %s
            UNION ALL
            SELECT inv.id_insumo, inv.nombre_insumo, pm.cantidad_por_extra AS cantidad_base,
                   0 AS incluido, pm.permite_quitar, pm.permite_extra
              FROM producto_modificador pm
              JOIN inventario inv ON inv.id_insumo = pm.id_insumo
             WHERE pm.id_producto = %s
               AND NOT EXISTS (
                   SELECT 1 FROM producto_insumo pi2
                    WHERE pi2.id_producto = pm.id_producto
                      AND pi2.id_insumo = pm.id_insumo
               )
             ORDER BY nombre_insumo
        """, (id_producto, id_producto))
        return cursor.fetchall()
    finally:
        cursor.close()
        conexion.close()
