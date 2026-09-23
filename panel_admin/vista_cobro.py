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
categorías), aquí las categorías se eligen en un menú en cascada
(un menú que "cae") arriba de la cuadrícula de productos: el
administrador ya tiene su propio sidebar de navegación entre
secciones, así que un segundo sidebar fijo se sentiría
redundante. La lista se lee de la base de datos cada vez que se
abre el menú, así que una categoría recién creada aparece sin
reiniciar. El administrador puede ver todas las categorías y todos los
productos, sin importar el horario actual. El cajero conserva su
lógica normal de horarios porque esta vista solo afecta al panel
de administrador.
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

        self.periodo_actual = "todos"

        # Mismas categorías que ve el cajero para este periodo
        # (las que sí tienen productos disponibles ahora mismo).
        # "todos" siempre se ofrece además, para ver el catálogo
        # completo del periodo de un vistazo.
        self.categorias = catalogo.listar_categorias()
        self.categoria_actual = "todos"

        self.cajero_actual = getattr(self.admin, "nombre_admin", None) or "Administrador"
        self.id_usuario = getattr(self.admin, "id_usuario", None)

        self._crear_interfaz()


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
    # MENÚ EN CASCADA DE CATEGORÍAS
    # ========================================================
    # Un botón que, al hacer clic, "deja caer" la lista de
    # categorías; al elegir una, se filtran los productos y el
    # botón muestra la categoría activa.
    # ========================================================

    def _crear_barra_categorias(self):

        barra = tk.Frame(
            self, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1
        )
        barra.pack(fill="x", pady=(0, 12))

        tk.Label(
            barra, text="🏷  Categoría", font=("Segoe UI", 11, "bold"),
            fg=TEXTO, bg=BLANCO
        ).pack(side="left", padx=(15, 12), pady=10)

        self.btn_menu_categorias = tk.Menubutton(
            barra, font=("Segoe UI", 11, "bold"),
            fg="white", bg=ROJO_CLARO,
            activebackground=ROJO, activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            anchor="w", padx=14, pady=8, width=30,
            direction="below"
        )
        self.btn_menu_categorias.pack(side="left", pady=8)

        # postcommand: justo antes de abrirse, se vuelve a llenar
        # el menú con las categorías actuales de la base de datos.
        self.menu_categorias = tk.Menu(
            self.btn_menu_categorias, tearoff=0,
            font=("Segoe UI", 11), bg=BLANCO, fg=TEXTO,
            activebackground=ROJO_CLARO, activeforeground="white",
            postcommand=self._llenar_menu_categorias
        )
        self.btn_menu_categorias.configure(menu=self.menu_categorias)

        self._llenar_menu_categorias()
        self._actualizar_texto_boton()

    def _llenar_menu_categorias(self):
        """(Re)construye las opciones del menú: \"Todos\" y luego
        cada categoría, marcando con una palomita la activa."""

        self.categorias = catalogo.listar_categorias()

        self.menu_categorias.delete(0, "end")

        opciones = [("todos", "Todos", "📋")] + [
            (categoria, categoria, catalogo.icono_de_categoria(categoria))
            for categoria in self.categorias
        ]

        for valor, texto, icono in opciones:

            marca = "   ✔" if valor == self.categoria_actual else ""

            self.menu_categorias.add_command(
                label=f"{icono}  {texto}{marca}",
                command=lambda v=valor: self._filtrar_categoria(v)
            )

    def _actualizar_texto_boton(self):

        if self.categoria_actual == "todos":
            texto = "📋  Todos  ▾"
        else:
            icono = catalogo.icono_de_categoria(self.categoria_actual)
            texto = f"{icono}  {self.categoria_actual}  ▾"

        self.btn_menu_categorias.configure(text=texto)

    def _filtrar_categoria(self, categoria):

        self.categoria_actual = categoria

        self._actualizar_texto_boton()
        self.vista_productos.dibujar_productos()

    # ========================================================
    # AGREGAR PRODUCTO AL CARRITO
    # ========================================================
    # Punto de unión entre VistaProductos (donde se hace clic en
    # un producto) y PanelCarrito (donde vive el carrito) — igual
    # que en punto_venta/app.py.
    # ========================================================

    def agregar_producto(self, producto):

        self.panel_carrito.agregar_producto(producto)
