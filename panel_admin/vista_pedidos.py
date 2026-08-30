"""
vista_pedidos.py
------------------------------------------------------------
Sección "Pedidos" del Panel de Administrador: supervisión de
los pedidos más recientes tomados por los cajeros.
------------------------------------------------------------
"""

import tkinter as tk
from tkinter import ttk

from estilos import CREMA, BLANCO, GRIS, BORDE, crear_encabezado, preparar_estilo_tabla

import datos_ventas


class VistaPedidos(tk.Frame):

    def __init__(self, parent, controlador):

        super().__init__(parent, bg=CREMA)

        self.controlador = controlador

        self._crear_interfaz()

    # ========================================================
    def _crear_interfaz(self):

        crear_encabezado(self, "Pedidos", "Supervisa los pedidos más recientes tomados por los cajeros")

        preparar_estilo_tabla(self)

        marco_tabla = tk.Frame(self, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
        marco_tabla.pack(fill="both", expand=True)

        columnas = ("id", "fecha", "cajero", "tipo", "productos", "total", "estado")

        tabla = ttk.Treeview(marco_tabla, columns=columnas, show="headings", style="Mr.Treeview")

        titulos = {
            "id": "#", "fecha": "Fecha", "cajero": "Cajero", "tipo": "Pedido",
            "productos": "Productos", "total": "Total", "estado": "Estado"
        }
        anchos = {"id": 50, "fecha": 160, "cajero": 120, "tipo": 120, "productos": 260, "total": 100, "estado": 110}

        for col in columnas:
            tabla.heading(col, text=titulos[col])
            tabla.column(col, width=anchos[col], anchor="center" if col not in ("productos",) else "w")

        scroll = ttk.Scrollbar(marco_tabla, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=scroll.set)

        tabla.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        ventas = sorted(datos_ventas.cargar_ventas(), key=lambda v: v.get("fecha", ""), reverse=True)

        for venta in ventas[:100]:

            tipo = f"Mesa {venta['mesa']}" if venta.get("tipo_pedido") == "mesa" else "Para Llevar"

            resumen_items = ", ".join(
                f"{it['cantidad']}x {it['nombre']}" for it in venta.get("items", [])
            )

            tabla.insert(
                "", "end",
                values=(
                    venta["id"], venta.get("fecha", ""), venta.get("cajero", ""),
                    tipo, resumen_items, f"Q{venta.get('total', 0):.2f}", "✔ Completado"
                )
            )

        if not ventas:
            tk.Label(
                self, text="Todavía no se ha tomado ningún pedido.",
                font=("Segoe UI", 10), fg=GRIS, bg=CREMA
            ).pack(pady=15)
