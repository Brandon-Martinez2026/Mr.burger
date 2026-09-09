"""
vista_reportes.py
------------------------------------------------------------
Sección "Reportes" del Panel de Administrador: resumen general
del desempeño del negocio (tarjetas, ventas por método de pago
y productos más vendidos).
------------------------------------------------------------
"""

import datetime

import tkinter as tk

from estilos import CREMA, CREMA_CLARO, BLANCO, TEXTO, GRIS, BORDE, ROJO, NARANJA, crear_encabezado
from panel_admin.datos_admin import METODOS_PAGO

import datos_ventas


class VistaReportes(tk.Frame):

    def __init__(self, parent, controlador):

        super().__init__(parent, bg=CREMA)

        self.controlador = controlador
        self.repo = controlador.repo

        self._crear_interfaz()

    # ========================================================
    def _crear_interfaz(self):

        crear_encabezado(self, "Reportes", "Resumen general del desempeño del negocio")

        ventas = datos_ventas.cargar_ventas()

        contenedor = tk.Frame(self, bg=CREMA)
        contenedor.pack(fill="both", expand=True)

        # ----------------------------------------------------
        # TARJETAS DE RESUMEN
        # ----------------------------------------------------

        tarjetas = tk.Frame(contenedor, bg=CREMA)
        tarjetas.pack(fill="x", pady=(0, 20))

        hoy = datetime.date.today().isoformat()
        ventas_hoy = [v for v in ventas if v.get("fecha", "").startswith(hoy)]

        total_historico = datos_ventas.total_de(ventas)
        total_hoy = datos_ventas.total_de(ventas_hoy)
        promedio = (total_historico / len(ventas)) if ventas else 0

        stock_bajo = self.repo.productos_con_poco_stock(limite=5)

        datos_tarjetas = [
            ("💵", "Ventas de Hoy", f"Q{total_hoy:.2f}", f"{len(ventas_hoy)} venta(s)"),
            ("📈", "Total Histórico", f"Q{total_historico:.2f}", f"{len(ventas)} venta(s) en total"),
            ("🧾", "Ticket Promedio", f"Q{promedio:.2f}", "por venta"),
            ("📦", "Productos con Poco Stock", str(len(stock_bajo)), "5 unidades o menos"),
        ]

        for icono, titulo, valor, extra in datos_tarjetas:

            tarjeta = tk.Frame(tarjetas, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
            tarjeta.pack(side="left", fill="both", expand=True, padx=6)

            tk.Label(tarjeta, text=icono, font=("Segoe UI Emoji", 22), bg=BLANCO).pack(anchor="w", padx=15, pady=(15, 0))
            tk.Label(tarjeta, text=titulo, font=("Segoe UI", 10), fg=GRIS, bg=BLANCO).pack(anchor="w", padx=15)
            tk.Label(tarjeta, text=valor, font=("Segoe UI", 20, "bold"), fg=ROJO, bg=BLANCO).pack(anchor="w", padx=15)
            tk.Label(tarjeta, text=extra, font=("Segoe UI", 9), fg=GRIS, bg=BLANCO).pack(anchor="w", padx=15, pady=(0, 15))

        # ----------------------------------------------------
        # VENTAS POR MÉTODO DE PAGO
        # ----------------------------------------------------

        detalle = tk.Frame(contenedor, bg=CREMA)
        detalle.pack(fill="both", expand=True)

        panel_metodos = tk.Frame(detalle, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
        panel_metodos.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(
            panel_metodos, text="Ventas por Método de Pago", font=("Segoe UI", 13, "bold"),
            fg=TEXTO, bg=BLANCO
        ).pack(anchor="w", padx=18, pady=(15, 10))

        totales_metodo = {"efectivo": 0.0, "tarjeta": 0.0, "mixto": 0.0}

        for venta in ventas:
            metodo = venta.get("metodo_pago")
            if metodo in totales_metodo:
                totales_metodo[metodo] += venta.get("total", 0)

        maximo = max(totales_metodo.values()) if any(totales_metodo.values()) else 1

        for metodo, nombre in METODOS_PAGO.items():

            fila = tk.Frame(panel_metodos, bg=BLANCO)
            fila.pack(fill="x", padx=18, pady=6)

            tk.Label(
                fila, text=f"{nombre}: Q{totales_metodo[metodo]:.2f}",
                font=("Segoe UI", 10), fg=TEXTO, bg=BLANCO
            ).pack(anchor="w")

            barra_fondo = tk.Frame(fila, bg=CREMA_CLARO, height=14)
            barra_fondo.pack(fill="x", pady=(3, 0))

            ancho_pct = totales_metodo[metodo] / maximo if maximo else 0

            barra = tk.Frame(barra_fondo, bg=NARANJA, height=14)
            barra.place(relx=0, rely=0, relwidth=max(ancho_pct, 0.01), relheight=1)

        tk.Frame(panel_metodos, bg=BLANCO, height=10).pack()

        # ----------------------------------------------------
        # PRODUCTOS MÁS VENDIDOS
        # ----------------------------------------------------

        panel_top = tk.Frame(detalle, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
        panel_top.pack(side="left", fill="both", expand=True, padx=(10, 0))

        tk.Label(
            panel_top, text="Productos Más Vendidos", font=("Segoe UI", 13, "bold"),
            fg=TEXTO, bg=BLANCO
        ).pack(anchor="w", padx=18, pady=(15, 10))

        conteo = {}

        for venta in ventas:
            for item in venta.get("items", []):
                conteo[item["nombre"]] = conteo.get(item["nombre"], 0) + item["cantidad"]

        top = sorted(conteo.items(), key=lambda kv: -kv[1])[:6]

        if not top:
            tk.Label(
                panel_top, text="Aún no hay ventas registradas.",
                font=("Segoe UI", 10), fg=GRIS, bg=BLANCO
            ).pack(padx=18, pady=10, anchor="w")
        else:
            for nombre, cantidad in top:

                fila = tk.Frame(panel_top, bg=BLANCO)
                fila.pack(fill="x", padx=18, pady=4)

                tk.Label(
                    fila, text=nombre, font=("Segoe UI", 10), fg=TEXTO, bg=BLANCO
                ).pack(side="left")

                tk.Label(
                    fila, text=f"{cantidad} vendidos", font=("Segoe UI", 10, "bold"),
                    fg=ROJO, bg=BLANCO
                ).pack(side="right")
