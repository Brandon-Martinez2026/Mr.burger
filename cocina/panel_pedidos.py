"""
panel_pedidos.py (cocina)
------------------------------------------------------------
Cuadrícula (con scroll) de tarjetas con los pedidos: pendientes
de cocina o entregados recientemente, según la pestaña activa
en la ventana principal. Cada tarjeta muestra los productos del
pedido y, si está pendiente, un botón para marcarlo como listo.
------------------------------------------------------------
"""

import tkinter as tk

from estilos import ROJO_CLARO, ROJO, CREMA, BLANCO, TEXTO, GRIS, BORDE, VERDE, NARANJA

from basedatos import repositorio_cocina
from basedatos.conexion import ErrorBaseDatos


COLUMNAS_TOTALES = 3


class PanelPedidos(tk.Frame):
    """Muestra los pedidos como tarjetas dentro de un área con
    scroll (puede haber más pedidos de los que caben en la
    pantalla en un día ocupado)."""

    def __init__(self, parent, controlador):

        super().__init__(parent, bg=CREMA)

        self.controlador = controlador

        # ----------------------------------------------------
        # Canvas + scrollbar (patrón estándar de frame con scroll
        # en Tkinter: el frame real vive dentro del canvas).
        # ----------------------------------------------------

        self.canvas = tk.Canvas(self, bg=CREMA, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.frame_interno = tk.Frame(self.canvas, bg=CREMA)
        self._ventana_interna = self.canvas.create_window((0, 0), window=self.frame_interno, anchor="nw")

        self.frame_interno.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.bind("<Configure>", self._ajustar_ancho)

        self.canvas.bind_all("<MouseWheel>", self._sobre_rueda_raton)
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    # --------------------------------------------------------
    def _ajustar_ancho(self, event):
        self.canvas.itemconfig(self._ventana_interna, width=event.width)

    def _sobre_rueda_raton(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ========================================================
    def refrescar(self):
        """Vuelve a consultar la base de datos y redibuja todas
        las tarjetas. Se llama al abrir la pantalla, cada vez que
        el cocinero marca un pedido como listo, al cambiar de
        pestaña y automáticamente cada pocos segundos."""

        for widget in self.frame_interno.winfo_children():
            widget.destroy()

        pestana = self.controlador.pestana_actual

        try:
            if pestana == "pendientes":
                pedidos = repositorio_cocina.pedidos_pendientes()
            else:
                pedidos = repositorio_cocina.pedidos_entregados_recientes(20)
        except ErrorBaseDatos as error:
            tk.Label(
                self.frame_interno, text=f"No se pudo conectar a la base de datos:\n{error}",
                font=("Segoe UI", 12), fg=ROJO, bg=CREMA, justify="left"
            ).pack(pady=40, padx=20)
            return

        if not pedidos:

            mensaje = (
                "No hay pedidos pendientes en este momento. 🎉" if pestana == "pendientes"
                else "Todavía no se ha entregado ningún pedido."
            )

            tk.Label(
                self.frame_interno, text=mensaje, font=("Segoe UI", 14),
                fg=GRIS, bg=CREMA
            ).pack(pady=40)

            return

        for i in range(COLUMNAS_TOTALES):
            self.frame_interno.grid_columnconfigure(i, weight=1)

        fila = 0
        columna = 0

        for pedido in pedidos:

            self._crear_tarjeta(pedido, fila, columna, pestana)

            columna += 1

            if columna == COLUMNAS_TOTALES:
                columna = 0
                fila += 1

    # --------------------------------------------------------
    def _crear_tarjeta(self, pedido, fila, columna, pestana):

        tarjeta = tk.Frame(
            self.frame_interno, bg=BLANCO,
            highlightbackground=BORDE, highlightthickness=1
        )
        tarjeta.grid(row=fila, column=columna, padx=10, pady=10, sticky="nsew")

        color_cabecera = NARANJA if pestana == "pendientes" else VERDE

        cabecera = tk.Frame(tarjeta, bg=color_cabecera)
        cabecera.pack(fill="x")

        tipo = f"Mesa {pedido['mesa']}" if pedido.get("tipo_pedido") == "mesa" else "Para Llevar"

        tk.Label(
            cabecera, text=f"Pedido #{pedido['id']}  ·  {tipo}",
            font=("Segoe UI", 12, "bold"), fg="white", bg=color_cabecera
        ).pack(side="left", padx=12, pady=8)

        hora = pedido.get("fecha", "").split(" ")[-1][:5]

        tk.Label(
            cabecera, text=hora, font=("Segoe UI", 10), fg="white", bg=color_cabecera
        ).pack(side="right", padx=12)

        cuerpo = tk.Frame(tarjeta, bg=BLANCO)
        cuerpo.pack(fill="both", expand=True, padx=12, pady=10)

        for item in pedido.get("items", []):

            tk.Label(
                cuerpo, text=f"•  {item['cantidad']}x {item['nombre']}",
                font=("Segoe UI", 11), fg=TEXTO, bg=BLANCO, anchor="w", justify="left"
            ).pack(fill="x", pady=2)

        if pedido.get("notas"):

            tk.Label(
                cuerpo, text=f"Nota: {pedido['notas']}", font=("Segoe UI", 9, "italic"),
                fg=GRIS, bg=BLANCO, wraplength=220, justify="left", anchor="w"
            ).pack(fill="x", pady=(8, 0))

        tk.Label(
            cuerpo, text=f"Cajero: {pedido.get('cajero', '')}", font=("Segoe UI", 9),
            fg=GRIS, bg=BLANCO, anchor="w"
        ).pack(fill="x", pady=(8, 0))

        if pestana == "pendientes":

            tk.Button(
                tarjeta, text="✔  Marcar como Listo", font=("Segoe UI", 11, "bold"),
                bg=ROJO_CLARO, fg="white", relief="flat",
                activebackground=ROJO, activeforeground="white",
                cursor="hand2",
                command=lambda id_pedido=pedido["id"]: self.controlador.marcar_entregado(id_pedido)
            ).pack(fill="x", padx=12, pady=(0, 12), ipady=7)

        else:

            tk.Label(
                tarjeta, text="✔ Entregado", font=("Segoe UI", 10, "bold"),
                fg=VERDE, bg=BLANCO
            ).pack(pady=(0, 12))
