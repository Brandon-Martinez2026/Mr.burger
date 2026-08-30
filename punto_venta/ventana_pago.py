"""
ventana_pago.py
------------------------------------------------------------
Ventana modal que se abre al presionar 'Pagar'. Permite elegir
si el pedido se paga en efectivo, con tarjeta o de forma mixta
(parte efectivo, parte tarjeta).
------------------------------------------------------------
"""

import tkinter as tk
from tkinter import messagebox

from estilos import ROJO, ROJO_CLARO, BLANCO, TEXTO, VERDE, NARANJA


class VentanaMetodoPago(tk.Toplevel):
    """Pequeña ventana modal que se abre al presionar 'Pagar'.
    Permite elegir si el pedido se paga en efectivo, con
    tarjeta o de forma mixta (parte efectivo, parte tarjeta)."""

    def __init__(self, padre, total, al_confirmar):

        super().__init__(padre)

        self.padre = padre
        self.total = total
        self.al_confirmar = al_confirmar
        self.metodo = "efectivo"

        self.title("Método de Pago")
        self.configure(bg=BLANCO)
        self.resizable(False, False)
        self.transient(padre)
        self.grab_set()

        self.geometry("420x520")
        self.after(10, self._centrar)

        self.botones_metodo = {}
        self.detalle_frame = None

        self._crear_interfaz()
        self._seleccionar_metodo("efectivo")

    # --------------------------------------------------------
    def _centrar(self):

        self.update_idletasks()

        ancho = self.winfo_width()
        alto = self.winfo_height()

        x = self.padre.winfo_rootx() + (self.padre.winfo_width() - ancho) // 2
        y = self.padre.winfo_rooty() + (self.padre.winfo_height() - alto) // 2

        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    # --------------------------------------------------------
    def _crear_interfaz(self):

        cabecera = tk.Frame(self, bg=ROJO)
        cabecera.pack(fill="x")

        tk.Label(
            cabecera,
            text="Selecciona el método de pago",
            font=("Segoe UI", 14, "bold"),
            fg="white",
            bg=ROJO
        ).pack(padx=20, pady=(18, 4), anchor="w")

        tk.Label(
            cabecera,
            text=f"Total a pagar: Q{self.total:.2f}",
            font=("Segoe UI", 20, "bold"),
            fg="white",
            bg=ROJO
        ).pack(padx=20, pady=(0, 18), anchor="w")

        # ----------------------------------------------------
        # BOTONES DE MÉTODO
        # ----------------------------------------------------

        opciones = tk.Frame(self, bg=BLANCO)
        opciones.pack(fill="x", padx=20, pady=(18, 5))

        for metodo, icono, texto in (
            ("efectivo", "💵", "Efectivo"),
            ("tarjeta", "💳", "Tarjeta"),
            ("mixto", "🔀", "Mixto"),
        ):

            boton = tk.Button(
                opciones,
                text=f"{icono}\n{texto}",
                font=("Segoe UI", 11, "bold"),
                relief="solid",
                bd=1,
                command=lambda m=metodo: self._seleccionar_metodo(m)
            )

            boton.pack(side="left", fill="x", expand=True, padx=4, ipady=12)

            self.botones_metodo[metodo] = boton

        # ----------------------------------------------------
        # DETALLE (cambia según el método elegido)
        # ----------------------------------------------------

        self.detalle_frame = tk.Frame(self, bg=BLANCO)
        self.detalle_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # ----------------------------------------------------
        # BOTONES FINALES
        # ----------------------------------------------------

        abajo = tk.Frame(self, bg=BLANCO)
        abajo.pack(fill="x", padx=20, pady=(0, 20))

        tk.Button(
            abajo,
            text="Cancelar",
            font=("Segoe UI", 11),
            bg=BLANCO,
            relief="solid",
            bd=1,
            command=self.destroy
        ).pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=9)

        tk.Button(
            abajo,
            text="Confirmar Pago",
            font=("Segoe UI", 11, "bold"),
            bg=ROJO_CLARO,
            fg="white",
            activebackground=ROJO,
            activeforeground="white",
            relief="flat",
            command=self._confirmar
        ).pack(side="left", fill="x", expand=True, padx=(5, 0), ipady=9)

    # --------------------------------------------------------
    def _seleccionar_metodo(self, metodo):

        self.metodo = metodo

        for nombre, boton in self.botones_metodo.items():

            if nombre == metodo:
                boton.configure(bg=ROJO_CLARO, fg="white")
            else:
                boton.configure(bg=BLANCO, fg=TEXTO)

        self._dibujar_detalle()

    # --------------------------------------------------------
    def _dibujar_detalle(self):

        for widget in self.detalle_frame.winfo_children():
            widget.destroy()

        if self.metodo == "efectivo":
            self._detalle_efectivo()
        elif self.metodo == "tarjeta":
            self._detalle_tarjeta()
        else:
            self._detalle_mixto()

    # --------------------------------------------------------
    def _detalle_efectivo(self):

        tk.Label(
            self.detalle_frame,
            text="Monto recibido en efectivo",
            font=("Segoe UI", 11),
            fg=TEXTO,
            bg=BLANCO
        ).pack(anchor="w", pady=(5, 3))

        self.entry_recibido = tk.Entry(
            self.detalle_frame,
            font=("Segoe UI", 13),
            bd=1,
            relief="solid"
        )

        self.entry_recibido.pack(fill="x", ipady=6)
        self.entry_recibido.insert(0, f"{self.total:.2f}")
        self.entry_recibido.bind("<KeyRelease>", lambda e: self._actualizar_cambio())

        self.lbl_cambio = tk.Label(
            self.detalle_frame,
            text="Cambio a entregar: Q0.00",
            font=("Segoe UI", 12, "bold"),
            fg=VERDE,
            bg=BLANCO
        )

        self.lbl_cambio.pack(anchor="w", pady=(10, 0))

        self._actualizar_cambio()

    def _actualizar_cambio(self):

        try:
            recibido = float(self.entry_recibido.get())
        except ValueError:
            recibido = 0

        cambio = recibido - self.total

        if cambio < 0:
            self.lbl_cambio.configure(
                text="Falta dinero para cubrir el total",
                fg=ROJO
            )
        else:
            self.lbl_cambio.configure(
                text=f"Cambio a entregar: Q{cambio:.2f}",
                fg=VERDE
            )

    # --------------------------------------------------------
    def _detalle_tarjeta(self):

        tk.Label(
            self.detalle_frame,
            text=f"Se cobrará Q{self.total:.2f} con tarjeta.",
            font=("Segoe UI", 12),
            fg=TEXTO,
            bg=BLANCO,
            wraplength=340,
            justify="left"
        ).pack(anchor="w", pady=(10, 0))

    # --------------------------------------------------------
    def _detalle_mixto(self):

        tk.Label(
            self.detalle_frame,
            text="Monto en efectivo",
            font=("Segoe UI", 11),
            fg=TEXTO,
            bg=BLANCO
        ).pack(anchor="w", pady=(5, 3))

        self.entry_mixto_efectivo = tk.Entry(
            self.detalle_frame,
            font=("Segoe UI", 13),
            bd=1,
            relief="solid"
        )

        self.entry_mixto_efectivo.pack(fill="x", ipady=6)
        self.entry_mixto_efectivo.insert(0, "0.00")
        self.entry_mixto_efectivo.bind("<KeyRelease>", lambda e: self._actualizar_restante())

        tk.Label(
            self.detalle_frame,
            text="Monto con tarjeta",
            font=("Segoe UI", 11),
            fg=TEXTO,
            bg=BLANCO
        ).pack(anchor="w", pady=(12, 3))

        self.entry_mixto_tarjeta = tk.Entry(
            self.detalle_frame,
            font=("Segoe UI", 13),
            bd=1,
            relief="solid"
        )

        self.entry_mixto_tarjeta.pack(fill="x", ipady=6)
        self.entry_mixto_tarjeta.insert(0, f"{self.total:.2f}")
        self.entry_mixto_tarjeta.bind("<KeyRelease>", lambda e: self._actualizar_restante())

        self.lbl_restante = tk.Label(
            self.detalle_frame,
            text="",
            font=("Segoe UI", 12, "bold"),
            bg=BLANCO
        )

        self.lbl_restante.pack(anchor="w", pady=(10, 0))

        self._actualizar_restante()

    def _actualizar_restante(self):

        try:
            efectivo = float(self.entry_mixto_efectivo.get())
        except ValueError:
            efectivo = 0

        try:
            tarjeta = float(self.entry_mixto_tarjeta.get())
        except ValueError:
            tarjeta = 0

        diferencia = self.total - (efectivo + tarjeta)

        if abs(diferencia) < 0.01:
            self.lbl_restante.configure(
                text="Los montos cubren el total. ✔",
                fg=VERDE
            )
        elif diferencia > 0:
            self.lbl_restante.configure(
                text=f"Falta Q{diferencia:.2f} por cubrir",
                fg=ROJO
            )
        else:
            self.lbl_restante.configure(
                text=f"Sobran Q{abs(diferencia):.2f}",
                fg=NARANJA
            )

    # --------------------------------------------------------
    def _confirmar(self):

        detalle = {}

        if self.metodo == "efectivo":

            try:
                recibido = float(self.entry_recibido.get())
            except ValueError:
                recibido = -1

            if recibido < self.total:
                messagebox.showwarning(
                    "Mr.Burger",
                    "El monto recibido no cubre el total.",
                    parent=self
                )
                return

            detalle = {
                "recibido": round(recibido, 2),
                "cambio": round(recibido - self.total, 2)
            }

        elif self.metodo == "tarjeta":

            detalle = {"monto": round(self.total, 2)}

        else:

            try:
                efectivo = float(self.entry_mixto_efectivo.get())
                tarjeta = float(self.entry_mixto_tarjeta.get())
            except ValueError:
                messagebox.showwarning(
                    "Mr.Burger",
                    "Ingresa montos válidos.",
                    parent=self
                )
                return

            if abs((efectivo + tarjeta) - self.total) > 0.01:
                messagebox.showwarning(
                    "Mr.Burger",
                    "La suma de efectivo y tarjeta debe ser igual al total.",
                    parent=self
                )
                return

            detalle = {
                "efectivo": round(efectivo, 2),
                "tarjeta": round(tarjeta, 2)
            }

        self.al_confirmar(self.metodo, detalle)
        self.destroy()
