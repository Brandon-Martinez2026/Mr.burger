"""
vista_ventas.py
------------------------------------------------------------
Sección "Ventas" del Panel de Administrador: historial
completo de ventas realizadas, con filtros por cajero y método
de pago.
------------------------------------------------------------
"""

import tkinter as tk
from tkinter import ttk

from estilos import CREMA, BLANCO, TEXTO, GRIS, BORDE, ROJO, crear_encabezado, preparar_estilo_tabla
from panel_admin.datos_admin import METODOS_PAGO
from panel_admin.dialogo_detalle_venta import mostrar_detalle_venta

import datos_ventas


class VistaVentas(tk.Frame):

    def __init__(self, parent, controlador):

        super().__init__(parent, bg=CREMA)

        self.controlador = controlador

        self._crear_interfaz()

    # ========================================================
    def _crear_interfaz(self):

        crear_encabezado(self, "Ventas", "Historial completo de ventas realizadas")

        barra = tk.Frame(self, bg=CREMA)
        barra.pack(fill="x", pady=(0, 12))

        todas = datos_ventas.cargar_ventas()
        cajeros = sorted({v.get("cajero", "Desconocido") for v in todas})

        tk.Label(barra, text="Cajero:", font=("Segoe UI", 10, "bold"), fg=TEXTO, bg=CREMA).pack(side="left")

        self.combo_ventas_cajero = ttk.Combobox(
            barra, values=["todos"] + cajeros, state="readonly", width=16
        )
        self.combo_ventas_cajero.set("todos")
        self.combo_ventas_cajero.pack(side="left", padx=(6, 18))
        self.combo_ventas_cajero.bind("<<ComboboxSelected>>", lambda e: self._filtrar())

        tk.Label(barra, text="Método:", font=("Segoe UI", 10, "bold"), fg=TEXTO, bg=CREMA).pack(side="left")

        self.combo_ventas_metodo = ttk.Combobox(
            barra, values=["todos"] + list(METODOS_PAGO.values()), state="readonly", width=14
        )
        self.combo_ventas_metodo.set("todos")
        self.combo_ventas_metodo.pack(side="left", padx=(6, 18))
        self.combo_ventas_metodo.bind("<<ComboboxSelected>>", lambda e: self._filtrar())

        tk.Label(
            barra, text=f"Total histórico: Q{datos_ventas.total_de(todas):.2f}",
            font=("Segoe UI", 11, "bold"), fg=ROJO, bg=CREMA
        ).pack(side="right")

        preparar_estilo_tabla(self)

        marco_tabla = tk.Frame(self, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
        marco_tabla.pack(fill="both", expand=True)

        columnas = ("id", "fecha", "cajero", "tipo", "metodo", "total")

        self.tabla_ventas = ttk.Treeview(
            marco_tabla, columns=columnas, show="headings", style="Mr.Treeview"
        )

        titulos = {
            "id": "#", "fecha": "Fecha", "cajero": "Cajero",
            "tipo": "Pedido", "metodo": "Método", "total": "Total"
        }
        anchos = {"id": 50, "fecha": 160, "cajero": 130, "tipo": 130, "metodo": 100, "total": 110}

        for col in columnas:
            self.tabla_ventas.heading(col, text=titulos[col])
            self.tabla_ventas.column(col, width=anchos[col], anchor="center")

        scroll = ttk.Scrollbar(marco_tabla, orient="vertical", command=self.tabla_ventas.yview)
        self.tabla_ventas.configure(yscrollcommand=scroll.set)

        self.tabla_ventas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.tabla_ventas.bind("<Double-1>", lambda e: self._ver_detalle_venta())

        tk.Label(
            self, text="Doble clic sobre una venta para ver el detalle de productos.",
            font=("Segoe UI", 9), fg=GRIS, bg=CREMA
        ).pack(anchor="w", pady=(6, 0))

        self._filtrar()

    # ========================================================
    def _filtrar(self):

        for fila in self.tabla_ventas.get_children():
            self.tabla_ventas.delete(fila)

        cajero = self.combo_ventas_cajero.get()
        metodo_texto = self.combo_ventas_metodo.get()

        for venta in sorted(datos_ventas.cargar_ventas(), key=lambda v: v.get("fecha", ""), reverse=True):

            if cajero != "todos" and venta.get("cajero") != cajero:
                continue

            metodo_venta = METODOS_PAGO.get(venta.get("metodo_pago"), venta.get("metodo_pago"))

            if metodo_texto != "todos" and metodo_venta != metodo_texto:
                continue

            tipo = f"Mesa {venta['mesa']}" if venta.get("tipo_pedido") == "mesa" else "Para Llevar"

            self.tabla_ventas.insert(
                "", "end", iid=str(venta["id"]),
                values=(
                    venta["id"], venta.get("fecha", ""), venta.get("cajero", ""),
                    tipo, metodo_venta, f"Q{venta.get('total', 0):.2f}"
                )
            )

    # ========================================================
    def _ver_detalle_venta(self):

        seleccion = self.tabla_ventas.selection()

        if not seleccion:
            return

        id_venta = int(seleccion[0])
        venta = next((v for v in datos_ventas.cargar_ventas() if v["id"] == id_venta), None)

        if venta is None:
            return

        mostrar_detalle_venta(self, venta)
