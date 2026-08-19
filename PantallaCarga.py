import tkinter as tk
import subprocess
import sys
import os

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


class PantallaCarga(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Mr.Burger")
        self.attributes("-fullscreen", False)
        self.overrideredirect(True)
        self.geometry("600x500")
        self.resizable(False, False)
        self.configure(bg="#F3F3F3")

        # Centrar la ventana de 500x600
        self.update_idletasks()
        ancho_ventana = 600
        alto_ventana = 500
        ancho_pantalla = self.winfo_screenwidth()
        alto_pantalla = self.winfo_screenheight()
        x = (ancho_pantalla - ancho_ventana) // 2
        y = (alto_pantalla - alto_ventana) // 2
        self.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")
        self.lift()
        self.focus_force()

        self.progreso = 0

        # ----------------------------------------------------
        # Ruta del logo
        # Busca la carpeta "recursos" junto a este archivo.
        # Esto permite mover el programa a otra computadora.
        # ----------------------------------------------------
        carpeta_base = os.path.dirname(os.path.abspath(__file__))
        carpeta_logo = os.path.join(carpeta_base, "recursos")

        self.logo_path = self._buscar_logo(
            carpeta_logo,
            "01_logo_p"
        )

        self.logo_img_original = None

        if self.logo_path:
            print(f"Logo encontrado: {self.logo_path}")
            try:
                self.logo_img_original = Image.open(
                    self.logo_path
                ).convert("RGBA")
            except Exception as e:
                print(f"No se pudo cargar el logo: {e}")

        if not self.logo_path:
            print(
                "AVISO: no se encontró ningún logo. "
                "Coloca Logo_fondoBlanco.png dentro de la carpeta "
                "'recursos' junto a este archivo."
            )

        self.logo_tk = None

        # ----------------------------------------------------
        # CANVAS
        # ----------------------------------------------------
        self.canvas = tk.Canvas(
            self,
            bg="#FBF0DC",
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

    def _buscar_logo(self, carpeta, nombre_base):
        """Busca el logo de forma robusta en la carpeta del programa."""

        extensiones = [
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
            ".bmp"
        ]

        # 1. Buscar por nombre exacto en la carpeta indicada.
        for ext in extensiones:
            ruta = os.path.join(
                carpeta,
                nombre_base + ext
            )

            if os.path.isfile(ruta):
                return ruta

        # 2. Buscar de forma recursiva dentro de la carpeta.
        if os.path.isdir(carpeta):
            nombre_objetivo = nombre_base.lower()

            for raiz, carpetas, archivos in os.walk(carpeta):
                for archivo in archivos:
                    base, ext = os.path.splitext(archivo)

                    if (
                        base.lower() == nombre_objetivo
                        and ext.lower() in extensiones
                    ):
                        return os.path.join(
                            raiz,
                            archivo
                        )

        return None

    def _dibujar_blob(
        self,
        cx,
        cy,
        radio,
        color
    ):
        """Dibuja una mancha/splash orgánica."""

        import math
        import random

        random.seed(int(cx + cy))

        puntos = []

        n = 10

        for i in range(n):

            angulo = (
                2 * math.pi / n
            ) * i

            r = radio * random.uniform(
                0.65,
                1.05
            )

            x = (
                cx +
                r * math.cos(angulo)
            )

            y = (
                cy +
                r * math.sin(angulo)
            )

            puntos.extend([
                x,
                y
            ])

        self.canvas.create_polygon(
            puntos,
            fill=color,
            outline="",
            smooth=True
        )

    def _dibujar_hoja(
        self,
        x,
        y,
        escala=1.0,
        color="#3D9B35"
    ):
        """Dibuja un grupo de hojas de pasto."""

        import math

        base_angulos = [
            -25,
            -10,
            5,
            20,
            35
        ]

        for ang in base_angulos:

            largo = 45 * escala

            rad = math.radians(ang)

            x2 = (
                x +
                largo * math.cos(rad)
            )

            y2 = (
                y -
                largo * math.sin(rad) -
                20 * escala
            )

            self.canvas.create_line(
                x,
                y,
                x2,
                y2,
                fill=color,
                width=6,
                smooth=True,
                capstyle="round"
            )

    def _dibujar_decoraciones(
        self,
        ancho,
        alto
    ):
        margen = 0

        # ----------------------------------------------------
        # Manchas de colores
        # ----------------------------------------------------

        self._dibujar_blob(
            margen + 25,
            margen + 25,
            85,
            "#F2B01E"
        )

        self._dibujar_blob(
            ancho - margen - 30,
            margen + 25,
            90,
            "#D0432B"
        )

        self._dibujar_blob(
            margen + 20,
            alto - margen - 30,
            85,
            "#D0432B"
        )

        self._dibujar_blob(
            ancho - margen - 30,
            alto - margen - 25,
            90,
            "#E8901E"
        )

        # ----------------------------------------------------
        # Hojas decorativas
        # ----------------------------------------------------

        self._dibujar_hoja(
            ancho * 0.60,
            alto * 0.15,
            escala=0.65
        )

        self._dibujar_hoja(
            ancho * 0.10,
            alto * 0.40,
            escala=0.65
        )

        self._dibujar_hoja(
            ancho * 0.85,
            alto * 0.50,
            escala=0.65
        )

        self._dibujar_hoja(
            ancho * 0.38,
            alto * 0.85,
            escala=0.65
        )

    # ========================================================
    # DIBUJO PRINCIPAL
    # ========================================================

    def actualizar(self):

        self.canvas.delete("all")

        ancho = self.winfo_width()
        alto = self.winfo_height()

        # ----------------------------------------------------
        # Fondo decorativo
        # ----------------------------------------------------

        self._dibujar_decoraciones(
            ancho,
            alto
        )

        cx = ancho // 2

        # ----------------------------------------------------
        # LOGO
        # ----------------------------------------------------

        logo_alto_reservado = 0

        if self.logo_img_original is not None:

            tam_logo = 100

            img = self.logo_img_original.copy()

            img.thumbnail(
                (
                    tam_logo,
                    tam_logo
                ),
                FILTRO_REESCALADO
            )

            self.logo_tk = ImageTk.PhotoImage(img)

            logo_y = (
                alto // 2 -
                105
            )

            self.canvas.create_image(
                cx,
                logo_y,
                image=self.logo_tk,
                anchor="center"
            )

            logo_alto_reservado = img.height

        # ----------------------------------------------------
        # TÍTULO
        # ----------------------------------------------------

        titulo_y = (
            alto // 2 -
            95 +
            (
                logo_alto_reservado // 2
                if self.logo_img_original
                else 0
            )
        )

        self.canvas.create_text(
            cx,
            titulo_y + 35,
            text="Mr.Burger",
            font=("Arial", 32),
            fill="black"
        )

        # ----------------------------------------------------
        # BARRA DE PROGRESO
        # ----------------------------------------------------

        barra_ancho = 330
        barra_alto = 28

        x = (
            cx -
            barra_ancho // 2
        )

        y = (
            alto // 2 +
            35
        )

        # Fondo de la barra
        self.canvas.create_rectangle(
            x,
            y,
            x + barra_ancho,
            y + barra_alto,
            fill="#F5D98A",
            outline=""
        )

        # Progreso
        progreso_ancho = (
            barra_ancho *
            self.progreso /
            100
        )

        self.canvas.create_rectangle(
            x,
            y,
            x + progreso_ancho,
            y + barra_alto,
            fill="#F97316",
            outline=""
        )

        # Porcentaje
        self.canvas.create_text(
            x + 10,
            y + barra_alto // 2,
            text=f"{self.progreso}%",
            anchor="w",
            font=("Arial", 18),
            fill="black"
        )

        # ----------------------------------------------------
        # PROGRESO RÁPIDO
        # ----------------------------------------------------
        # Avanza 2% cada 15 ms para una carga más rápida
        # y visualmente más fluida.
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

        # Carpeta donde está este archivo
        carpeta = os.path.dirname(
            os.path.abspath(__file__)
        )

        # Buscar IniciarSesion.py
        archivo_login = os.path.join(
            carpeta,
            "IniciarSesion.py"
        )

        # Verificar que exista
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