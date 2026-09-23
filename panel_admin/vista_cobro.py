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

A diferencia del cajero (que tiene un sidebar fijo de
categorías), aquí las categorías viven en un mini dashboard
desplegable arriba de la cuadrícula de productos: el
administrador ya tiene su propio sidebar de navegación entre
secciones, así que un segundo sidebar fijo se sentiría
redundante. Las categorías que se muestran son exactamente las
mismas y con la misma lógica que usa el cajero
(catalogo.categorias_disponibles): solo las que sí tienen
productos disponibles en el periodo actual.
------------------------------------------------------------
"""

import tkinter as tk

from estilos import ROJO, ROJO_CLARO, CREMA, BORDE, BLANCO, TEXTO
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

        # Mismas categorías que ve el cajero para este periodo
        # (las que sí tienen productos disponibles ahora mismo).
        # "todos" siempre se ofrece además, para ver el catálogo
        # completo del periodo de un vistazo.
        self.categorias = catalogo.categorias_disponibles(self.periodo_actual)
        self.categoria_actual = "todos"

        self.cajero_actual = getattr(self.admin, "nombre_admin", None) or "Administrador"
        self.id_usuario = getattr(self.admin, "id_usuario", None)

        self._categorias_desplegadas = False

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

        self._crear_barra_categorias()

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
    # MINI DASHBOARD DESPLEGABLE DE CATEGORÍAS
    # ========================================================

    def _crear_barra_categorias(self):

        barra = tk.Frame(
            self, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1
        )
        barra.pack(fill="x", pady=(0, 12))

        self.btn_desplegar_categorias = tk.Button(
            barra, text="🏷  Categorías  ▾", font=("Segoe UI", 11, "bold"),
            fg=TEXTO, bg=BLANCO, relief="flat", bd=0, cursor="hand2",
            anchor="w", command=self._alternar_categorias
        )
        self.btn_desplegar_categorias.pack(fill="x", padx=15, pady=10)

        # Panel con los botones de categoría. Empieza colapsado
        # (no se hace pack todavía) para no ocupar espacio extra
        # hasta que el administrador lo abra.
        self.categorias_panel = tk.Frame(self, bg=CREMA)

        self._dibujar_botones_categorias()

    def _alternar_categorias(self):

        self._categorias_desplegadas = not self._categorias_desplegadas

        if self._categorias_desplegadas:
            self.categorias_panel.pack(fill="x", pady=(0, 12))
            self.btn_desplegar_categorias.configure(text="🏷  Categorías  ▴")
        else:
            self.categorias_panel.pack_forget()
            self.btn_desplegar_categorias.configure(text="🏷  Categorías  ▾")

    def _dibujar_botones_categorias(self):
        """(Re)dibuja los botones del mini dashboard según
        self.categorias, resaltando en rojo la categoría activa.
        Se llama al abrir la vista, al elegir una categoría (para
        actualizar cuál queda resaltada) y cada vez que cambia el
        periodo (desayuno/almuerzo)."""

        for widget in self.categorias_panel.winfo_children():
            widget.destroy()

        opciones = [("todos", "Todos", "📋")] + [
            (categoria, categoria, catalogo.icono_de_categoria(categoria))
            for categoria in self.categorias
        ]

        columnas = 3

        for indice, (valor, texto, icono) in enumerate(opciones):

            activo = valor == self.categoria_actual

            boton = tk.Button(
                self.categorias_panel, text=f"{icono}  {texto}",
                font=("Segoe UI", 10, "bold" if activo else "normal"),
                bg=ROJO_CLARO if activo else CREMA,
                fg="white" if activo else TEXTO,
                relief="flat", bd=0, cursor="hand2",
                wraplength=160, justify="left", anchor="w",
                padx=10, pady=10,
                activebackground=ROJO, activeforeground="white",
                command=lambda v=valor: self._filtrar_categoria(v)
            )
            boton.grid(
                row=indice // columnas, column=indice % columnas,
                padx=4, pady=4, sticky="ew"
            )
            self.categorias_panel.grid_columnconfigure(indice % columnas, weight=1)

    def _filtrar_categoria(self, categoria):

        self.categoria_actual = categoria

        self._dibujar_botones_categorias()
        self.vista_productos.dibujar_productos()

    # ========================================================
    # PERIODO DEL MENÚ (DESAYUNO / ALMUERZO)
    # ========================================================

    def _revisar_cambio_periodo(self):

        nuevo_periodo = catalogo.obtener_periodo_actual()

        if nuevo_periodo != self.periodo_actual:

            self.periodo_actual = nuevo_periodo
            self.categorias = catalogo.categorias_disponibles(nuevo_periodo)

            if self.categoria_actual not in self.categorias and self.categoria_actual != "todos":
                self.categoria_actual = "todos"

            self._dibujar_botones_categorias()
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
