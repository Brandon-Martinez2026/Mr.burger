"""
Cocina.py
------------------------------------------------------------
Punto de entrada de la pantalla de Cocina. Se mantiene en esta
carpeta porque IniciarSesion.py lo abre por su nombre de archivo
(subprocess), igual que MenuPrincipal.py y MenuAdministrador.py.
Todo el código real vive, separado por clases, dentro del
paquete cocina/:

    cocina/panel_pedidos.py -> cuadrícula de tarjetas de pedidos
    cocina/app.py           -> ventana principal (VentanaCocina)
------------------------------------------------------------
"""

import os
import sys

# Permite importar los paquetes locales (estilos, basedatos,
# cocina) sin importar desde dónde se ejecute este archivo.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cocina.app import VentanaCocina


if __name__ == "__main__":

    # IniciarSesion.py abre esta ventana pasando la sesión real
    # del cocinero autenticado: id_usuario y nombre_completo, en
    # ese orden, como argumentos de línea de comandos. Si se
    # ejecuta este archivo directamente (sin pasar por el login)
    # se usan valores de respaldo.
    id_usuario = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else None
    nombre_cocinero = sys.argv[2] if len(sys.argv) > 2 else None

    app = VentanaCocina(id_usuario=id_usuario, nombre_cocinero=nombre_cocinero)
    app.mainloop()
