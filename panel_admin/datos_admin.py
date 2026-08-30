"""
datos_admin.py
------------------------------------------------------------
Capa de datos del Panel de Administrador (inventario y
categorías).

Antes estos datos vivían únicamente en memoria mientras se
usaba el programa; ahora RepositorioProductos es solo un alias
de basedatos.repositorio_productos.RepositorioProductos, que
consulta y actualiza MySQL de verdad (tablas productos,
categorias, inventario y producto_insumo). Las vistas
(vista_inventario.py, vista_categorias.py, etc.) no necesitaron
cambiar porque siguen hablando con los mismos métodos.
------------------------------------------------------------
"""

from basedatos.repositorio_productos import (  # noqa: F401
    RepositorioProductos,
    PERIODOS,
    METODOS_PAGO,
    ICONOS_CATEGORIA,
    ICONO_CATEGORIA_DEFECTO,
)
