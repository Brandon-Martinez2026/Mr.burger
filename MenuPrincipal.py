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
# versiones de Pillow.
# ------------------------------------------------------------
try:
    FILTRO_REESCALADO = Image.Resampling.LANCZOS
except AttributeError:
    FILTRO_REESCALADO = getattr(Image, "LANCZOS", None) or getattr(Image, "ANTIALIAS")


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
# RUTA DEL LOGO GENERAL
# ============================================================
# Se mantiene separado del logo del Sidebar.
# ============================================================

CARPETA_BASE = os.path.dirname(os.path.abspath(__file__))


def _resolver_carpeta_recursos(base):
    """Devuelve la carpeta 'Recursos' del proyecto sin importar si
    está escrita en mayúsculas o minúsculas (compatibilidad entre
    sistemas operativos)."""

    for nombre in ("Recursos", "recursos"):
        ruta = os.path.join(base, nombre)
        if os.path.isdir(ruta):
            return ruta

    return os.path.join(base, "Recursos")


def _resolver_carpeta_decoraciones(base):
    """Devuelve la carpeta 'Decoraciones' del proyecto sin importar
    si está escrita en mayúsculas o minúsculas."""

    for nombre in ("Decoraciones", "decoraciones"):
        ruta = os.path.join(base, nombre)
        if os.path.isdir(ruta):
            return ruta

    return os.path.join(base, "Decoraciones")


CARPETA_LOGO = _resolver_carpeta_recursos(CARPETA_BASE)
CARPETA_DECORACIONES = _resolver_carpeta_decoraciones(CARPETA_BASE)
NOMBRE_LOGO = "Logotipo"


# ============================================================
# HORARIOS DEL MENÚ
# ============================================================
# De 7:00 a 10:59 se muestra únicamente el menú de desayunos.
# Del resto del día (11:00 a 6:59, es decir tarde, noche y
# madrugada) se muestra únicamente el menú de almuerzo.
# ============================================================

HORA_INICIO_DESAYUNO = 7
HORA_FIN_DESAYUNO = 11


def obtener_periodo_actual():
    """Devuelve 'desayuno' o 'almuerzo' según la hora del sistema."""

    import datetime

    hora = datetime.datetime.now().hour

    if HORA_INICIO_DESAYUNO <= hora < HORA_FIN_DESAYUNO:
        return "desayuno"

    return "almuerzo"


# ============================================================
# PRODUCTOS - MENÚ DE DESAYUNO (7:00 - 10:59)
# ============================================================

PRODUCTOS_DESAYUNO = [
    {
        "nombre": "Desayuno\nClásico",
        "descripcion": "Huevos, tocino,\npan tostado",
        "precio": 45,
        "categoria": "comida",
        "emoji": "🍳"
    },
    {
        "nombre": "Pancakes",
        "descripcion": "Con miel y\nmantequilla",
        "precio": 35,
        "categoria": "comida",
        "emoji": "🥞"
    },
    {
        "nombre": "Sandwich\nde Huevo",
        "descripcion": "Pan artesanal",
        "precio": 30,
        "categoria": "comida",
        "emoji": "🥪"
    },
    {
        "nombre": "Café\nAmericano",
        "descripcion": "",
        "precio": 15,
        "categoria": "bebidas",
        "emoji": "☕"
    },
    {
        "nombre": "Jugo de\nNaranja",
        "descripcion": "Natural",
        "precio": 18,
        "categoria": "bebidas",
        "emoji": "🧃"
    },
    {
        "nombre": "Chocolate\nCaliente",
        "descripcion": "",
        "precio": 20,
        "categoria": "bebidas",
        "emoji": "🍫"
    },
    {
        "nombre": "Muffin de\nArándanos",
        "descripcion": "",
        "precio": 20,
        "categoria": "postres",
        "emoji": "🧁"
    },
    {
        "nombre": "Fruta\nPicada",
        "descripcion": "De temporada",
        "precio": 18,
        "categoria": "postres",
        "emoji": "🍓"
    },
    {
        "nombre": "Combo\nDesayuno",
        "descripcion": "Desayuno +\ncafé + jugo",
        "precio": 70,
        "categoria": "combos",
        "emoji": "🍽"
    },
]


# ============================================================
# PRODUCTOS - MENÚ DE ALMUERZO (11:00 - 6:59)
# ============================================================

PRODUCTOS_ALMUERZO = [
    {
        "nombre": "Hamburguesa\nClásica",
        "descripcion": "Lechuga,\ntomate, cebolla",
        "precio": 85,
        "categoria": "comida",
        "emoji": "🍔"
    },
    {
        "nombre": "Hamburguesa\nDoble",
        "descripcion": "Doble carne,\ndoble queso",
        "precio": 105,
        "categoria": "comida",
        "emoji": "🍔"
    },
    {
        "nombre": "Papas\nFritas",
        "descripcion": "",
        "precio": 25,
        "categoria": "comida",
        "emoji": "🍟"
    },
    {
        "nombre": "Alitas\nBBQ",
        "descripcion": "8 unidades",
        "precio": 55,
        "categoria": "comida",
        "emoji": "🍗"
    },
    {
        "nombre": "Limonada\nNatural",
        "descripcion": "",
        "precio": 25,
        "categoria": "bebidas",
        "emoji": "🍋"
    },
    {
        "nombre": "Gaseosa",
        "descripcion": "",
        "precio": 15,
        "categoria": "bebidas",
        "emoji": "🥤"
    },
    {
        "nombre": "Malteada",
        "descripcion": "Vainilla o\nchocolate",
        "precio": 28,
        "categoria": "bebidas",
        "emoji": "🥛"
    },
    {
        "nombre": "Helado",
        "descripcion": "",
        "precio": 22,
        "categoria": "postres",
        "emoji": "🍨"
    },
    {
        "nombre": "Brownie",
        "descripcion": "Con nuez",
        "precio": 24,
        "categoria": "postres",
        "emoji": "🍰"
    },
    {
        "nombre": "Combo\nMr.Burger",
        "descripcion": "Burger + papas\n+ bebida",
        "precio": 120,
        "categoria": "combos",
        "emoji": "🍔"
    },
    {
        "nombre": "Combo\nDoble",
        "descripcion": "2 burgers +\n2 papas + 2 bebidas",
        "precio": 210,
        "categoria": "combos",
        "emoji": "🍽"
    },
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

        # Categoría actual (comida, bebidas, postres o combos)
        self.categoria_actual = "comida"

        # Periodo actual del menú: "desayuno" o "almuerzo",
        # según la hora del sistema.
        self.periodo_actual = obtener_periodo_actual()

        # Logo (para que no lo borre el garbage collector)
        self.logo_tk = None
        self.logo_path = self._buscar_logo(CARPETA_LOGO, NOMBRE_LOGO)

        # Construir interfaz
        self.crear_interfaz()

        # Revisa cada minuto si cambió el periodo del menú
        # (por ejemplo, de desayuno a almuerzo) para actualizar
        # los productos mostrados automáticamente.
        self.after(60000, self._revisar_cambio_periodo)

    # ========================================================
    # PERIODO DEL MENÚ (DESAYUNO / ALMUERZO)
    # ========================================================

    def _revisar_cambio_periodo(self):

        nuevo_periodo = obtener_periodo_actual()

        if nuevo_periodo != self.periodo_actual:

            self.periodo_actual = nuevo_periodo

            self.mostrar_productos()

        self.after(60000, self._revisar_cambio_periodo)

    def _productos_del_periodo(self):

        if self.periodo_actual == "desayuno":
            return PRODUCTOS_DESAYUNO

        return PRODUCTOS_ALMUERZO

    # ========================================================
    # UTILIDADES
    # ========================================================

    def _buscar_logo(self, carpeta, nombre_base):
        """Busca el archivo del logo probando extensiones comunes."""
        extensiones = [".png", ".jpg", ".jpeg", ".webp", ".bmp"]
        for ext in extensiones:
            ruta = os.path.join(carpeta, nombre_base + ext)
            if os.path.isfile(ruta):
                return ruta
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

        # ====================================================
        # LOGO EXCLUSIVO DEL SIDEBAR
        # ====================================================

        logo = tk.Frame(
            self.sidebar,
            bg=ROJO
        )

        logo.pack(
            pady=(30, 20)
        )

        logo_mostrado = False

        # ----------------------------------------------------
        # Buscar únicamente Logo_fondoBlanco
        # ----------------------------------------------------

        carpeta_logo_sidebar = CARPETA_LOGO

        logo_sidebar_path = self._buscar_logo(
            carpeta_logo_sidebar,
            "Logo_fondoBlanco"
        )

        # ----------------------------------------------------
        # Cargar Logo_fondoBlanco
        # ----------------------------------------------------

        if logo_sidebar_path:

            try:

                img = Image.open(
                    logo_sidebar_path
                ).convert("RGBA")

                img.thumbnail(
                    (110, 110),
                    FILTRO_REESCALADO
                )

                # Mantener referencia para evitar
                # que Python elimine la imagen.
                self.logo_sidebar_tk = ImageTk.PhotoImage(
                    img
                )

                tk.Label(
                    logo,
                    image=self.logo_sidebar_tk,
                    bg=ROJO
                ).pack(
                    pady=(0, 8)
                )

                logo_mostrado = True

            except Exception as e:

                print(
                    f"No se pudo cargar el logo del Sidebar: {e}"
                )

        # ----------------------------------------------------
        # Logo de respaldo
        # ----------------------------------------------------

        if not logo_mostrado:

            tk.Label(
                logo,
                text="♨",
                font=("Segoe UI", 38, "bold"),
                fg="#FFA51F",
                bg=ROJO
            ).pack()

        # ----------------------------------------------------
        # Nombre
        # ----------------------------------------------------

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
        ).pack(
            pady=(2, 0)
        )

        # ====================================================
        # LÍNEA SEPARADORA
        # ====================================================

        tk.Frame(
            self.sidebar,
            bg=ROJO_OSCURO,
            height=1
        ).pack(
            fill="x",
            padx=25,
            pady=(20, 10)
        )

        # ====================================================
        # MENÚ
        # ====================================================

        # ====================================================
        # MENÚ (Dashboard del cajero)
        # ====================================================
        # Solo se dejan las opciones de categorías de productos
        # más "Cerrar Caja", tal como lo pidió el profesor.
        # ====================================================

        self.botones_sidebar = {}

        self.crear_boton_menu(
            "🍔",
            "Comida",
            "comida",
            lambda: self.filtrar_categoria("comida")
        )

        self.crear_boton_menu(
            "🥤",
            "Bebidas",
            "bebidas",
            lambda: self.filtrar_categoria("bebidas")
        )

        self.crear_boton_menu(
            "🍰",
            "Postres",
            "postres",
            lambda: self.filtrar_categoria("postres")
        )

        self.crear_boton_menu(
            "🍟",
            "Combos",
            "combos",
            lambda: self.filtrar_categoria("combos")
        )

        self.crear_boton_menu(
            "⇥",
            "Cerrar Caja",
            None,
            self.cerrar_caja
        )

        # ====================================================
        # USUARIO
        # ====================================================

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

        # ----------------------------------------------------
        # Avatar
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # Datos del usuario
        # ----------------------------------------------------

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
        ).pack(
            anchor="w"
        )

        tk.Label(
            datos,
            text="Cajero",
            font=("Segoe UI", 9),
            fg="#F5D8D2",
            bg=ROJO_OSCURO
        ).pack(
            anchor="w"
        )

        # ----------------------------------------------------
        # Flecha
        # ----------------------------------------------------

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
        categoria,
        comando
    ):

        activo = (
            categoria is not None
            and categoria == self.categoria_actual
        )

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

            es_activo = (
                categoria is not None
                and categoria == self.categoria_actual
            )

            if not es_activo:
                boton.configure(bg=ROJO_OSCURO)
                label.configure(bg=ROJO_OSCURO)

        def salir(event):

            es_activo = (
                categoria is not None
                and categoria == self.categoria_actual
            )

            color_normal = ROJO_CLARO if es_activo else ROJO

            boton.configure(bg=color_normal)
            label.configure(bg=color_normal)

        boton.bind("<Enter>", entrar)
        boton.bind("<Leave>", salir)

        label.bind("<Enter>", entrar)
        label.bind("<Leave>", salir)

        # Se guarda la referencia para poder resaltar el botón
        # activo cuando el cajero cambie de categoría.
        if categoria is not None:

            self.botones_sidebar[categoria] = (
                boton,
                label,
                icono,
                texto
            )

    # ========================================================
    # PARTE CENTRAL
    # ========================================================

    def crear_cabecera(self):

        titulo_texto = (
            "Menú de Desayuno"
            if self.periodo_actual == "desayuno"
            else "Menú de Almuerzo"
        )

        encabezado = tk.Frame(
            self.zona_central,
            bg=CREMA
        )

        encabezado.pack(
            fill="x",
            pady=(0, 18)
        )

        titulo = tk.Label(
            encabezado,
            text=titulo_texto,
            font=("Segoe UI", 28, "bold"),
            fg=TEXTO,
            bg=CREMA
        )

        titulo.pack(
            side="left"
        )

        horario_texto = (
            "🕐  Disponible de 7:00 a 11:00"
            if self.periodo_actual == "desayuno"
            else "🕐  Disponible de 11:00 a 2:00"
        )

        tk.Label(
            encabezado,
            text=horario_texto,
            font=("Segoe UI", 10),
            fg=GRIS,
            bg=CREMA
        ).pack(
            side="left",
            padx=(15, 0),
            pady=(10, 0)
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

        for producto in self._productos_del_periodo():

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

        for cat, (boton, label, icono, texto) in self.botones_sidebar.items():

            es_activo = cat == categoria

            color = ROJO_CLARO if es_activo else ROJO

            boton.configure(bg=color)

            label.configure(
                bg=color,
                font=("Segoe UI", 13, "bold" if es_activo else "normal")
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
        # PAGAR
        # ----------------------------------------------------
        # (Se eliminó la calculadora/teclado numérico: al ser
        # un sistema automatizado, el total se calcula solo.)
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
    # CERRAR CAJA
    # ========================================================

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

