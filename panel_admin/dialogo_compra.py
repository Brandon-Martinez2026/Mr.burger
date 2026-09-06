"""
dialogo_compra.py
------------------------------------------------------------
Pequeño formulario que se abre al seleccionar un producto en
"Comprar Productos": pide la cantidad que se va a comprar y el
costo unitario, y se la entrega a VistaComprar para que la
agregue a la orden de compra en curso.
------------------------------------------------------------
"""

import tkinter as tk
from tkinter import messagebox

from estilos import ROJO, ROJO_CLARO, BLANCO, TEXTO


class DialogoCantidadCompra(tk.Toplevel):

    def __init__(self, padre, producto, al_confirmar):

        super().__init__(padre)

        self.producto = producto
        self.al_confirmar = al_confirmar

        self.title("Agregar a la compra")
        self.configure(bg=BLANCO)
        self.geometry("340x300")
        self.resizable(False, False)
        self.transient(padre)
        self.grab_set()

        self._crear_interfaz()

    def _crear_interfaz(self):

        nombre = self.producto["nombre"].replace("\n", " ")

        tk.Label(
            self, text=f"{self.producto.get('emoji', '')}  {nombre}",
            font=("Segoe UI", 13, "bold"), fg=ROJO, bg=BLANCO,
            wraplength=290, justify="left"
        ).pack(padx=20, pady=(20, 4), anchor="w")

        tk.Label(
            self, text=f"Stock actual: {self.producto.get('stock', 0)}",
            font=("Segoe UI", 9), fg=TEXTO, bg=BLANCO
        ).pack(padx=20, anchor="w", pady=(0, 14))

        tk.Label(
            self, text="Cantidad a comprar", font=("Segoe UI", 10, "bold"),
            fg=TEXTO, bg=BLANCO
        ).pack(anchor="w", padx=20)

        self.entry_cantidad = tk.Entry(self, font=("Segoe UI", 12), bd=1, relief="solid")
        self.entry_cantidad.insert(0, "10")
        self.entry_cantidad.pack(padx=20, fill="x", ipady=6, pady=(2, 12))

        tk.Label(
            self, text="Costo unitario (Q, opcional)", font=("Segoe UI", 10, "bold"),
            fg=TEXTO, bg=BLANCO
        ).pack(anchor="w", padx=20)

        self.entry_costo = tk.Entry(self, font=("Segoe UI", 12), bd=1, relief="solid")
        self.entry_costo.insert(0, "0.00")
        self.entry_costo.pack(padx=20, fill="x", ipady=6, pady=(2, 15))

        botones = tk.Frame(self, bg=BLANCO)
        botones.pack(fill="x", padx=20, pady=(0, 18))

        tk.Button(
            botones, text="Cancelar", font=("Segoe UI", 11), bg=BLANCO,
            relief="solid", bd=1, command=self.destroy
        ).pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=8)

        tk.Button(
            botones, text="Agregar", font=("Segoe UI", 11, "bold"),
            bg=ROJO_CLARO, fg="white", relief="flat",
            activebackground=ROJO, activeforeground="white",
            command=self._confirmar
        ).pack(side="left", fill="x", expand=True, padx=(5, 0), ipady=8)

        self.entry_cantidad.focus_set()

    def _confirmar(self):

        try:
            cantidad = int(self.entry_cantidad.get())
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Mr.Burger", "Ingresa una cantidad válida (entero mayor a 0).", parent=self)
            return

        try:
            costo_unitario = float(self.entry_costo.get() or 0)
            if costo_unitario < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Mr.Burger", "Ingresa un costo unitario válido.", parent=self)
            return

        nombre = self.producto["nombre"].replace("\n", " ")

        self.al_confirmar(self.producto["id"], nombre, cantidad, costo_unitario)

        self.destroy()
