"""
vista_productos.py
------------------------------------------------------------
Zona central del Punto de Venta: encabezado con el periodo del
menú, buscador y la cuadrícula de productos en los que el
cajero da clic para agregarlos al carrito.
------------------------------------------------------------
"""

import os
import tkinter as tk

try:
    from PIL import Image, ImageTk
    _PIL_DISPONIBLE = True
except ImportError:
    _PIL_DISPONIBLE = False

from estilos import CREMA, BLANCO, TEXTO, GRIS, ROJO, NARANJA, BORDE
from punto_venta import catalogo
import imagenes_productos

# Tamaño de la foto dentro de la tarjeta de producto.
_ANCHO_FOTO = 160
_ALTO_FOTO = 100


class VistaProductos(tk.Frame):
    """Frame que se coloca en la zona central de la ventana
    principal del Punto de Venta. 'controlador' es la instancia
    de MenuPrincipal (punto_venta/app.py), de la cual se leen
    la categoría/periodo actuales y a la que se avisa cuando se
    agrega un producto al carrito."""

    def __init__(self, parent, controlador):

        super().__init__(parent, bg=CREMA)

        self.controlador = controlador

        # Tkinter no mantiene una referencia propia a los PhotoImage:
        # si no los guardamos en algún lado, el recolector de basura de
        # Python los borra y las tarjetas se quedan en blanco. Esta
        # caché vive mientras viva la vista y se reutiliza entre
        # refrescos (misma ruta -> mismo PhotoImage).
        self._fotos_cache = {}

        self._crear_cabecera()

        self._crear_area_scroll()

        self.dibujar_productos()

        self._crear_fila_cliente()

    # ========================================================
    # ÁREA CON SCROLL (cuadrícula de productos)
    # ========================================================
    # Con categorías largas (el menú nuevo llega a tener hasta 8
    # productos en una sola categoría) la cuadrícula ya no cabe
    # siempre en la pantalla, así que va dentro de un Canvas con
    # una barra de scroll vertical y soporte para la rueda del
    # mouse.
    # ========================================================

    def _crear_area_scroll(self):

        contenedor = tk.Frame(self, bg=CREMA)
        contenedor.pack(fill="both", expand=True)

        self.canvas_productos = tk.Canvas(contenedor, bg=CREMA, highlightthickness=0)
        self.canvas_productos.pack(side="left", fill="both", expand=True)

        barra_scroll = tk.Scrollbar(
            contenedor, orient="vertical", command=self.canvas_productos.yview
        )
        barra_scroll.pack(side="right", fill="y")

        self.canvas_productos.configure(yscrollcommand=barra_scroll.set)

        self.productos_frame = tk.Frame(self.canvas_productos, bg=CREMA)

        self._ventana_productos = self.canvas_productos.create_window(
            (0, 0), window=self.productos_frame, anchor="nw"
        )

        self.productos_frame.bind("<Configure>", self._actualizar_scrollregion)
        self.canvas_productos.bind("<Configure>", self._ajustar_ancho_productos)

        # La rueda del mouse solo mueve este canvas mientras el
        # cursor está encima (se activa/desactiva con Enter/Leave)
        # para no dejar un bind_all "pegado" si esta vista se
        # destruye y se vuelve a crear (por ejemplo, al cambiar de
        # sección en el Panel de Administrador).
        self.canvas_productos.bind("<Enter>", self._activar_scroll_mouse)
        self.canvas_productos.bind("<Leave>", self._desactivar_scroll_mouse)

    def _actualizar_scrollregion(self, event=None):
        self.canvas_productos.configure(scrollregion=self.canvas_productos.bbox("all"))

    def _ajustar_ancho_productos(self, event):
        self.canvas_productos.itemconfigure(self._ventana_productos, width=event.width)

    def _activar_scroll_mouse(self, event=None):
        self.canvas_productos.bind_all("<MouseWheel>", self._al_rodar_mouse)
        self.canvas_productos.bind_all("<Button-4>", self._al_rodar_mouse)
        self.canvas_productos.bind_all("<Button-5>", self._al_rodar_mouse)

    def _desactivar_scroll_mouse(self, event=None):
        self.canvas_productos.unbind_all("<MouseWheel>")
        self.canvas_productos.unbind_all("<Button-4>")
        self.canvas_productos.unbind_all("<Button-5>")

    def _al_rodar_mouse(self, event):

        if event.num == 4:
            self.canvas_productos.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas_productos.yview_scroll(1, "units")
        else:
            self.canvas_productos.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _crear_cabecera(self):

        periodo = self.controlador.periodo_actual

        if periodo == "desayuno":
            titulo_texto = "Menú de Desayuno"
        elif periodo == "todos":
            titulo_texto = "Todos los productos"
        else:
            titulo_texto = "Menú de Almuerzo"

        encabezado = tk.Frame(self, bg=CREMA)
        encabezado.pack(fill="x", pady=(0, 18))

        tk.Label(
            encabezado, text=titulo_texto, font=("Segoe UI", 28, "bold"),
            fg=TEXTO, bg=CREMA
        ).pack(side="left")

        if periodo == "desayuno":
            horario_texto = f"🕐  Disponible de {catalogo.HORA_INICIO_DESAYUNO}:00 a {catalogo.HORA_FIN_DESAYUNO}:00"
        elif periodo == "todos":
            horario_texto = "🕐  Sin restricción de horario (modo administrador)"
        else:
            horario_texto = f"🕐  Disponible de {catalogo.HORA_FIN_DESAYUNO}:00 a {catalogo.HORA_INICIO_DESAYUNO}:00"

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

        self._desactivar_scroll_mouse()

        for widget in self.winfo_children():
            widget.destroy()

        self._crear_cabecera()

        self._crear_area_scroll()

        self.dibujar_productos()

        self._crear_fila_cliente()

    # ========================================================
    # FOTO DEL PRODUCTO (con el emoji como respaldo)
    # ========================================================

    def _foto_de_producto(self, producto):
        """Devuelve un ImageTk.PhotoImage listo para mostrarse, o
        None si no se encontró ninguna imagen suficientemente
        parecida al nombre del producto en Recursos/productos/, si
        Pillow no está disponible, o si el archivo no se pudo abrir
        (en cualquiera de esos casos la tarjeta cae de vuelta al
        emoji, sin generar ningún error)."""

        if not _PIL_DISPONIBLE:
            return None

        nombre = producto.get("nombre", "")

        if nombre in self._fotos_cache:
            return self._fotos_cache[nombre]

        ruta_relativa = imagenes_productos.buscar_imagen_de_producto(nombre)
        foto = None

        if ruta_relativa:
            ruta_absoluta = os.path.join(
                imagenes_productos.RAIZ_PROYECTO, ruta_relativa
            )
            try:
                imagen = Image.open(ruta_absoluta).convert("RGB")

                # thumbnail() reduce la imagen manteniendo su proporción
                # original (no la deforma), respetando _ANCHO_FOTO/_ALTO_FOTO
                # como límites máximos.
                imagen.thumbnail((_ANCHO_FOTO, _ALTO_FOTO), Image.LANCZOS)

                # La pegamos centrada sobre un lienzo del tamaño fijo de
                # la tarjeta, para que todas las tarjetas midan igual
                # aunque las fotos originales tengan proporciones distintas.
                lienzo = Image.new("RGB", (_ANCHO_FOTO, _ALTO_FOTO), "#FFF4DE")
                x = (_ANCHO_FOTO - imagen.width) // 2
                y = (_ALTO_FOTO - imagen.height) // 2
                lienzo.paste(imagen, (x, y))

                foto = ImageTk.PhotoImage(lienzo)
            except (OSError, FileNotFoundError):
                foto = None

        self._fotos_cache[nombre] = foto
        return foto

    # ========================================================
    # DIBUJAR PRODUCTOS (cuadrícula)
    # ========================================================

    def dibujar_productos(self):

        for widget in self.productos_frame.winfo_children():
            widget.destroy()

        # Vuelve a poner el scroll hasta arriba: si el cajero venía
        # desplazado hacia abajo y cambia de categoría o busca algo
        # distinto, debe empezar a ver la cuadrícula desde el inicio.
        if hasattr(self, "_contenedor_productos"):
            self._contenedor_productos.canvas.yview_moveto(0)

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

            foto = self._foto_de_producto(producto)

            if foto is not None:
                etiqueta_foto = tk.Label(tarjeta, image=foto, bg="#FFF4DE")
                etiqueta_foto.image = foto  # referencia extra, por si acaso
                etiqueta_foto.pack(fill="x", pady=(0, 8))
            else:
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
