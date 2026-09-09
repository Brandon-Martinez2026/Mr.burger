import tkinter as tk
import subprocess
import sys
import os

try:
    from PIL import Image, ImageTk, ImageDraw
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
# Paleta oficial de Mr.Burger, tomada de las figuras de
# decoración para que todo combine de forma consistente.
# ============================================================

CREMA = "#FBF0DC"          # Fondo principal
BEIGE_PISTA = "#F3E3C3"    # Pista/track de la barra de progreso
TEXTO = "#2B2118"          # Texto oscuro
GRIS = "#8A7B68"           # Texto secundario

NARANJA_INICIO = "#F2891D"  # Inicio del degradado de la barra
MARRON_MEDIO = "#5C3A21"    # Punto medio del degradado
AMARILLO_FINAL = "#FFEB3B"  # Extremo derecho del degradado


class PantallaCarga(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Mr.Burger")
        self.attributes("-fullscreen", False)
        self.overrideredirect(True)
        self.geometry("640x520")
        self.resizable(False, False)
        self.configure(bg=CREMA)

        # Centrar la ventana
        self.update_idletasks()
        ancho_ventana = 640
        alto_ventana = 520
        ancho_pantalla = self.winfo_screenwidth()
        alto_pantalla = self.winfo_screenheight()
        x = (ancho_pantalla - ancho_ventana) // 2
        y = (alto_pantalla - alto_ventana) // 2
        self.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")
        self.lift()
        self.focus_force()

        self.progreso = 0

        # ----------------------------------------------------
        # Carpeta base del proyecto
        # ----------------------------------------------------
        self.carpeta_base = os.path.dirname(os.path.abspath(__file__))

        # ----------------------------------------------------
        # LOGO PRINCIPAL (Recursos/01_logo_principal.png)
        # ----------------------------------------------------
        carpeta_recursos = self._resolver_carpeta(
            self.carpeta_base,
            "Recursos",
            "recursos"
        )

        self.logo_path = self._buscar_archivo(
            carpeta_recursos,
            "01_logo_principal"
        )

        self.logo_img_original = None

        if self.logo_path:
            try:
                self.logo_img_original = Image.open(
                    self.logo_path
                ).convert("RGBA")
            except Exception as e:
                print(f"No se pudo cargar el logo: {e}")
        else:
            print(
                "AVISO: no se encontró '01_logo_principal.png' "
                "dentro de la carpeta 'Recursos'."
            )

        self.logo_tk = None

        # ----------------------------------------------------
        # FIGURAS DECORATIVAS (carpeta Decoraciones)
        # ----------------------------------------------------
        carpeta_decoraciones = self._resolver_carpeta(
            self.carpeta_base,
            "Decoraciones",
            "decoraciones"
        )

        self.figuras_originales = self._cargar_figuras(
            carpeta_decoraciones
        )

        self.figuras_tk = []

        # ----------------------------------------------------
        # CANVAS
        # ----------------------------------------------------
        self.canvas = tk.Canvas(
            self,
            bg=CREMA,
            highlightthickness=0,
            bd=0
        )

        self.canvas.pack(
            fill="both",
            expand=True
        )

        # Permite salir con ESC
        self.bind(
            "<Escape>",
            lambda e: self.destroy()
        )

        self.after(
            100,
            self.actualizar
        )

    # ========================================================
    # UTILIDADES
    # ========================================================

    def _resolver_carpeta(self, base, *nombres_posibles):
        """Devuelve la primera carpeta existente entre las opciones
        dadas (permite que el proyecto funcione sin importar si el
        nombre de la carpeta está en mayúsculas o minúsculas)."""

        for nombre in nombres_posibles:
            ruta = os.path.join(base, nombre)
            if os.path.isdir(ruta):
                return ruta

        return os.path.join(base, nombres_posibles[0])

    def _buscar_archivo(self, carpeta, nombre_base):
        """Busca un archivo de imagen de forma robusta."""

        extensiones = [".png", ".jpg", ".jpeg", ".webp", ".bmp"]

        for ext in extensiones:
            ruta = os.path.join(carpeta, nombre_base + ext)

            if os.path.isfile(ruta):
                return ruta

        if os.path.isdir(carpeta):
            nombre_objetivo = nombre_base.lower()

            for raiz, carpetas, archivos in os.walk(carpeta):
                for archivo in archivos:
                    base, ext = os.path.splitext(archivo)

                    if (
                        base.lower() == nombre_objetivo
                        and ext.lower() in extensiones
                    ):
                        return os.path.join(raiz, archivo)

        return None

    def _cargar_figuras(self, carpeta):
        """Carga las figuras decorativas (manchas) desde la carpeta
        'Decoraciones', reemplazando las manchas dibujadas a mano
        por las figuras oficiales de la marca."""

        nombres = [
            "FiguraMostaza.png",
            "FiguraRoja.png",
            "FiguraNaranja.png",
        ]

        figuras = []

        if not carpeta or not os.path.isdir(carpeta):
            print(
                "AVISO: no se encontró la carpeta 'Decoraciones'."
            )
            return figuras

        for nombre in nombres:
            ruta = os.path.join(carpeta, nombre)

            if os.path.isfile(ruta):
                try:
                    figuras.append(
                        Image.open(ruta).convert("RGBA")
                    )
                except Exception as e:
                    print(f"No se pudo cargar {nombre}: {e}")

        return figuras

    # ========================================================
    # DECORACIONES (figuras de marca en las esquinas)
    # ========================================================

    def _dibujar_decoraciones(self, ancho, alto):

        if not self.figuras_originales:
            return

        self.figuras_tk = []

        tam = 150

        # (imagen, posición x, posición y, ancla)
        # Se colocan sutilmente recortadas en cada esquina,
        # igual que las manchas originales pero con las
        # figuras oficiales de decoración.
        posiciones = [
            (self.figuras_originales[0 % len(self.figuras_originales)], -35, -35, "nw"),
            (self.figuras_originales[1 % len(self.figuras_originales)], ancho + 35, -35, "ne"),
            (self.figuras_originales[1 % len(self.figuras_originales)], -35, alto + 35, "sw"),
            (self.figuras_originales[2 % len(self.figuras_originales)], ancho + 35, alto + 35, "se"),
        ]

        for img_original, x, y, ancla in posiciones:

            img = img_original.copy()
            img.thumbnail((tam, tam), FILTRO_REESCALADO)

            # Opacidad suave para que sea elegante y no
            # compita visualmente con el logo.
            r, g, b, a = img.split()
            a = a.point(lambda px: int(px * 0.85))
            img.putalpha(a)

            img_tk = ImageTk.PhotoImage(img)
            self.figuras_tk.append(img_tk)

            self.canvas.create_image(
                x,
                y,
                image=img_tk,
                anchor=ancla
            )

    # ========================================================
    # BARRA DE PROGRESO (con degradado, estilo profesional)
    # ========================================================

    def _interpolar_color(self, t, c1, c2, c3):
        """Interpola entre 3 colores: c1 -> c2 -> c3 según t (0-1)."""

        def hex_a_rgb(h):
            h = h.lstrip("#")
            return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

        r1, g1, b1 = hex_a_rgb(c1)
        r2, g2, b2 = hex_a_rgb(c2)
        r3, g3, b3 = hex_a_rgb(c3)

        if t <= 0.5:
            f = t / 0.5
            r = r1 + (r2 - r1) * f
            g = g1 + (g2 - g1) * f
            b = b1 + (b2 - b1) * f
        else:
            f = (t - 0.5) / 0.5
            r = r2 + (r3 - r2) * f
            g = g2 + (g3 - g2) * f
            b = b2 + (b3 - b2) * f

        return (int(r), int(g), int(b), 255)

    def _crear_imagen_barra(self, ancho, alto, radio, progreso_ancho):
        """Genera la imagen de la barra de progreso con esquinas
        redondeadas y relleno en degradado (naranja -> marrón -> amarillo)."""

        barra = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
        draw = ImageDraw.Draw(barra)

        # Pista de fondo
        draw.rectangle([0, 0, ancho, alto], fill=BEIGE_PISTA)

        # Relleno en degradado, calculado sobre el ancho total
        # de la barra para que el color avance de forma fluida.
        ancho_relleno = max(0, min(int(progreso_ancho), ancho))

        for x in range(ancho_relleno):
            t = x / max(ancho - 1, 1)
            color = self._interpolar_color(
                t,
                NARANJA_INICIO,
                MARRON_MEDIO,
                AMARILLO_FINAL
            )
            draw.line([(x, 0), (x, alto)], fill=color)

        # Máscara de esquinas redondeadas
        mascara = Image.new("L", (ancho, alto), 0)
        ImageDraw.Draw(mascara).rounded_rectangle(
            [0, 0, ancho - 1, alto - 1],
            radius=radio,
            fill=255
        )

        barra.putalpha(mascara)

        return barra

    # ========================================================
    # DIBUJO PRINCIPAL
    # ========================================================

    def actualizar(self):

        self.canvas.delete("all")

        ancho = self.winfo_width()
        alto = self.winfo_height()

        # ----------------------------------------------------
        # Figuras decorativas de marca (esquinas)
        # ----------------------------------------------------

        self._dibujar_decoraciones(ancho, alto)

        cx = ancho // 2

        # ----------------------------------------------------
        # LOGO PRINCIPAL
        # ----------------------------------------------------

        logo_y = alto // 2 - 150
        logo_alto_reservado = 0

        if self.logo_img_original is not None:

            tam_logo = 190

            img = self.logo_img_original.copy()

            img.thumbnail(
                (tam_logo, tam_logo),
                FILTRO_REESCALADO
            )

            self.logo_tk = ImageTk.PhotoImage(img)

            self.canvas.create_image(
                cx,
                logo_y,
                image=self.logo_tk,
                anchor="center"
            )

            logo_alto_reservado = img.height

        else:

            # Si no se encuentra el logo, se muestra un texto
            # de respaldo para que la pantalla no quede vacía.
            self.canvas.create_text(
                cx,
                logo_y,
                text="MR BURGER",
                font=("Segoe UI", 34, "bold"),
                fill=TEXTO
            )

            logo_alto_reservado = 60

        # ----------------------------------------------------
        # SUBTÍTULO (estilo splash screen profesional)
        # ----------------------------------------------------
        # Se calcula a partir del borde inferior real del logo
        # para que nunca se encimen, sin importar su tamaño.

        subtitulo_y = (
            logo_y +
            logo_alto_reservado // 2 +
            30
        )

        self.canvas.create_text(
            cx,
            subtitulo_y,
            text="Sistema de Punto de Venta",
            font=("Segoe UI", 12),
            fill=GRIS
        )

        # ----------------------------------------------------
        # BARRA DE PROGRESO
        # ----------------------------------------------------

        barra_ancho = 360
        barra_alto = 12
        radio = 6

        x = cx - barra_ancho // 2
        y = subtitulo_y + 35

        progreso_ancho = barra_ancho * self.progreso / 100

        imagen_barra = self._crear_imagen_barra(
            barra_ancho,
            barra_alto,
            radio,
            progreso_ancho
        )

        self.barra_tk = ImageTk.PhotoImage(imagen_barra)

        self.canvas.create_image(
            x,
            y,
            image=self.barra_tk,
            anchor="nw"
        )

        # ----------------------------------------------------
        # TEXTO DE ESTADO (debajo de la barra)
        # ----------------------------------------------------

        self.canvas.create_text(
            cx,
            y + barra_alto + 22,
            text=f"Cargando... {self.progreso}%",
            font=("Segoe UI", 10),
            fill=GRIS
        )

        # ----------------------------------------------------
        # PROGRESO
        # ----------------------------------------------------
        # Avanza 2% cada 15 ms para una carga fluida.

        if self.progreso < 100:

            self.progreso = min(
                self.progreso + 2,
                100
            )

            self.after(
                15,
                self.actualizar
            )

        else:

            self.after(
                150,
                self.abrir_principal
            )

    # ========================================================
    # ABRIR LOGIN
    # ========================================================

    def abrir_principal(self):

        self.destroy()

        carpeta = self.carpeta_base

        archivo_login = os.path.join(
            carpeta,
            "IniciarSesion.py"
        )

        if not os.path.isfile(archivo_login):

            print(
                "Error: no se encontró "
                f"IniciarSesion.py en:\n{carpeta}"
            )

            return

        try:

            subprocess.Popen([
                sys.executable,
                archivo_login
            ])

        except Exception as e:

            print(
                f"No se pudo abrir IniciarSesion.py: {e}"
            )


# ============================================================
# EJECUTAR
# ============================================================

if __name__ == "__main__":

    app = PantallaCarga()

    app.mainloop()
