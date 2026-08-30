"""
vista_productos.py
------------------------------------------------------------
Zona central del Punto de Venta: encabezado con el periodo del
menú, buscador y la cuadrícula de productos en los que el
cajero da clic para agregarlos al carrito.
------------------------------------------------------------
"""

import tkinter as tk

from estilos import CREMA, BLANCO, TEXTO, GRIS, ROJO, NARANJA, BORDE
from punto_venta import catalogo


class VistaProductos(tk.Frame):
    """Frame que se coloca en la zona central de la ventana
    principal del Punto de Venta. 'controlador' es la instancia
    de MenuPrincipal (punto_venta/app.py), de la cual se leen
    la categoría/periodo actuales y a la que se avisa cuando se
    agrega un producto al carrito."""

    def __init__(self, parent, controlador):

        super().__init__(parent, bg=CREMA)

        self.controlador = controlador

        self._crear_cabecera()

        self.productos_frame = tk.Frame(self, bg=CREMA)
        self.productos_frame.pack(fill="both", expand=True)

        self.dibujar_productos()

        self._crear_fila_cliente()

    # ========================================================
    # CABECERA (título del periodo + buscador)
    # ========================================================

    def _crear_cabecera(self):

        titulo_texto = (
            "Menú de Desayuno"
            if self.controlador.periodo_actual == "desayuno"
            else "Menú de Almuerzo"
        )

        encabezado = tk.Frame(self, bg=CREMA)
        encabezado.pack(fill="x", pady=(0, 18))

        tk.Label(
            encabezado, text=titulo_texto, font=("Segoe UI", 28, "bold"),
            fg=TEXTO, bg=CREMA
        ).pack(side="left")

        horario_texto = (
            "🕐  Disponible de 7:00 a 11:00"
            if self.controlador.periodo_actual == "desayuno"
            else "🕐  Disponible de 11:00 a 2:00"
        )

        tk.Label(
            encabezado, text=horario_texto, font=("Segoe UI", 10),
            fg=GRIS, bg=CREMA
        ).pack(side="left", padx=(15, 0), pady=(10, 0))

        # ----------------------------------------------------
        # BUSCADOR
        # ----------------------------------------------------

        buscador = tk.Frame(self, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
        buscador.pack(fill="x", pady=(0, 15))

        self.buscar_entry = tk.Entry(
            buscador, font=("Segoe UI", 13), bd=0, bg=BLANCO, fg=GRIS
        )
        self.buscar_entry.insert(0, "Buscar plato...")
        self.buscar_entry.pack(side="left", fill="x", expand=True, padx=15, pady=14)
        self.buscar_entry.bind("<KeyRelease>", lambda e: self.dibujar_productos())

        tk.Label(
            buscador, text="⌕", font=("Segoe UI", 22), fg=ROJO, bg=BLANCO
        ).pack(side="right", padx=15)

    # ========================================================
    # FILA DE CLIENTE (opcional)
    # ========================================================

    def _crear_fila_cliente(self):

        cliente = tk.Frame(self, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
        cliente.pack(fill="x", pady=(12, 0))

        tk.Label(
            cliente, text="Cliente ", font=("Segoe UI", 11, "bold"),
            fg=TEXTO, bg=BLANCO
        ).pack(side="left", padx=(15, 0), pady=15)

        tk.Label(
            cliente, text="(Opcional)", font=("Segoe UI", 11),
            fg=NARANJA, bg=BLANCO
        ).pack(side="left", pady=15)

        entrada = tk.Entry(cliente, font=("Segoe UI", 11), bd=0, bg="#FFFDF9")
        entrada.insert(0, " 🔍  Teléfono (opcional)")
        entrada.pack(side="left", fill="x", expand=True, padx=20, pady=10)

    # ========================================================
    # REFRESCAR (cuando cambia el periodo del menú)
    # ========================================================

    def refrescar_periodo(self):
        """Se llama cuando cambia de 'desayuno' a 'almuerzo' (o
        viceversa) para volver a dibujar la cabecera y la
        cuadrícula con el catálogo correspondiente."""

        for widget in self.winfo_children():
            widget.destroy()

        self._crear_cabecera()

        self.productos_frame = tk.Frame(self, bg=CREMA)
        self.productos_frame.pack(fill="both", expand=True)

        self.dibujar_productos()

        self._crear_fila_cliente()

    # ========================================================
    # DIBUJAR PRODUCTOS (cuadrícula)
    # ========================================================

    def dibujar_productos(self):

        for widget in self.productos_frame.winfo_children():
            widget.destroy()

        busqueda = self.buscar_entry.get().lower()

        if busqueda == "buscar plato...":
            busqueda = ""

        productos = []

        for producto in catalogo.obtener_productos_del_periodo(self.controlador.periodo_actual):

            if (
                self.controlador.categoria_actual != "todos"
                and producto["categoria"] != self.controlador.categoria_actual
            ):
                continue

            if busqueda and busqueda not in producto["nombre"].lower():
                continue

            productos.append(producto)

        if not productos:

            tk.Label(
                self.productos_frame, text="No se encontraron platillos.",
                font=("Segoe UI", 12), fg=GRIS, bg=CREMA
            ).grid(row=0, column=0, pady=30, padx=10, sticky="w")

            return

        fila = 0
        columna = 0

        for producto in productos:

            tarjeta = tk.Frame(
                self.productos_frame, bg=BLANCO,
                highlightbackground=BORDE, highlightthickness=1, cursor="hand2"
            )

            tarjeta.grid(row=fila, column=columna, padx=7, pady=7, sticky="nsew")
            self.productos_frame.grid_columnconfigure(columna, weight=1)

            tk.Label(
                tarjeta, text=producto["emoji"], font=("Segoe UI Emoji", 42), bg="#FFF4DE"
            ).pack(fill="x", pady=(0, 8), ipady=15)

            tk.Label(
                tarjeta, text=producto["nombre"], font=("Segoe UI", 13, "bold"),
                fg=TEXTO, bg=BLANCO, justify="center"
            ).pack()

            if producto["descripcion"]:
                tk.Label(
                    tarjeta, text=producto["descripcion"], font=("Segoe UI", 8),
                    fg=GRIS, bg=BLANCO, justify="center"
                ).pack(pady=2)

            tk.Label(
                tarjeta, text=f"Q{producto['precio']}", font=("Segoe UI", 15, "bold"),
                fg=ROJO, bg=BLANCO
            ).pack(pady=(3, 12))

            tarjeta.bind("<Button-1>", lambda e, p=producto: self.controlador.agregar_producto(p))

            def entrar(event, t=tarjeta):
                t.configure(highlightbackground=NARANJA, highlightthickness=2)

            def salir(event, t=tarjeta):
                t.configure(highlightbackground=BORDE, highlightthickness=1)

            tarjeta.bind("<Enter>", entrar)
            tarjeta.bind("<Leave>", salir)

            for widget in tarjeta.winfo_children():
                widget.bind("<Button-1>", lambda e, p=producto: self.controlador.agregar_producto(p))
                widget.bind("<Enter>", entrar)
                widget.bind("<Leave>", salir)

            columna += 1

            if columna == 2:
                columna = 0
                fila += 1
