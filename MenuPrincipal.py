"""
MenuPrincipal.py
------------------------------------------------------------
Punto de entrada del Punto de Venta. Se mantiene con este mismo
nombre y en esta misma carpeta porque IniciarSesion.py lo abre
por su nombre de archivo (subprocess). Todo el código real vive
ahora, separado por clases, dentro del paquete punto_venta/:

    punto_venta/catalogo.py        -> productos y categorías
    punto_venta/vista_productos.py -> cuadrícula de productos
    punto_venta/panel_carrito.py   -> carrito y cobro
    punto_venta/ventana_pago.py    -> ventana de método de pago
    punto_venta/app.py             -> ventana principal (MenuPrincipal)
------------------------------------------------------------
"""

import os
import sys

# Permite importar los paquetes locales (estilos, datos_ventas,
# punto_venta) sin importar desde dónde se ejecute este archivo.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from punto_venta.app import MenuPrincipal


if __name__ == "__main__":

    # IniciarSesion.py abre esta ventana pasando la sesión real
    # del cajero autenticado: id_usuario y nombre_completo, en
    # ese orden, como argumentos de línea de comandos. Si se
    # ejecuta este archivo directamente (sin pasar por el login)
    # se usan valores de respaldo.
    id_usuario = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else None
    nombre_cajero = sys.argv[2] if len(sys.argv) > 2 else None

    app = MenuPrincipal(id_usuario=id_usuario, nombre_cajero=nombre_cajero)
    app.mainloop()
