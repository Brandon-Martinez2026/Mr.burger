"""
app.py (cocina)
------------------------------------------------------------
Ventana principal de la pantalla de Cocina: muestra los pedidos
que ya se pagaron y fueron enviados a cocina (estado
'enviado_cocina'), para que el cocinero los prepare y los marque
como listos/entregados con sp_marcar_pedido_entregado. También
tiene una pestaña de "Entregados recientes" a modo de historial.

Se refresca sola cada pocos segundos, porque corre en un proceso
aparte del Punto de Venta y necesita enterarse de los pedidos
nuevos que va guardando el cajero en la base de datos.
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
    ROJO, ROJO_OSCURO, CREMA, resolver_carpeta_recursos, buscar_logo, FILTRO_REESCALADO
)

from basedatos import repositorio_cocina
from basedatos.conexion import ErrorBaseDatos

from cocina.panel_pedidos import PanelPedidos


COCINERO_ACTUAL_POR_DEFECTO = "Cocina"

CARPETA_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARPETA_LOGO = resolver_carpeta_recursos(CARPETA_BASE)

# Cada cuántos milisegundos se vuelve a consultar la base de
# datos para ver si llegaron pedidos nuevos.
INTERVALO_REFRESCO_MS = 8000


class VentanaCocina(tk.Tk):

    def __init__(self, id_usuario=None, nombre_cocinero=None):

        super().__init__()

        self.title("Mr.Burger - Cocina")
        self.geometry("1200x720")
        self.minsize(1000, 600)
        self.configure(bg=CREMA)

        self.attributes("-fullscreen", True)
        self.bind("<F11>", self.alternar_pantalla)
        self.bind("<Escape>", self.salir_pantalla)

        self.id_usuario = id_usuario
        self.nombre_cocinero = nombre_cocinero or COCINERO_ACTUAL_POR_DEFECTO

        # "pendientes" o "entregados"
        self.pestana_actual = "pendientes"

        self.logo_tk = None
        self.panel_pedidos = None

        self._crear_interfaz()

        # Primer refresco (pequeño delay para que la ventana ya
        # esté dibujada) y luego uno automático cada rato.
        self.after(200, self._refrescar_periodicamente)

    # ========================================================
    # PANTALLA
    # ========================================================

    def alternar_pantalla(self, event=None):
        estado = self.attributes("-fullscreen")
        self.attributes("-fullscreen", not estado)

    def salir_pantalla(self, event=None):
        self.attributes("-fullscreen", False)

    # ========================================================
    # INTERFAZ
    # ========================================================

    def _crear_interfaz(self):

        self._crear_encabezado()

        self.panel_pedidos = PanelPedidos(self, self)
        self.panel_pedidos.pack(fill="both", expand=True, padx=25, pady=(0, 20))

    def _crear_encabezado(self):

        cabecera = tk.Frame(self, bg=ROJO)
        cabecera.pack(fill="x")

        izquierda = tk.Frame(cabecera, bg=ROJO)
        izquierda.pack(side="left", padx=25, pady=15)

        logo_path = buscar_logo(CARPETA_LOGO, "Logo_fondoBlanco")

        if logo_path:
            try:
                img = Image.open(logo_path).convert("RGBA")
                img.thumbnail((42, 42), FILTRO_REESCALADO)
                self.logo_tk = ImageTk.PhotoImage(img)
                tk.Label(izquierda, image=self.logo_tk, bg=ROJO).pack(side="left", padx=(0, 10))
            except Exception as e:
                print(f"No se pudo cargar el logo: {e}")

        tk.Label(
            izquierda, text="Mr.Burger — Cocina", font=("Segoe UI", 18, "bold"),
            fg="white", bg=ROJO
        ).pack(side="left")

        derecha = tk.Frame(cabecera, bg=ROJO)
        derecha.pack(side="right", padx=25, pady=15)

        tk.Label(
            derecha, text=self.nombre_cocinero, font=("Segoe UI", 11, "bold"),
            fg="white", bg=ROJO
        ).pack(side="right", padx=(15, 6))

        self.btn_pestana_entregados = tk.Button(
            derecha, text="Entregados recientes", font=("Segoe UI", 10),
            relief="flat", bd=0, cursor="hand2",
            command=lambda: self._cambiar_pestana("entregados")
        )
        self.btn_pestana_entregados.pack(side="right", padx=6, ipady=4, ipadx=6)

        self.btn_pestana_pendientes = tk.Button(
            derecha, text="Pendientes", font=("Segoe UI", 10, "bold"),
            relief="flat", bd=0, cursor="hand2",
            command=lambda: self._cambiar_pestana("pendientes")
        )
        self.btn_pestana_pendientes.pack(side="right", padx=6, ipady=4, ipadx=6)

        self._actualizar_botones_pestana()

    def _actualizar_botones_pestana(self):

        activo_pendientes = self.pestana_actual == "pendientes"

        self.btn_pestana_pendientes.configure(
            bg="white" if activo_pendientes else ROJO_OSCURO,
            fg=ROJO if activo_pendientes else "white",
            font=("Segoe UI", 10, "bold" if activo_pendientes else "normal")
        )

        self.btn_pestana_entregados.configure(
            bg="white" if not activo_pendientes else ROJO_OSCURO,
            fg=ROJO if not activo_pendientes else "white",
            font=("Segoe UI", 10, "bold" if not activo_pendientes else "normal")
        )

    def _cambiar_pestana(self, pestana):

        self.pestana_actual = pestana
        self._actualizar_botones_pestana()
        self.panel_pedidos.refrescar()

    # ========================================================
    # ACCIONES
    # ========================================================

    def marcar_entregado(self, id_pedido):

        try:
            repositorio_cocina.marcar_entregado(id_pedido)
        except ErrorBaseDatos as error:
            messagebox.showerror("Mr.Burger", str(error))
            return

        self.panel_pedidos.refrescar()

    # ========================================================
    # REFRESCO AUTOMÁTICO
    # ========================================================

    def _refrescar_periodicamente(self):

        self.panel_pedidos.refrescar()
        self.after(INTERVALO_REFRESCO_MS, self._refrescar_periodicamente)
