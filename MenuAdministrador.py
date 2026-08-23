"""
MenuAdministrador.py
------------------------------------------------------------
Punto de entrada del Panel de Administrador. Se mantiene con
este mismo nombre y en esta misma carpeta porque IniciarSesion.py
lo abre por su nombre de archivo (subprocess). Todo el código
real vive ahora, separado por clases -una por cada sección del
dashboard-, dentro del paquete panel_admin/:

    panel_admin/datos_admin.py       -> productos y categorías
    panel_admin/vista_inventario.py  -> sección Inventario
    panel_admin/vista_categorias.py  -> sección Categorías
    panel_admin/vista_cajeros.py     -> sección Cajeros
    panel_admin/vista_ventas.py      -> sección Ventas
    panel_admin/vista_pedidos.py     -> sección Pedidos
    panel_admin/vista_reportes.py    -> sección Reportes
    panel_admin/dialogo_producto.py  -> formulario agregar/editar producto
    panel_admin/app.py               -> ventana principal (MenuAdministrador)
------------------------------------------------------------
"""

import os
import sys

# Permite importar los paquetes locales (estilos, datos_ventas,
# panel_admin) sin importar desde dónde se ejecute este archivo.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from panel_admin.app import MenuAdministrador


if __name__ == "__main__":

    app = MenuAdministrador()
    app.mainloop()
