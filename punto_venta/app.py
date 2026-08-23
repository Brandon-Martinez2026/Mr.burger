"""
app.py (punto_venta)
------------------------------------------------------------
Ventana principal del Punto de Venta (antes todo esto vivía en
un único archivo MenuPrincipal.py). Esta clase solo se encarga
de la ventana, el sidebar y de unir las piezas:

    - punto_venta/catalogo.py        -> datos de productos
    - punto_venta/vista_productos.py -> cuadrícula de productos
    - punto_venta/panel_carrito.py   -> carrito y cobro
    - punto_venta/ventana_pago.py    -> ventana de método de pago
------------------------------------------------------------
"""

import os
import sys

import tkinter as tk
from tkinter import messagebox

try:
    from PIL import Image, ImageTk
except ImportError:
    print("Necesitas instalar Pillow: pip install pillow")
    sys.exit(1)

from estilos import (
    ROJO, ROJO_CLARO, ROJO_OSCURO, CREMA, BLANCO,
    FILTRO_REESCALADO, resolver_carpeta_recursos, buscar_logo
)
from punto_venta import catalogo
from punto_venta.vista_productos import VistaProductos
from punto_venta.panel_carrito import PanelCarrito


# ============================================================
# CAJERO ACTUAL
# ============================================================
# Nombre del cajero que tiene la sesión abierta en este punto
# de venta. Se usa para guardar a qué cajero pertenece cada
# venta, de modo que el administrador pueda consultarlas por
# separado en el apartado "Cajeros".
# ============================================================

CAJERO_ACTUAL = "Carlos"

CARPETA_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARPETA_LOGO = resolver_carpeta_recursos(CARPETA_BASE)
NOMBRE_LOGO = "Logotipo"


class MenuPrincipal(tk.Tk):

    def __init__(self):

        super().__init__()

        self.title("Mr.Burger - Sistema de Punto de Venta")
        self.geometry("1300x750")
        self.minsize(1100, 650)
        self.configure(bg=CREMA)

        self.attributes("-fullscreen", True)
        self.bind("<F11>", self.alternar_pantalla)
        self.bind("<Escape>", self.salir_pantalla)

        self.cajero_actual = CAJERO_ACTUAL

        # Catálogo de productos (ver nota en punto_venta/catalogo.py:
        # son datos de ejemplo en memoria, sin conexión a base de
        # datos todavía).
        self.categorias = catalogo.CATEGORIAS

        # Categoría actual (la primera categoría disponible)
        self.categoria_actual = self.categorias[0] if self.categorias else "comida"

        # Periodo actual del menú: "desayuno" o "almuerzo", según
        # la hora del sistema.
        self.periodo_actual = catalogo.obtener_periodo_actual()

        # Tipo de pedido / carrito: administrados por PanelCarrito.

        self.logo_tk = None
        self.logo_path = buscar_logo(CARPETA_LOGO, NOMBRE_LOGO)

        self.crear_interfaz()

        # Revisa cada minuto si cambió el periodo del menú (por
        # ejemplo, de desayuno a almuerzo) para actualizar los
        # productos mostrados automáticamente.
        self.after(60000, self._revisar_cambio_periodo)

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
    # PANTALLA
    # ========================================================

    def alternar_pantalla(self, event=None):
        estado = self.attributes("-fullscreen")
        self.attributes("-fullscreen", not estado)

    def salir_pantalla(self, event=None):
        self.attributes("-fullscreen", False)

    # ========================================================
    # INTERFAZ PRINCIPAL
    # ========================================================

    def crear_interfaz(self):

        self.contenedor = tk.Frame(self, bg=CREMA)
        self.contenedor.pack(fill="both", expand=True)

        self.crear_sidebar()

        self.contenido = tk.Frame(self.contenedor, bg=CREMA)
        self.contenido.pack(side="left", fill="both", expand=True)

        # Zona central: cuadrícula de productos
        self.zona_central = tk.Frame(self.contenido, bg=CREMA)
        self.zona_central.pack(side="left", fill="both", expand=True, padx=(35, 20), pady=25)

        # Panel del carrito (a la derecha)
        self.panel_carrito = PanelCarrito(self.contenido, self)
        self.panel_carrito.pack(side="right", fill="y", padx=(0, 25), pady=25)

        self.vista_productos = VistaProductos(self.zona_central, self)
        self.vista_productos.pack(fill="both", expand=True)

    # ========================================================
    # SIDEBAR
    # ========================================================

    def crear_sidebar(self):

        self.sidebar = tk.Frame(self.contenedor, bg=ROJO, width=270)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo = tk.Frame(self.sidebar, bg=ROJO)
        logo.pack(pady=(30, 20))

        logo_mostrado = False

        logo_sidebar_path = buscar_logo(CARPETA_LOGO, "Logo_fondoBlanco")

        if logo_sidebar_path:
            try:
                img = Image.open(logo_sidebar_path).convert("RGBA")
                img.thumbnail((110, 110), FILTRO_REESCALADO)
                self.logo_sidebar_tk = ImageTk.PhotoImage(img)
                tk.Label(logo, image=self.logo_sidebar_tk, bg=ROJO).pack(pady=(0, 8))
                logo_mostrado = True
            except Exception as e:
                print(f"No se pudo cargar el logo del Sidebar: {e}")

        if not logo_mostrado:
            tk.Label(
                logo, text="♨", font=("Segoe UI", 38, "bold"), fg="#FFA51F", bg=ROJO
            ).pack()

        tk.Label(
            logo, text="Mr.Burger", font=("Segoe UI", 26, "bold"), fg="white", bg=ROJO
        ).pack()

        tk.Label(
            logo, text="DISFRUTA CADA MOMENTO", font=("Segoe UI", 9, "bold"),
            fg="#FFB72B", bg=ROJO
        ).pack(pady=(2, 0))

        tk.Frame(self.sidebar, bg=ROJO_OSCURO, height=1).pack(fill="x", padx=25, pady=(20, 10))

        # ----------------------------------------------------
        # MENÚ (categorías del dashboard del cajero)
        # ----------------------------------------------------

        self.botones_sidebar = {}

        for categoria in self.categorias:
            self.crear_boton_menu(
                catalogo.ICONOS_CATEGORIA.get(categoria, "🍽"),
                categoria.capitalize(),
                categoria,
                lambda c=categoria: self.filtrar_categoria(c)
            )

        self.crear_boton_menu("⇥", "Cerrar Caja", None, self.cerrar_caja)

        # ----------------------------------------------------
        # USUARIO
        # ----------------------------------------------------

        usuario = tk.Frame(self.sidebar, bg=ROJO_OSCURO, height=80)
        usuario.pack(side="bottom", fill="x")
        usuario.pack_propagate(False)

        avatar = tk.Canvas(usuario, width=48, height=48, bg=ROJO_OSCURO, highlightthickness=0)
        avatar.pack(side="left", padx=(18, 10), pady=15)
        avatar.create_oval(2, 2, 46, 46, fill="white", outline="")
        avatar.create_text(24, 24, text="C", font=("Segoe UI", 18, "bold"), fill=ROJO)

        datos = tk.Frame(usuario, bg=ROJO_OSCURO)
        datos.pack(side="left", pady=15)

        tk.Label(
            datos, text=self.cajero_actual, font=("Segoe UI", 12, "bold"),
            fg="white", bg=ROJO_OSCURO
        ).pack(anchor="w")

        tk.Label(
            datos, text="Cajero", font=("Segoe UI", 9), fg="#F5D8D2", bg=ROJO_OSCURO
        ).pack(anchor="w")

        tk.Label(
            usuario, text="⌄", font=("Segoe UI", 18), fg="white", bg=ROJO_OSCURO
        ).pack(side="right", padx=15)

    # ========================================================
    # BOTONES DEL SIDEBAR
    # ========================================================

    def crear_boton_menu(self, icono, texto, categoria, comando):

        activo = categoria is not None and categoria == self.categoria_actual
        color = ROJO_CLARO if activo else ROJO

        boton = tk.Frame(self.sidebar, bg=color, cursor="hand2")
        boton.pack(fill="x", padx=18, pady=5)

        label = tk.Label(
            boton, text=f"{icono}   {texto}",
            font=("Segoe UI", 13, "bold" if activo else "normal"),
            fg="white", bg=color, anchor="w", padx=15, pady=12
        )
        label.pack(fill="x")

        boton.bind("<Button-1>", lambda e: comando())
        label.bind("<Button-1>", lambda e: comando())

        def entrar(event):
            es_activo = categoria is not None and categoria == self.categoria_actual
            if not es_activo:
                boton.configure(bg=ROJO_OSCURO)
                label.configure(bg=ROJO_OSCURO)

        def salir(event):
            es_activo = categoria is not None and categoria == self.categoria_actual
            color_normal = ROJO_CLARO if es_activo else ROJO
            boton.configure(bg=color_normal)
            label.configure(bg=color_normal)

        boton.bind("<Enter>", entrar)
        boton.bind("<Leave>", salir)
        label.bind("<Enter>", entrar)
        label.bind("<Leave>", salir)

        if categoria is not None:
            self.botones_sidebar[categoria] = (boton, label, icono, texto)

    # ========================================================
    # FILTRAR POR CATEGORÍA
    # ========================================================

    def filtrar_categoria(self, categoria):

        self.categoria_actual = categoria

        for cat, (boton, label, icono, texto) in self.botones_sidebar.items():

            es_activo = cat == categoria
            color = ROJO_CLARO if es_activo else ROJO

            boton.configure(bg=color)
            label.configure(bg=color, font=("Segoe UI", 13, "bold" if es_activo else "normal"))

        self.vista_productos.dibujar_productos()

    # ========================================================
    # AGREGAR PRODUCTO AL CARRITO
    # ========================================================
    # Punto de unión entre VistaProductos (donde se hace clic en
    # un producto) y PanelCarrito (donde vive el carrito).
    # ========================================================

    def agregar_producto(self, producto):

        self.panel_carrito.agregar_producto(producto)

    # ========================================================
    # CERRAR CAJA
    # ========================================================

    def cerrar_caja(self):

        respuesta = messagebox.askyesno("Cerrar caja", "¿Deseas cerrar la caja?")

        if respuesta:
            messagebox.showinfo("Caja", "Caja cerrada correctamente.")
            self.destroy()
