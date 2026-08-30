"""
estilos.py
------------------------------------------------------------
Colores, filtros de imagen y utilidades de interfaz que se
comparten entre el Punto de Venta (punto_venta/) y el Panel de
Administrador (panel_admin/). Al estar en un único lugar, si el
negocio decide cambiar la paleta de colores solo hay que
editarla aquí.
------------------------------------------------------------
"""

import os

from tkinter import ttk

try:
    from PIL import Image
except ImportError:
    Image = None


# ============================================================
# COLORES
# ============================================================

ROJO = "#C0392B"
ROJO_CLARO = "#D1382A"
ROJO_OSCURO = "#7A2418"

CREMA = "#FBF0DC"
CREMA_CLARO = "#FFF9ED"
BLANCO = "#FFFFFF"

NARANJA = "#E8963C"
NARANJA_CLARO = "#F5A623"

VERDE = "#4CAF50"

TEXTO = "#2B2118"
GRIS = "#777777"
BORDE = "#D9C9A8"


# ============================================================
# FILTRO DE REESCALADO DE IMÁGENES (compatible con distintas
# versiones de Pillow)
# ============================================================

if Image is not None:
    try:
        FILTRO_REESCALADO = Image.Resampling.LANCZOS
    except AttributeError:
        FILTRO_REESCALADO = getattr(Image, "LANCZOS", None) or getattr(Image, "ANTIALIAS")
else:
    FILTRO_REESCALADO = None


# ============================================================
# RUTAS DE RECURSOS
# ============================================================

def resolver_carpeta_recursos(base):
    """Devuelve la carpeta 'Recursos' del proyecto sin importar si
    está escrita en mayúsculas o minúsculas (compatibilidad entre
    sistemas operativos)."""

    for nombre in ("Recursos", "recursos"):
        ruta = os.path.join(base, nombre)
        if os.path.isdir(ruta):
            return ruta

    return os.path.join(base, "Recursos")


def resolver_carpeta_decoraciones(base):
    """Devuelve la carpeta 'Decoraciones' del proyecto sin importar
    si está escrita en mayúsculas o minúsculas."""

    for nombre in ("Decoraciones", "decoraciones"):
        ruta = os.path.join(base, nombre)
        if os.path.isdir(ruta):
            return ruta

    return os.path.join(base, "Decoraciones")


def buscar_logo(carpeta, nombre_base):
    """Busca el archivo del logo probando extensiones comunes."""

    for ext in (".png", ".jpg", ".jpeg", ".webp", ".bmp"):
        ruta = os.path.join(carpeta, nombre_base + ext)
        if os.path.isfile(ruta):
            return ruta

    return None


# ============================================================
# WIDGETS / ESTILOS REUTILIZABLES (Treeview, encabezados, etc.)
# ============================================================

def preparar_estilo_tabla(ventana):
    """Configura y devuelve el estilo 'Mr.Treeview' usado por las
    tablas (Treeview) de ambos dashboards."""

    estilo = ttk.Style(ventana)

    try:
        estilo.theme_use("clam")
    except Exception:
        pass

    estilo.configure(
        "Mr.Treeview",
        background=BLANCO,
        fieldbackground=BLANCO,
        foreground=TEXTO,
        rowheight=32,
        font=("Segoe UI", 10)
    )

    estilo.configure(
        "Mr.Treeview.Heading",
        background=ROJO,
        foreground="white",
        font=("Segoe UI", 10, "bold"),
        relief="flat"
    )

    estilo.map(
        "Mr.Treeview",
        background=[("selected", NARANJA_CLARO)],
        foreground=[("selected", "white")]
    )

    return estilo


def crear_encabezado(contenedor, titulo, subtitulo=""):
    """Crea el encabezado (título + subtítulo) reutilizado por
    todas las vistas de ambos dashboards."""

    import tkinter as tk

    encabezado = tk.Frame(contenedor, bg=CREMA)
    encabezado.pack(fill="x", pady=(0, 18))

    tk.Label(
        encabezado, text=titulo, font=("Segoe UI", 26, "bold"),
        fg=TEXTO, bg=CREMA
    ).pack(side="left")

    if subtitulo:
        tk.Label(
            encabezado, text=subtitulo, font=("Segoe UI", 10),
            fg=GRIS, bg=CREMA
        ).pack(side="left", padx=(15, 0), pady=(10, 0))

    return encabezado
