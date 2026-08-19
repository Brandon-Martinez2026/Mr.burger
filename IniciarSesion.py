import tkinter as tk
from tkinter import messagebox
import os
import sys

try:
    from PIL import Image, ImageTk
except ImportError:
    print("Necesitas instalar Pillow: pip install pillow")
    sys.exit(1)

# ------------------------------------------------------------
# Filtro de reescalado de alta calidad, compatible con distintas
# versiones de Pillow (en versiones nuevas vive en
# Image.Resampling.LANCZOS, en versiones viejas en Image.LANCZOS
# o Image.ANTIALIAS).
# ------------------------------------------------------------

try:
    FILTRO_REESCALADO = Image.Resampling.LANCZOS
except AttributeError:
    FILTRO_REESCALADO = getattr(Image, "LANCZOS", None) or getattr(Image, "ANTIALIAS")


# ============================================================
# COLORES
# ============================================================

ROJO = "#A92718"
ROJO_CLARO = "#D93A20"
ROJO_OSCURO = "#7E1D14"

CREMA = "#FBF0DC"
CREMA_CLARO = "#FFF9ED"
BLANCO = "#FFFFFF"

NARANJA = "#E98A20"
NARANJA_CLARO = "#F5A623"

VERDE = "#4CAF50"

TEXTO = "#292929"
GRIS = "#777777"
BORDE = "#E5D8C4"

# ------------------------------------------------------------
# Ruta donde está el logo.
# Se busca dentro de la carpeta "recursos", ubicada en la misma
# carpeta donde está guardado este archivo .py, sin importar en
# qué computadora se ejecute el programa.
# ------------------------------------------------------------

CARPETA_BASE = os.path.dirname(os.path.abspath(__file__))
CARPETA_LOGO = os.path.join(CARPETA_BASE, "recursos")
NOMBRE_LOGO = "01_logo_principal"


# ============================================================
# PRODUCTOS
# ============================================================

PRODUCTOS = [
    {
        "nombre": "Hamburguesa\nClásica",
        "descripcion": "Ensalada,\ntomate, cebolla",
        "precio": 85,
        "categoria": "hamburguesas",
        "emoji": "🍔"
    },
    {
        "nombre": "Pizza\nMargherita",
        "descripcion": "",
        "precio": 120,
        "categoria": "pizza",
        "emoji": "🍕"
    },
    {
        "nombre": "Pasta Boloñesa",
        "descripcion": "",
        "precio": 65,
        "categoria": "pasta",
        "emoji": "🍝"
    },
    {
        "nombre": "Ensalada César",
        "descripcion": "",
        "precio": 60,
        "categoria": "ensaladas",
        "emoji": "🥗"
    },
    {
        "nombre": "Limonada\nNatural",
        "descripcion": "",
        "precio": 25,
        "categoria": "bebidas",
        "emoji": "🍋"
    }
]


# ============================================================
# APLICACIÓN
# ============================================================

class MenuPrincipal(tk.Tk):

    def __init__(self):

        super().__init__()

        self.title("Mr.Burger - Sistema de Punto de Venta")

        self.geometry("1300x750")
        self.minsize(1100, 650)

        self.configure(bg=CREMA)

        # Pantalla completa
        self.attributes("-fullscreen", True)

        self.bind("<F11>", self.alternar_pantalla)
        self.bind("<Escape>", self.salir_pantalla)

        # Carrito
        self.carrito = []

        # Categoría actual
        self.categoria_actual = "todos"

        # Logo (para que no lo borre el garbage collector)
        self.logo_tk = None
        self.logo_path = self._buscar_logo(CARPETA_LOGO, NOMBRE_LOGO)

        # Construir interfaz
        self.crear_interfaz()

    # ========================================================
    # UTILIDADES
    # ========================================================

    def _buscar_logo(self, carpeta, nombre_base):
        """Busca el archivo del logo dentro de 'recursos' probando extensiones comunes."""
        extensiones = [".png", ".jpg", ".jpeg", ".webp", ".bmp"]

        if not os.path.isdir(carpeta):
            print(f"Aviso: no se encontró la carpeta de recursos: {carpeta}")
            return None

        for ext in extensiones:
            ruta = os.path.join(carpeta, nombre_base + ext)
            if os.path.isfile(ruta):
                return ruta

        print(
            f"Aviso: no se encontró '{nombre_base}' con ninguna extensión "
            f"conocida dentro de {carpeta}"
        )
        return None

    # ========================================================
    # PANTALLA
    # ========================================================

    def alternar_pantalla(self, event=None):

        estado = self.attributes("-fullscreen")

        self.attributes("-fullscreen", not estado)

    def salir_pantalla(self, event=None):

        self.attributes("-fullscreen", False)

    # ========================================================
    # INTERFAZ PRINCIPAL
    # ========================================================

    def crear_interfaz(self):

        # Contenedor principal
        self.contenedor = tk.Frame(
            self,
            bg=CREMA
        )

        self.contenedor.pack(
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # SIDEBAR
        # ----------------------------------------------------

        self.crear_sidebar()

        # ----------------------------------------------------
        # CONTENIDO
        # ----------------------------------------------------

        self.contenido = tk.Frame(
            self.contenedor,
            bg=CREMA
        )

        self.contenido.pack(
            side="left",
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # ZONA CENTRAL
        # ----------------------------------------------------

        self.zona_central = tk.Frame(
            self.contenido,
            bg=CREMA
        )

        self.zona_central.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(35, 20),
            pady=25
        )

        # ----------------------------------------------------
        # RESUMEN
        # ----------------------------------------------------

        self.crear_resumen()

        # Mostrar productos
        self.mostrar_productos()

    # ========================================================
    # SIDEBAR
    # ========================================================

    def crear_sidebar(self):

        self.sidebar = tk.Frame(
            self.contenedor,
            bg=ROJO,
            width=270
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        self.sidebar.pack_propagate(False)

        # ----------------------------------------------------
        # LOGO (arriba del todo, centrado)
        # ----------------------------------------------------

        logo = tk.Frame(
            self.sidebar,
            bg=ROJO
        )

        logo.pack(
            pady=(30, 20)
        )

        logo_mostrado = False

        if self.logo_path:
            try:
                img = Image.open(self.logo_path).convert("RGBA")
                img.thumbnail((110, 110), FILTRO_REESCALADO)
                self.logo_tk = ImageTk.PhotoImage(img)

                tk.Label(
                    logo,
                    image=self.logo_tk,
                    bg=ROJO
                ).pack(pady=(0, 8))

                logo_mostrado = True
            except Exception as e:
                print(f"No se pudo cargar el logo: {e}")

        if not logo_mostrado:
            # Ícono de respaldo si no se encontró la imagen
            tk.Label(
                logo,
                text="♨",
                font=("Segoe UI", 38, "bold"),
                fg="#FFA51F",
                bg=ROJO
            ).pack()

        tk.Label(
            logo,
            text="Mr.Burger",
            font=("Segoe UI", 26, "bold"),
            fg="white",
            bg=ROJO
        ).pack()

        tk.Label(
            logo,
            text="DISFRUTA CADA MOMENTO",
            font=("Segoe UI", 9, "bold"),
            fg="#FFB72B",
            bg=ROJO
        ).pack(pady=(2, 0))

        # Línea separadora sutil
        tk.Frame(
            self.sidebar,
            bg=ROJO_OSCURO,
            height=1
        ).pack(fill="x", padx=25, pady=(20, 10))

        # ----------------------------------------------------
        # MENÚ
        # ----------------------------------------------------

        self.crear_boton_menu(
            "⌂",
            "Pedido Nuevo",
            True,
            self.pedido_nuevo
        )

        self.crear_boton_menu(
            "▣",
            "Historial de\nPedidos",
            False,
            self.historial
        )

        self.crear_boton_menu(
            "♙",
            "Clientes",
            False,
            self.clientes
        )

        self.crear_boton_menu(
            "↗",
            "Menú Rápido",
            False,
            self.menu_rapido
        )

        self.crear_boton_menu(
            "⚙",
            "Configuración\nde Caja",
            False,
            self.configuracion
        )

        self.crear_boton_menu(
            "⇥",
            "Cerrar Caja",
            False,
            self.cerrar_caja
        )

        # ----------------------------------------------------
        # USUARIO
        # ----------------------------------------------------

        usuario = tk.Frame(
            self.sidebar,
            bg=ROJO_OSCURO,
            height=80
        )

        usuario.pack(
            side="bottom",
            fill="x"
        )

        usuario.pack_propagate(False)

        avatar = tk.Canvas(
            usuario,
            width=48,
            height=48,
            bg=ROJO_OSCURO,
            highlightthickness=0
        )

        avatar.pack(
            side="left",
            padx=(18, 10),
            pady=15
        )

        avatar.create_oval(
            2,
            2,
            46,
            46,
            fill="white",
            outline=""
        )

        avatar.create_text(
            24,
            24,
            text="C",
            font=("Segoe UI", 18, "bold"),
            fill=ROJO
        )

        datos = tk.Frame(
            usuario,
            bg=ROJO_OSCURO
        )

        datos.pack(
            side="left",
            pady=15
        )

        tk.Label(
            datos,
            text="Carlos",
            font=("Segoe UI", 12, "bold"),
            fg="white",
            bg=ROJO_OSCURO
        ).pack(anchor="w")

        tk.Label(
            datos,
            text="Cajero",
            font=("Segoe UI", 9),
            fg="#F5D8D2",
            bg=ROJO_OSCURO
        ).pack(anchor="w")

        tk.Label(
            usuario,
            text="⌄",
            font=("Segoe UI", 18),
            fg="white",
            bg=ROJO_OSCURO
        ).pack(
            side="right",
            padx=15
        )

    # ========================================================
    # BOTONES DEL SIDEBAR
    # ========================================================

    def crear_boton_menu(
        self,
        icono,
        texto,
        activo,
        comando
    ):

        color = ROJO_CLARO if activo else ROJO

        boton = tk.Frame(
            self.sidebar,
            bg=color,
            cursor="hand2"
        )

        boton.pack(
            fill="x",
            padx=18,
            pady=5
        )

        label = tk.Label(
            boton,
            text=f"{icono}   {texto}",
            font=("Segoe UI", 13, "bold" if activo else "normal"),
            fg="white",
            bg=color,
            anchor="w",
            padx=15,
            pady=12
        )

        label.pack(
            fill="x"
        )

        boton.bind(
            "<Button-1>",
            lambda e: comando()
        )

        label.bind(
            "<Button-1>",
            lambda e: comando()
        )

        def entrar(event):

            if not activo:
                boton.configure(bg=ROJO_OSCURO)
                label.configure(bg=ROJO_OSCURO)

        def salir(event):

            if not activo:
                boton.configure(bg=ROJO)
                label.configure(bg=ROJO)

        boton.bind("<Enter>", entrar)
        boton.bind("<Leave>", salir)

        label.bind("<Enter>", entrar)
        label.bind("<Leave>", salir)

    # ========================================================
    # PARTE CENTRAL
    # ========================================================

    def crear_cabecera(self):

        titulo = tk.Label(
            self.zona_central,
            text="Nuevo Pedido",
            font=("Segoe UI", 28, "bold"),
            fg=TEXTO,
            bg=CREMA
        )

        titulo.pack(
            anchor="w",
            pady=(0, 18)
        )

        # ----------------------------------------------------
        # BUSCADOR
        # ----------------------------------------------------

        buscador = tk.Frame(
            self.zona_central,
            bg=BLANCO,
            highlightbackground=BORDE,
            highlightthickness=1
        )

        buscador.pack(
            fill="x",
            pady=(0, 15)
        )

        self.buscar_entry = tk.Entry(
            buscador,
            font=("Segoe UI", 13),
            bd=0,
            bg=BLANCO,
            fg=GRIS
        )

        self.buscar_entry.insert(
            0,
            "Buscar plato..."
        )

        self.buscar_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=15,
            pady=14
        )

        self.buscar_entry.bind(
            "<KeyRelease>",
            lambda e: self.buscar()
        )

        tk.Label(
            buscador,
            text="⌕",
            font=("Segoe UI", 22),
            fg=ROJO,
            bg=BLANCO
        ).pack(
            side="right",
            padx=15
        )

        # ----------------------------------------------------
        # CATEGORÍAS
        # ----------------------------------------------------

        categorias = tk.Frame(
            self.zona_central,
            bg=CREMA
        )

        categorias.pack(
            fill="x",
            pady=(0, 15)
        )

        botones = [
            ("🍔", "todos"),
            ("🍝", "pasta"),
            ("🍕", "pizza"),
            ("🍴", "ensaladas"),
            ("⚙", "bebidas")
        ]

        self.botones_categoria = {}

        for icono, categoria in botones:

            es_activo = categoria == self.categoria_actual

            boton = tk.Button(
                categorias,
                text=icono,
                font=("Segoe UI", 16),
                bg=NARANJA if es_activo else BLANCO,
                fg="white" if es_activo else NARANJA,
                activebackground="#FFE3B3",
                relief="flat",
                bd=0,
                width=5,
                height=1,
                command=lambda c=categoria:
                self.filtrar_categoria(c)
            )

            boton.pack(
                side="left",
                padx=5
            )

            self.botones_categoria[categoria] = boton

    # ========================================================
    # MOSTRAR PRODUCTOS
    # ========================================================

    def mostrar_productos(self):

        # Limpiar zona central
        for widget in self.zona_central.winfo_children():
            widget.destroy()

        self.crear_cabecera()

        # Contenedor de productos
        self.productos_frame = tk.Frame(
            self.zona_central,
            bg=CREMA
        )

        self.productos_frame.pack(
            fill="both",
            expand=True
        )

        self.dibujar_productos()

        # ----------------------------------------------------
        # CLIENTE
        # ----------------------------------------------------

        cliente = tk.Frame(
            self.zona_central,
            bg=BLANCO,
            highlightbackground=BORDE,
            highlightthickness=1
        )

        cliente.pack(
            fill="x",
            pady=(12, 0)
        )

        tk.Label(
            cliente,
            text="Cliente ",
            font=("Segoe UI", 11, "bold"),
            fg=TEXTO,
            bg=BLANCO
        ).pack(
            side="left",
            padx=(15, 0),
            pady=15
        )

        tk.Label(
            cliente,
            text="(Opcional)",
            font=("Segoe UI", 11),
            fg=NARANJA,
            bg=BLANCO
        ).pack(
            side="left",
            pady=15
        )

        entrada = tk.Entry(
            cliente,
            font=("Segoe UI", 11),
            bd=0,
            bg="#FFFDF9"
        )

        entrada.insert(
            0,
            " 🔍  E-mail/teléfono"
        )

        entrada.pack(
            side="left",
            fill="x",
            expand=True,
            padx=20,
            pady=10
        )

    # ========================================================
    # DIBUJAR PRODUCTOS
    # ========================================================

    def dibujar_productos(self):

        for widget in self.productos_frame.winfo_children():
            widget.destroy()

        busqueda = ""

        if hasattr(self, "buscar_entry"):
            busqueda = self.buscar_entry.get().lower()

            if busqueda == "buscar plato...":
                busqueda = ""

        productos = []

        for producto in PRODUCTOS:

            if (
                self.categoria_actual != "todos"
                and producto["categoria"] != self.categoria_actual
            ):
                continue

            if busqueda:

                nombre = producto["nombre"].lower()

                if busqueda not in nombre:
                    continue

            productos.append(producto)

        if not productos:

            tk.Label(
                self.productos_frame,
                text="No se encontraron platillos.",
                font=("Segoe UI", 12),
                fg=GRIS,
                bg=CREMA
            ).grid(row=0, column=0, pady=30, padx=10, sticky="w")

            return

        # Crear tarjetas
        fila = 0
        columna = 0

        for producto in productos:

            tarjeta = tk.Frame(
                self.productos_frame,
                bg=BLANCO,
                highlightbackground=BORDE,
                highlightthickness=1,
                cursor="hand2"
            )

            tarjeta.grid(
                row=fila,
                column=columna,
                padx=7,
                pady=7,
                sticky="nsew"
            )

            self.productos_frame.grid_columnconfigure(
                columna,
                weight=1
            )

            # Imagen / emoji
            imagen = tk.Label(
                tarjeta,
                text=producto["emoji"],
                font=("Segoe UI Emoji", 42),
                bg="#FFF4DE"
            )

            imagen.pack(
                fill="x",
                pady=(0, 8),
                ipady=15
            )

            # Nombre
            tk.Label(
                tarjeta,
                text=producto["nombre"],
                font=("Segoe UI", 13, "bold"),
                fg=TEXTO,
                bg=BLANCO,
                justify="center"
            ).pack()

            # Descripción
            if producto["descripcion"]:

                tk.Label(
                    tarjeta,
                    text=producto["descripcion"],
                    font=("Segoe UI", 8),
                    fg=GRIS,
                    bg=BLANCO,
                    justify="center"
                ).pack(
                    pady=2
                )

            # Precio
            tk.Label(
                tarjeta,
                text=f"Q{producto['precio']}",
                font=("Segoe UI", 15, "bold"),
                fg=ROJO,
                bg=BLANCO
            ).pack(
                pady=(3, 12)
            )

            # Click
            tarjeta.bind(
                "<Button-1>",
                lambda e, p=producto:
                self.agregar_producto(p)
            )

            # Efecto hover en toda la tarjeta
            def entrar(event, t=tarjeta):
                t.configure(highlightbackground=NARANJA, highlightthickness=2)

            def salir(event, t=tarjeta):
                t.configure(highlightbackground=BORDE, highlightthickness=1)

            tarjeta.bind("<Enter>", entrar)
            tarjeta.bind("<Leave>", salir)

            for widget in tarjeta.winfo_children():

                widget.bind(
                    "<Button-1>",
                    lambda e, p=producto:
                    self.agregar_producto(p)
                )

                widget.bind("<Enter>", entrar)
                widget.bind("<Leave>", salir)

            columna += 1

            if columna == 2:

                columna = 0
                fila += 1

    # ========================================================
    # FILTRAR
    # ========================================================

    def filtrar_categoria(self, categoria):

        self.categoria_actual = categoria

        for cat, boton in self.botones_categoria.items():

            es_activo = cat == categoria

            boton.configure(
                bg=NARANJA if es_activo else BLANCO,
                fg="white" if es_activo else NARANJA
            )

        self.dibujar_productos()

    # ========================================================
    # BUSCAR
    # ========================================================

    def buscar(self):

        self.dibujar_productos()

    # ========================================================
    # AGREGAR PRODUCTO
    # ========================================================

    def agregar_producto(self, producto):

        encontrado = False

        for item in self.carrito:

            if item["nombre"] == producto["nombre"]:

                item["cantidad"] += 1

                encontrado = True

                break

        if not encontrado:

            self.carrito.append(
                {
                    "nombre": producto["nombre"].replace(
                        "\n",
                        " "
                    ),
                    "precio": producto["precio"],
                    "cantidad": 1
                }
            )

        self.actualizar_resumen()

    # ========================================================
    # RESUMEN
    # ========================================================

    def crear_resumen(self):

        self.resumen = tk.Frame(
            self.contenido,
            bg=BLANCO,
            width=430,
            highlightbackground=BORDE,
            highlightthickness=1
        )

        self.resumen.pack(
            side="right",
            fill="y",
            padx=(0, 25),
            pady=25
        )

        self.resumen.pack_propagate(False)

        # ----------------------------------------------------
        # TÍTULO
        # ----------------------------------------------------

        tk.Label(
            self.resumen,
            text="Resumen del Pedido",
            font=("Segoe UI", 22, "bold"),
            fg=TEXTO,
            bg=BLANCO
        ).pack(
            anchor="w",
            padx=25,
            pady=(25, 18)
        )

        # ----------------------------------------------------
        # MESA
        # ----------------------------------------------------

        mesa = tk.Frame(
            self.resumen,
            bg="#FFF0D5"
        )

        mesa.pack(
            fill="x",
            padx=25
        )

        tk.Label(
            mesa,
            text="▰  Mesa 4",
            font=("Segoe UI", 12, "bold"),
            fg=TEXTO,
            bg="#FFF0D5"
        ).pack(
            side="left",
            padx=20,
            pady=12
        )

        tk.Label(
            mesa,
            text="🛍  Para Llevar",
            font=("Segoe UI", 11),
            fg=TEXTO,
            bg="#FFF0D5"
        ).pack(
            side="right",
            padx=15
        )

        # ----------------------------------------------------
        # PRODUCTOS DEL CARRITO
        # ----------------------------------------------------

        self.lista_carrito = tk.Frame(
            self.resumen,
            bg=BLANCO
        )

        self.lista_carrito.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=15
        )

        self.lbl_carrito_vacio = tk.Label(
            self.lista_carrito,
            text="Aún no has agregado productos.",
            font=("Segoe UI", 10),
            fg=GRIS,
            bg=BLANCO
        )

        self.lbl_carrito_vacio.pack(pady=10)

        # ----------------------------------------------------
        # TOTAL
        # ----------------------------------------------------

        self.total_frame = tk.Frame(
            self.resumen,
            bg=BLANCO
        )

        self.total_frame.pack(
            fill="x",
            padx=25
        )

        self.lbl_total = tk.Label(
            self.total_frame,
            text="Total:                    Q0.00",
            font=("Segoe UI", 15, "bold"),
            fg=TEXTO,
            bg=BLANCO
        )

        self.lbl_total.pack(
            pady=12
        )

        # ----------------------------------------------------
        # MODIFICADORES
        # ----------------------------------------------------

        tk.Button(
            self.resumen,
            text="Modificadores                         ⌄",
            font=("Segoe UI", 11),
            bg=BLANCO,
            fg=GRIS,
            relief="flat",
            anchor="w",
            bd=1
        ).pack(
            fill="x",
            padx=25,
            pady=5
        )

        # ----------------------------------------------------
        # NOTAS
        # ----------------------------------------------------

        notas = tk.Text(
            self.resumen,
            height=3,
            font=("Segoe UI", 10),
            fg=GRIS,
            bd=1,
            relief="solid"
        )

        notas.insert(
            "1.0",
            "Notas"
        )

        notas.pack(
            fill="x",
            padx=25,
            pady=5
        )

        # ----------------------------------------------------
        # BOTONES
        # ----------------------------------------------------

        botones = tk.Frame(
            self.resumen,
            bg=BLANCO
        )

        botones.pack(
            fill="x",
            padx=25,
            pady=8
        )

        tk.Button(
            botones,
            text="⚖\nDividir Cuenta",
            font=("Segoe UI", 10),
            bg=BLANCO,
            relief="solid",
            bd=1
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 5),
            ipady=8
        )

        tk.Button(
            botones,
            text="%\nAplicar Descuento",
            font=("Segoe UI", 10),
            bg=BLANCO,
            relief="solid",
            bd=1
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(5, 0),
            ipady=8
        )

        # ----------------------------------------------------
        # TECLADO
        # ----------------------------------------------------

        teclado = tk.Frame(
            self.resumen,
            bg=BLANCO
        )

        teclado.pack(
            fill="x",
            padx=25,
            pady=5
        )

        numeros = [
            "1", "2", "3", "⌫",
            "4", "5", "6", "−",
            "7", "8", "9", "+"
        ]

        for i, numero in enumerate(numeros):

            fila = i // 4
            columna = i % 4

            color = (
                NARANJA
                if numero in ["⌫", "+"]
                else BLANCO
            )

            boton = tk.Button(
                teclado,
                text=numero,
                font=("Segoe UI", 14, "bold"),
                bg=color,
                fg="white" if color == NARANJA else TEXTO,
                relief="solid",
                bd=1,
                command=lambda n=numero:
                self.tecla(n)
            )

            boton.grid(
                row=fila,
                column=columna,
                padx=3,
                pady=3,
                sticky="nsew"
            )

        for i in range(4):
            teclado.grid_columnconfigure(
                i,
                weight=1
            )

        # ----------------------------------------------------
        # PAGAR
        # ----------------------------------------------------

        self.btn_pagar = tk.Button(
            self.resumen,
            text="Pagar: Q0.00",
            font=("Segoe UI", 14, "bold"),
            bg=ROJO_CLARO,
            fg="white",
            activebackground=ROJO,
            activeforeground="white",
            relief="flat",
            command=self.pagar
        )

        self.btn_pagar.pack(
            fill="x",
            padx=25,
            pady=10,
            ipady=8
        )

        # ----------------------------------------------------
        # GUARDAR / CANCELAR
        # ----------------------------------------------------

        abajo = tk.Frame(
            self.resumen,
            bg=BLANCO
        )

        abajo.pack(
            fill="x",
            padx=25,
            pady=(0, 20)
        )

        tk.Button(
            abajo,
            text="Guardar Pedido",
            font=("Segoe UI", 10),
            bg=BLANCO,
            relief="solid",
            bd=1
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 5),
            ipady=7
        )

        tk.Button(
            abajo,
            text="Cancelar",
            font=("Segoe UI", 10),
            bg=BLANCO,
            relief="solid",
            bd=1,
            command=self.cancelar
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(5, 0),
            ipady=7
        )

    # ========================================================
    # ACTUALIZAR RESUMEN
    # ========================================================

    def actualizar_resumen(self):

        for widget in self.lista_carrito.winfo_children():
            widget.destroy()

        if not self.carrito:

            tk.Label(
                self.lista_carrito,
                text="Aún no has agregado productos.",
                font=("Segoe UI", 10),
                fg=GRIS,
                bg=BLANCO
            ).pack(pady=10)

        total = 0

        for item in self.carrito:

            subtotal = item["precio"] * item["cantidad"]

            total += subtotal

            fila = tk.Frame(
                self.lista_carrito,
                bg=BLANCO
            )

            fila.pack(
                fill="x",
                pady=8
            )

            tk.Label(
                fila,
                text=f"{item['cantidad']}x",
                font=("Segoe UI", 11, "bold"),
                fg=ROJO,
                bg=BLANCO
            ).pack(
                side="left"
            )

            tk.Label(
                fila,
                text=item["nombre"],
                font=("Segoe UI", 11),
                fg=TEXTO,
                bg=BLANCO
            ).pack(
                side="left",
                padx=12
            )

            tk.Label(
                fila,
                text=f"Q{subtotal:.2f}",
                font=("Segoe UI", 11, "bold"),
                fg=TEXTO,
                bg=BLANCO
            ).pack(
                side="right"
            )

        self.lbl_total.configure(
            text=f"Total:                    Q{total:.2f}"
        )

        self.btn_pagar.configure(
            text=f"Pagar: Q{total:.2f}"
        )

    # ========================================================
    # TECLADO
    # ========================================================

    def tecla(self, numero):

        print("Tecla:", numero)

    # ========================================================
    # PAGAR
    # ========================================================

    def pagar(self):

        if not self.carrito:

            messagebox.showwarning(
                "Mr.Burger",
                "No hay productos en el pedido."
            )

            return

        total = sum(
            item["precio"] * item["cantidad"]
            for item in self.carrito
        )

        messagebox.showinfo(
            "Pago realizado",
            f"Venta registrada correctamente.\n\n"
            f"Total: Q{total:.2f}"
        )

        self.carrito.clear()

        self.actualizar_resumen()

    # ========================================================
    # CANCELAR
    # ========================================================

    def cancelar(self):

        if not self.carrito:
            return

        confirmar = messagebox.askyesno(
            "Cancelar pedido",
            "¿Deseas cancelar el pedido?"
        )

        if confirmar:

            self.carrito.clear()

            self.actualizar_resumen()

    # ========================================================
    # OPCIONES DEL MENÚ
    # ========================================================

    def pedido_nuevo(self):

        pass

    def historial(self):

        messagebox.showinfo(
            "Historial",
            "Módulo de historial de pedidos."
        )

    def clientes(self):

        messagebox.showinfo(
            "Clientes",
            "Módulo de clientes."
        )

    def menu_rapido(self):

        messagebox.showinfo(
            "Menú rápido",
            "Módulo de menú rápido."
        )

    def configuracion(self):

        messagebox.showinfo(
            "Configuración",
            "Configuración de caja."
        )

    def cerrar_caja(self):

        respuesta = messagebox.askyesno(
            "Cerrar caja",
            "¿Deseas cerrar la caja?"
        )

        if respuesta:

            messagebox.showinfo(
                "Caja",
                "Caja cerrada correctamente."
            )

            self.destroy()


# ============================================================
# EJECUTAR
# ============================================================

if __name__ == "__main__":

    app = MenuPrincipal()

    app.mainloop()