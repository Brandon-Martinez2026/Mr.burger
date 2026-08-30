"""
app.py (panel_admin)
------------------------------------------------------------
Ventana principal del Panel de Administrador (antes todo esto
vivía en un único archivo MenuAdministrador.py). Esta clase solo
se encarga de la ventana, el sidebar y de cambiar entre las
secciones del dashboard, cada una en su propio archivo:

    panel_admin/vista_inventario.py
    panel_admin/vista_categorias.py
    panel_admin/vista_cajeros.py
    panel_admin/vista_ventas.py
    panel_admin/vista_pedidos.py
    panel_admin/vista_reportes.py
------------------------------------------------------------
"""

import os
import sys
import subprocess

import tkinter as tk
from tkinter import messagebox

try:
    from PIL import Image, ImageTk
except ImportError:
    print("Necesitas instalar Pillow: pip install pillow")
    sys.exit(1)

from estilos import (
    ROJO, ROJO_CLARO, ROJO_OSCURO, CREMA,
    FILTRO_REESCALADO, resolver_carpeta_recursos, buscar_logo
)
from panel_admin.datos_admin import RepositorioProductos
from panel_admin.vista_inventario import VistaInventario
from panel_admin.vista_categorias import VistaCategorias
from panel_admin.vista_cajeros import VistaCajeros
from panel_admin.vista_ventas import VistaVentas
from panel_admin.vista_pedidos import VistaPedidos
from panel_admin.vista_reportes import VistaReportes


ADMIN_ACTUAL = "Administrador"  # nombre de respaldo si se abre sin pasar por el login

CARPETA_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARPETA_LOGO = resolver_carpeta_recursos(CARPETA_BASE)

# Cada entrada del sidebar y la clase de Vista que le corresponde.
SECCIONES = [
    ("📦", "Inventario", "inventario", VistaInventario),
    ("🏷", "Categorías", "categorias", VistaCategorias),
    ("🧑‍🍳", "Cajeros", "cajeros", VistaCajeros),
    ("💵", "Ventas", "ventas", VistaVentas),
    ("📋", "Pedidos", "pedidos", VistaPedidos),
    ("📊", "Reportes", "reportes", VistaReportes),
]


class MenuAdministrador(tk.Tk):

    def __init__(self, id_usuario=None, nombre_admin=None):

        super().__init__()

        self.title("Mr.Burger - Panel de Administrador")
        self.geometry("1360x780")
        self.minsize(1150, 680)
        self.configure(bg=CREMA)

        self.attributes("-fullscreen", True)
        self.bind("<F11>", self.alternar_pantalla)
        self.bind("<Escape>", self.salir_pantalla)

        # Sesión real del administrador que inició sesión con sus
        # credenciales (usuario/contraseña) en IniciarSesion.py.
        self.id_usuario = id_usuario
        self.nombre_admin = nombre_admin or ADMIN_ACTUAL

        # Repositorio de productos/categorías: consulta y
        # actualiza MySQL de verdad (ver basedatos/repositorio_productos.py).
        self.repo = RepositorioProductos()

        # Vista actualmente seleccionada en el sidebar
        self.vista_actual = "inventario"
        self.vista_frame = None

        # Filtros usados en la vista de inventario
        self.filtro_categoria = "todas"
        self.filtro_periodo = "todos"

        self.logo_sidebar_tk = None

        self.crear_interfaz()

    # ========================================================
    # PANTALLA
    # ========================================================

    def alternar_pantalla(self, event=None):
        estado = self.attributes("-fullscreen")
        self.attributes("-fullscreen", not estado)

    def salir_pantalla(self, event=None):
        self.attributes("-fullscreen", False)

    # ========================================================
    # INTERFAZ GENERAL
    # ========================================================

    def crear_interfaz(self):

        self.contenedor = tk.Frame(self, bg=CREMA)
        self.contenedor.pack(fill="both", expand=True)

        self.crear_sidebar()

        self.contenido = tk.Frame(self.contenedor, bg=CREMA)
        self.contenido.pack(side="left", fill="both", expand=True, padx=30, pady=25)

        self.mostrar_vista("inventario")

    # ========================================================
    # SIDEBAR
    # ========================================================

    def crear_sidebar(self):

        self.sidebar = tk.Frame(self.contenedor, bg=ROJO, width=270)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo = tk.Frame(self.sidebar, bg=ROJO)
        logo.pack(pady=(30, 20))

        logo_path = buscar_logo(CARPETA_LOGO, "Logo_fondoBlanco")
        logo_mostrado = False

        if logo_path:
            try:
                img = Image.open(logo_path).convert("RGBA")
                img.thumbnail((100, 100), FILTRO_REESCALADO)
                self.logo_sidebar_tk = ImageTk.PhotoImage(img)
                tk.Label(logo, image=self.logo_sidebar_tk, bg=ROJO).pack(pady=(0, 8))
                logo_mostrado = True
            except Exception as e:
                print(f"No se pudo cargar el logo del Sidebar: {e}")

        if not logo_mostrado:
            tk.Label(
                logo, text="♨", font=("Segoe UI", 34, "bold"), fg="#FFA51F", bg=ROJO
            ).pack()

        tk.Label(
            logo, text="Mr.Burger", font=("Segoe UI", 23, "bold"), fg="white", bg=ROJO
        ).pack()

        tk.Label(
            logo, text="PANEL DE ADMINISTRADOR", font=("Segoe UI", 9, "bold"),
            fg="#FFB72B", bg=ROJO
        ).pack(pady=(2, 0))

        tk.Frame(self.sidebar, bg=ROJO_OSCURO, height=1).pack(fill="x", padx=25, pady=(20, 10))

        # ----------------------------------------------------
        # OPCIONES DEL MENÚ
        # ----------------------------------------------------

        self.botones_sidebar = {}

        for icono, texto, vista, _clase_vista in SECCIONES:
            self.crear_boton_menu(icono, texto, vista, lambda v=vista: self.mostrar_vista(v))

        self.crear_boton_menu("⇥", "Cerrar Sesión", None, self.cerrar_sesion)

        # ----------------------------------------------------
        # USUARIO
        # ----------------------------------------------------

        usuario = tk.Frame(self.sidebar, bg=ROJO_OSCURO, height=80)
        usuario.pack(side="bottom", fill="x")
        usuario.pack_propagate(False)

        avatar = tk.Canvas(usuario, width=48, height=48, bg=ROJO_OSCURO, highlightthickness=0)
        avatar.pack(side="left", padx=(18, 10), pady=15)
        avatar.create_oval(2, 2, 46, 46, fill="white", outline="")
        inicial = (self.nombre_admin or "?")[0].upper()
        avatar.create_text(24, 24, text=inicial, font=("Segoe UI", 18, "bold"), fill=ROJO)

        datos = tk.Frame(usuario, bg=ROJO_OSCURO)
        datos.pack(side="left", pady=15)

        tk.Label(
            datos, text=self.nombre_admin, font=("Segoe UI", 12, "bold"), fg="white", bg=ROJO_OSCURO
        ).pack(anchor="w")

        tk.Label(
            datos, text="Administrador", font=("Segoe UI", 9), fg="#F5D8D2", bg=ROJO_OSCURO
        ).pack(anchor="w")

    # ========================================================
    # BOTÓN DEL SIDEBAR
    # ========================================================

    def crear_boton_menu(self, icono, texto, vista, comando):

        activo = vista is not None and vista == self.vista_actual
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
            es_activo = vista is not None and vista == self.vista_actual
            if not es_activo:
                boton.configure(bg=ROJO_OSCURO)
                label.configure(bg=ROJO_OSCURO)

        def salir(event):
            es_activo = vista is not None and vista == self.vista_actual
            color_normal = ROJO_CLARO if es_activo else ROJO
            boton.configure(bg=color_normal)
            label.configure(bg=color_normal)

        boton.bind("<Enter>", entrar)
        boton.bind("<Leave>", salir)
        label.bind("<Enter>", entrar)
        label.bind("<Leave>", salir)

        if vista is not None:
            self.botones_sidebar[vista] = (boton, label, icono, texto)

    def _resaltar_boton_activo(self):

        for vista, (boton, label, icono, texto) in self.botones_sidebar.items():
            activo = vista == self.vista_actual
            color = ROJO_CLARO if activo else ROJO
            boton.configure(bg=color)
            label.configure(bg=color, font=("Segoe UI", 13, "bold" if activo else "normal"))

    # ========================================================
    # CERRAR SESIÓN
    # ========================================================

    def cerrar_sesion(self):

        respuesta = messagebox.askyesno("Cerrar sesión", "¿Deseas cerrar la sesión de administrador?")

        if not respuesta:
            return

        archivo_login = os.path.join(CARPETA_BASE, "IniciarSesion.py")

        if os.path.isfile(archivo_login):
            try:
                subprocess.Popen([sys.executable, archivo_login])
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir Iniciar Sesión:\n{e}")

        self.destroy()

    # ========================================================
    # CAMBIAR DE VISTA
    # ========================================================
    # Cada sección del dashboard es una clase (tk.Frame) en su
    # propio archivo (ver diccionario SECCIONES arriba). Cambiar
    # de vista simplemente destruye la anterior y crea la nueva.
    # ========================================================

    def mostrar_vista(self, vista):

        self.vista_actual = vista
        self._resaltar_boton_activo()

        if self.vista_frame is not None:
            self.vista_frame.destroy()

        clase_vista = next(
            (clase for _i, _t, v, clase in SECCIONES if v == vista), None
        )

        if clase_vista is None:
            return

        self.vista_frame = clase_vista(self.contenido, self)
        self.vista_frame.pack(fill="both", expand=True)
