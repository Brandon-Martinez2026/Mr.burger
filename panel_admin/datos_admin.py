"""
datos_admin.py
------------------------------------------------------------
Constantes compartidas por varias vistas del Panel de
Administrador. El repositorio real de productos/categorías
(conectado a MySQL) vive en basedatos/repositorio_productos.py
y lo usa panel_admin/app.py.
------------------------------------------------------------
"""

PERIODOS = ["desayuno", "almuerzo"]
METODOS_PAGO = {"efectivo": "Efectivo", "tarjeta": "Tarjeta", "mixto": "Mixto"}
