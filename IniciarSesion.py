import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

try:
    from PIL import Image, ImageTk
except ImportError:
    print("Necesitas instalar Pillow:")
    print("pip install pillow")
    sys.exit(1)

# Permite importar el paquete local "basedatos" sin importar
# desde dónde se ejecute este archivo.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from basedatos.repositorio_usuarios import autenticar
from basedatos.conexion import ErrorBaseDatos


# ============================================================
# COLORES
# ============================================================

ROJO = "#C0392B"
ROJO_OSCURO = "#7A2418"
CREMA = "#FBF0DC"
BLANCO = "#FFFFFF"
GRIS = "#777777"
BORDE = "#D9C9A8"
TEXTO = "#2B2118"
FONDO_INPUT = "#FAFAFA"


# ============================================================
# AUTENTICACIÓN
# ============================================================
# Mr.Burger se maneja únicamente con credenciales: no se pide ni
# se guarda correo electrónico en ningún punto del sistema. Cada
# intento de inicio de sesión se valida contra la tabla
# "usuarios" de mr_burguer_db (usuario + contraseña con hash).
# Según el rol devuelto, IniciarSesion.py decide a qué pantalla
# redirigir: "administrador" -> MenuAdministrador.py
#            cualquier otro  -> MenuPrincipal.py (cajero)
# ============================================================
<<<<<<< HEAD
=======
# Cada usuario tiene una contraseña y un rol asociado.
# Según el rol, IniciarSesion.py decide a qué pantalla
# redirigir: "administrador" -> MenuAdministrador.py
#            "cajero"        -> MenuPrincipal.py
# ============================================================

USUARIOS = {
    "admin": {
        "password": "admin",
        "rol": "administrador"
    },
    "cajero": {
        "password": "cajero123",
        "rol": "cajero"
    }
}
>>>>>>> 3af9e03b097cc6b36f9ba114fa6774e55e00e44f


# ============================================================
# FILTRO PARA REDIMENSIONAR IMÁGENES
# ============================================================

FILTRO_REESCALADO = Image.Resampling.LANCZOS


# ============================================================
# CLASE LOGIN
# ============================================================

class IniciarSesion(tk.Tk):

    def __init__(self):
        super().__init__()

        # ====================================================
        # CONFIGURACIÓN DE LA VENTANA
        # ====================================================

        self.title("Mr.Burger - Iniciar sesión")

        # Pantalla completa
        self.attributes("-fullscreen", True)

        # Elimina completamente la barra superior de Windows
        # incluyendo la X, minimizar y maximizar.
        self.overrideredirect(True)

        # Fondo general
        self.configure(
            bg=BLANCO
        )

        # ====================================================
        # VARIABLES
        # ====================================================

        self.usuario_var = tk.StringVar()
        self.password_var = tk.StringVar()

        self.mostrar_password = False

        # Datos del usuario autenticado (id_usuario, nombre_completo,
        # usuario, rol), llenados por autenticar() al iniciar sesión.
        self.usuario_autenticado = None

        self.logo_original = None
        self.logo_tk = None

        # ====================================================
        # CARGAR LOGO
        # ====================================================

        self.cargar_logo()

        # ====================================================
        # CREAR INTERFAZ
        # ====================================================

        self.crear_interfaz()

        # ====================================================
        # ATAJOS
        # ====================================================

        # ESC = salir
        self.bind(
            "<Escape>",
            lambda e: self.salir()
        )

        # ENTER = iniciar sesión
        self.bind(
            "<Return>",
            lambda e: self.iniciar_sesion()
        )

    # ========================================================
    # CARGAR LOGO
    # ========================================================

    def cargar_logo(self):

        carpeta = os.path.dirname(
            os.path.abspath(__file__)
        )

        carpeta_recursos = None

        for nombre in ("Recursos", "recursos"):
            posible = os.path.join(carpeta, nombre)
            if os.path.isdir(posible):
                carpeta_recursos = posible
                break

        if carpeta_recursos is None:
            carpeta_recursos = os.path.join(carpeta, "Recursos")

        ruta = os.path.join(
            carpeta_recursos,
            "Logo_fondoBlanco.png"
        )

        # Comprobar si existe
        if not os.path.exists(ruta):

            print(
                "=========================================="
            )

            print(
                "NO SE ENCONTRÓ EL LOGO"
            )

            print(
                "Ruta buscada:"
            )

            print(ruta)

            print(
                "=========================================="
            )

            return

        try:

            self.logo_original = Image.open(
                ruta
            ).convert("RGBA")

            print(
                "=========================================="
            )

            print(
                "LOGO CARGADO CORRECTAMENTE"
            )

            print(
                "Ruta:"
            )

            print(ruta)

            print(
                "Tamaño:",
                self.logo_original.size
            )

            print(
                "=========================================="
            )

        except Exception as e:

            print(
                "Error cargando el logo:"
            )

            print(e)

    # ========================================================
    # CREAR INTERFAZ
    # ========================================================

    def crear_interfaz(self):

        # ====================================================
        # CONTENEDOR PRINCIPAL
        # ====================================================

        contenedor = tk.Frame(
            self,
            bg=BLANCO
        )

        contenedor.pack(
            fill="both",
            expand=True
        )

        # ====================================================
        # CONFIGURACIÓN DE COLUMNAS
        # ====================================================

        # 45% para login
        # 55% para logo

        contenedor.grid_columnconfigure(
            0,
            weight=45
        )

        contenedor.grid_columnconfigure(
            1,
            weight=55
        )

        contenedor.grid_rowconfigure(
            0,
            weight=1
        )

        # ====================================================
        # PANEL IZQUIERDO
        # ====================================================

        panel_izquierdo = tk.Frame(
            contenedor,
            bg=BLANCO
        )

        panel_izquierdo.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        # ====================================================
        # PANEL DERECHO
        # ====================================================

        panel_derecho = tk.Frame(
            contenedor,
            bg=ROJO
        )

        panel_derecho.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        # ====================================================
        # LOGIN
        # ====================================================

        login = tk.Frame(
            panel_izquierdo,
            bg=BLANCO
        )

        login.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
            width=430
        )

        # ====================================================
        # NOMBRE DEL SISTEMA
        # ====================================================

        tk.Label(
            login,
            text="MR.BURGER",
            font=("Segoe UI", 20, "bold"),
            fg=ROJO,
            bg=BLANCO
        ).pack(
            pady=(0, 18)
        )

        # ====================================================
        # TÍTULO
        # ====================================================

        tk.Label(
            login,
            text="Iniciar sesión",
            font=("Segoe UI", 34, "bold"),
            fg=TEXTO,
            bg=BLANCO
        ).pack()

        # ====================================================
        # SUBTÍTULO
        # ====================================================

        tk.Label(
            login,
            text="Ingresa tus datos para continuar",
            font=("Segoe UI", 12),
            fg=GRIS,
            bg=BLANCO
        ).pack(
            pady=(8, 38)
        )

        # ====================================================
        # LABEL USUARIO
        # ====================================================

        tk.Label(
            login,
            text="Usuario",
            font=("Segoe UI", 11, "bold"),
            fg=TEXTO,
            bg=BLANCO
        ).pack(
            anchor="w"
        )

        # ====================================================
        # CAMPO USUARIO
        # ====================================================

        self.entrada_usuario = tk.Entry(
            login,
            textvariable=self.usuario_var,
            font=("Segoe UI", 14),
            fg=TEXTO,
            bg=FONDO_INPUT,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=BORDE,
            highlightcolor=ROJO
        )

        self.entrada_usuario.pack(
            fill="x",
            ipady=13,
            pady=(7, 24)
        )

        # ====================================================
        # LABEL CONTRASEÑA
        # ====================================================

        tk.Label(
            login,
            text="Contraseña",
            font=("Segoe UI", 11, "bold"),
            fg=TEXTO,
            bg=BLANCO
        ).pack(
            anchor="w"
        )

        # ====================================================
        # CONTENEDOR CONTRASEÑA
        # ====================================================

        marco_password = tk.Frame(
            login,
            bg=FONDO_INPUT,
            highlightthickness=1,
            highlightbackground=BORDE,
            highlightcolor=ROJO
        )

        marco_password.pack(
            fill="x",
            pady=(7, 32)
        )

        # ====================================================
        # CAMPO CONTRASEÑA
        # ====================================================

        self.entrada_password = tk.Entry(
            marco_password,
            textvariable=self.password_var,
            font=("Segoe UI", 14),
            fg=TEXTO,
            bg=FONDO_INPUT,
            relief="flat",
            bd=0,
            show="•"
        )

        self.entrada_password.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=13,
            padx=(12, 0)
        )

        # ====================================================
        # BOTÓN OJO
        # ====================================================

        self.boton_ojo = tk.Canvas(
            marco_password,
            width=45,
            height=45,
            bg=FONDO_INPUT,
            highlightthickness=0,
            bd=0,
            cursor="hand2"
        )

        self.boton_ojo.pack(
            side="right",
            padx=5
        )

        self.boton_ojo.bind(
            "<Button-1>",
            lambda e: self.mostrar_contrasena()
        )

        self.dibujar_ojo()

        # ====================================================
        # BOTÓN INICIAR SESIÓN
        # ====================================================

        self.boton_login = tk.Button(
            login,
            text="INICIAR SESIÓN",
            font=("Segoe UI", 12, "bold"),
            fg=BLANCO,
            bg=ROJO,
            activeforeground=BLANCO,
            activebackground=ROJO_OSCURO,
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.iniciar_sesion
        )

        self.boton_login.pack(
            fill="x",
            ipady=14,
            pady=(0, 14)
        )

        # ====================================================
        # BOTÓN SALIR
        # ====================================================

        self.boton_salir = tk.Button(
            login,
            text="SALIR",
            font=("Segoe UI", 11, "bold"),
            fg=ROJO,
            bg=BLANCO,
            activeforeground=BLANCO,
            activebackground=ROJO,
            relief="solid",
            bd=1,
            highlightthickness=0,
            cursor="hand2",
            command=self.salir
        )

        self.boton_salir.pack(
            fill="x",
            ipady=11
        )

        # ====================================================
        # INFORMACIÓN
        # ====================================================

        tk.Label(
            login,
            text="Sistema de Punto de Venta",
            font=("Segoe UI", 9),
            fg=GRIS,
            bg=BLANCO
        ).pack(
            pady=(26, 0)
        )

        # ====================================================
        # LOGO - PANEL DERECHO
        # ====================================================

        if self.logo_original is not None:

            # Obtener resolución
            ancho = self.winfo_screenwidth()
            alto = self.winfo_screenheight()

            # =================================================
            # TAMAÑO DEL LOGO
            # =================================================

            ancho_maximo = int(
                ancho * 0.43
            )

            alto_maximo = int(
                alto * 0.65
            )

            # Copiar imagen
            imagen = self.logo_original.copy()

            # Mantener proporción
            imagen.thumbnail(
                (
                    ancho_maximo,
                    alto_maximo
                ),
                FILTRO_REESCALADO
            )

            # Convertir a imagen Tkinter
            self.logo_tk = ImageTk.PhotoImage(
                imagen
            )

            # =================================================
            # MOSTRAR LOGO
            # =================================================

            logo_label = tk.Label(
                panel_derecho,
                image=self.logo_tk,
                bg=ROJO,
                bd=0
            )

            logo_label.place(
                relx=0.5,
                rely=0.44,
                anchor="center"
            )

        else:

            # =================================================
            # SI NO SE ENCUENTRA EL LOGO
            # =================================================

            tk.Label(
                panel_derecho,
                text="MR.BURGER",
                font=("Segoe UI", 65, "bold"),
                fg=BLANCO,
                bg=ROJO
            ).place(
                relx=0.5,
                rely=0.44,
                anchor="center"
            )

        # ====================================================
        # ESLOGAN
        # ====================================================

        tk.Label(
            panel_derecho,
            text="DISFRUTA CADA MOMENTO",
            font=("Segoe UI", 13, "bold"),
            fg=BLANCO,
            bg=ROJO
        ).place(
            relx=0.5,
            rely=0.80,
            anchor="center"
        )

        # ====================================================
        # LÍNEA DECORATIVA
        # ====================================================

        tk.Frame(
            panel_derecho,
            bg=BLANCO,
            height=4,
            width=200
        ).place(
            relx=0.5,
            rely=0.85,
            anchor="center"
        )

        # ====================================================
        # FOCUS INICIAL
        # ====================================================

        self.entrada_usuario.focus_set()

    # ========================================================
    # DIBUJAR OJO
    # ========================================================

    def dibujar_ojo(self):

        self.boton_ojo.delete("all")

        # ====================================================
        # PARTE SUPERIOR DEL OJO
        # ====================================================

        self.boton_ojo.create_arc(
            5,
            8,
            40,
            38,
            start=25,
            extent=130,
            style="arc",
            outline=GRIS,
            width=2
        )

        # ====================================================
        # PARTE INFERIOR DEL OJO
        # ====================================================

        self.boton_ojo.create_arc(
            5,
            8,
            40,
            38,
            start=205,
            extent=130,
            style="arc",
            outline=GRIS,
            width=2
        )

        # ====================================================
        # PUPILA
        # ====================================================

        self.boton_ojo.create_oval(
            14,
            12,
            31,
            29,
            outline=GRIS,
            width=2
        )

        self.boton_ojo.create_oval(
            19,
            17,
            26,
            24,
            fill=GRIS,
            outline=GRIS
        )

        # ====================================================
        # LÍNEA CUANDO ESTÁ OCULTA
        # ====================================================

        if not self.mostrar_password:

            self.boton_ojo.create_line(
                6,
                7,
                39,
                38,
                fill=GRIS,
                width=2
            )

    # ========================================================
    # MOSTRAR / OCULTAR CONTRASEÑA
    # ========================================================

    def mostrar_contrasena(self):

        self.mostrar_password = not self.mostrar_password

        if self.mostrar_password:

            self.entrada_password.config(
                show=""
            )

        else:

            self.entrada_password.config(
                show="•"
            )

        self.dibujar_ojo()

    # ========================================================
    # INICIAR SESIÓN
    # ========================================================

    def iniciar_sesion(self):

        usuario = self.usuario_var.get().strip()

        password = self.password_var.get()

        # ====================================================
        # VALIDAR USUARIO
        # ====================================================

        if not usuario:

            messagebox.showwarning(
                "Mr.Burger",
                "Ingresa tu usuario.",
                parent=self
            )

            self.entrada_usuario.focus_set()

            return

        # ====================================================
        # VALIDAR CONTRASEÑA
        # ====================================================

        if not password:

            messagebox.showwarning(
                "Mr.Burger",
                "Ingresa tu contraseña.",
                parent=self
            )

            self.entrada_password.focus_set()

            return

        # ====================================================
        # COMPROBAR CREDENCIALES CONTRA LA BASE DE DATOS
        # ====================================================

<<<<<<< HEAD
        try:

            datos_usuario = autenticar(usuario, password)

        except ErrorBaseDatos as error:

            messagebox.showerror(
                "Mr.Burger",
                str(error),
                parent=self
            )

            return

        if datos_usuario is not None:

            # Guardamos la sesión autenticada para pasarla a la
            # siguiente pantalla (id_usuario y nombre reales de la
            # tabla "usuarios").
            self.usuario_autenticado = datos_usuario

=======
        datos_usuario = USUARIOS.get(usuario)

        if (
            datos_usuario is not None
            and
            password == datos_usuario["password"]
        ):

>>>>>>> 3af9e03b097cc6b36f9ba114fa6774e55e00e44f
            if datos_usuario["rol"] == "administrador":

                self.abrir_menu_administrador()

            else:

                self.abrir_menu_principal()

        else:

            messagebox.showerror(
                "Acceso denegado",
                "Usuario o contraseña incorrectos.",
                parent=self
            )

            # Limpiar contraseña
            self.entrada_password.delete(
                0,
                tk.END
            )

            self.entrada_password.focus_set()

    # ========================================================
    # SALIR
    # ========================================================

    def salir(self):

        respuesta = messagebox.askyesno(
            "Salir",
            "¿Estás seguro de que deseas salir?",
            parent=self
        )

        if respuesta:

            self.destroy()

    # ========================================================
    # ABRIR VENTANA (uso interno / compartido)
    # ========================================================

    def _abrir_ventana(self, nombre_archivo, nombre_amigable):

        carpeta = os.path.dirname(
            os.path.abspath(__file__)
        )

        archivo_menu = os.path.join(
            carpeta,
            nombre_archivo
        )

        # ====================================================
        # COMPROBAR ARCHIVO
        # ====================================================

        if not os.path.isfile(archivo_menu):

            messagebox.showerror(
                "Error",
                f"No se encontró {nombre_archivo}.",
                parent=self
            )

            return

        # ====================================================
        # ABRIR VENTANA
        # ====================================================

        try:

            subprocess.Popen(
                [
                    sys.executable,
                    archivo_menu
                ]
            )

            self.destroy()

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"No se pudo abrir {nombre_amigable}:\n{e}",
                parent=self
            )

    # ========================================================
    # ABRIR MENÚ PRINCIPAL (CAJERO)
    # ========================================================

    def abrir_menu_principal(self):

        self._abrir_ventana(
            "MenuPrincipal.py",
            "el menú principal"
        )

    # ========================================================
    # ABRIR MENÚ ADMINISTRADOR
    # ========================================================

    def abrir_menu_administrador(self):

        self._abrir_ventana(
            "MenuAdministrador.py",
            "el menú de administrador"
        )


# ============================================================
# EJECUTAR PROGRAMA
# ============================================================

if __name__ == "__main__":

    app = IniciarSesion()

    app.mainloop()