"""
vista_cobro.py
------------------------------------------------------------
Sección "Cobro" del Panel de Administrador: le permite al
administrador tomar y cobrar un pedido exactamente igual que lo
haría un cajero desde punto_venta/app.py, sin tener que cerrar
sesión y volver a entrar como cajero.

En vez de reescribir la cuadrícula de productos y el carrito,
esta vista simplemente reutiliza las mismas piezas del Punto de
Venta:

    punto_venta/catalogo.py         -> datos de productos
    punto_venta/vista_productos.py  -> cuadrícula de productos
    punto_venta/panel_carrito.py    -> carrito y cobro

Ambas piezas esperan un "controlador" con ciertos atributos
(periodo_actual, categoria_actual, cajero_actual, id_usuario,
vista_productos, y el método agregar_producto). En
punto_venta/app.py ese controlador es la ventana del cajero
(MenuPrincipal); aquí, esta misma clase (VistaCobro) hace ese
papel, tomando el nombre y el id_usuario del administrador que
inició sesión (el segundo parámetro, 'controlador', es la
instancia real de MenuAdministrador).
------------------------------------------------------------
"""

import tkinter as tk

from estilos import CREMA, BORDE, BLANCO
from punto_venta import catalogo
from punto_venta.vista_productos import VistaProductos
from punto_venta.panel_carrito import PanelCarrito


class VistaCobro(tk.Frame):

    def __init__(self, parent, controlador):

        super().__init__(parent, bg=CREMA)

        # 'controlador' aquí es la ventana de MenuAdministrador;
        # de ahí sacamos quién inició sesión para que la venta
        # quede registrada con el administrador real, igual que
        # se registraría con el cajero real.
        self.admin = controlador

        # ----------------------------------------------------
        # Atributos que esperan VistaProductos y PanelCarrito
        # (la misma interfaz que usa punto_venta/app.py).
        # ----------------------------------------------------

        self.periodo_actual = catalogo.obtener_periodo_actual()

        # "todos": no se arma un sidebar de categorías aparte
        # (el administrador ya tiene su propio sidebar de
        # navegación); se muestran todos los productos
        # disponibles del periodo actual y se puede acotar con
        # el buscador que ya trae VistaProductos.
        self.categoria_actual = "todos"

        self.cajero_actual = getattr(self.admin, "nombre_admin", None) or "Administrador"
        self.id_usuario = getattr(self.admin, "id_usuario", None)

        self._crear_interfaz()

        # Revisa cada minuto si cambió el periodo del menú (por
        # ejemplo, de desayuno a almuerzo), igual que en el
        # Punto de Venta.
        self.after(60000, self._revisar_cambio_periodo)

    # ========================================================
    # INTERFAZ
    # ========================================================

    def _crear_interfaz(self):

        tk.Label(
            self, text="Cobro", font=("Segoe UI", 20, "bold"),
            fg="#2B2B2B", bg=CREMA
        ).pack(anchor="w", pady=(0, 15))

        cuerpo = tk.Frame(self, bg=CREMA)
        cuerpo.pack(fill="both", expand=True)

        zona_central = tk.Frame(cuerpo, bg=CREMA)
        zona_central.pack(side="left", fill="both", expand=True, padx=(0, 20))

        self.panel_carrito = PanelCarrito(cuerpo, self)
        self.panel_carrito.pack(
            side="right", fill="y"
        )

        self.vista_productos = VistaProductos(zona_central, self)
        self.vista_productos.pack(fill="both", expand=True)

    # ========================================================
    # PERIODO DEL MENÚ (DESAYUNO / ALMUERZO)
    # ========================================================

    def _revisar_cambio_periodo(self):

        nuevo_periodo = catalogo.obtener_periodo_actual()

        if nuevo_periodo != self.periodo_actual:
            self.periodo_actual = nuevo_periodo
            self.vista_productos.refrescar_periodo()

        self.after(60000, self._revisar_cambio_periodo)

    # ========================================================
    # AGREGAR PRODUCTO AL CARRITO
    # ========================================================
    # Punto de unión entre VistaProductos (donde se hace clic en
    # un producto) y PanelCarrito (donde vive el carrito) — igual
    # que en punto_venta/app.py.
    # ========================================================

    def agregar_producto(self, producto):

        self.panel_carrito.agregar_producto(producto)
