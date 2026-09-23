"""
ventana_dividir_cuenta.py
------------------------------------------------------------
Ventana modal para dividir la cuenta de un pedido entre varias
personas. Primero pregunta cuántas cuentas se necesitan, y
luego deja repartir, producto por producto (incluso unidad por
unidad de un mismo producto), cuánto le toca a cada cuenta.

Ejemplo: si el pedido tiene 1 agua, 1 pancake y 1 hamburguesa,
se puede mandar el agua y el pancake a la Cuenta 1 y la
hamburguesa a la Cuenta 2 — como decida el cliente.

Cada cuenta resultante se cobra por separado, con su propio
método de pago, a través de punto_venta/panel_carrito.py.
------------------------------------------------------------
"""

import tkinter as tk
from tkinter import messagebox

from estilos import ROJO, ROJO_CLARO, BLANCO, CREMA, TEXTO, GRIS, BORDE, VERDE


class VentanaDividirCuenta(tk.Toplevel):

    def __init__(self, padre, carrito, al_confirmar):

        super().__init__(padre)

        self.padre = padre
        self.carrito = carrito
        self.al_confirmar = al_confirmar
        self.num_cuentas = 2

        self.title("Dividir Cuenta")
        self.configure(bg=BLANCO)
        self.resizable(False, False)
        self.transient(padre)
        self.grab_set()

        self._pedir_numero_cuentas()

    # --------------------------------------------------------
    def _centrar(self, ancho, alto):

        self.update_idletasks()

        x = self.padre.winfo_rootx() + (self.padre.winfo_width() - ancho) // 2
        y = self.padre.winfo_rooty() + (self.padre.winfo_height() - alto) // 2

        self.geometry(f"{ancho}x{alto}+{max(x, 0)}+{max(y, 0)}")

    # ========================================================
    # PASO 1: ¿CUÁNTAS CUENTAS?
    # ========================================================

    def _pedir_numero_cuentas(self):

        for widget in self.winfo_children():
            widget.destroy()

        tk.Label(
            self, text="¿En cuántas cuentas se divide?", font=("Segoe UI", 14, "bold"),
            fg=TEXTO, bg=BLANCO, wraplength=280, justify="center"
        ).pack(padx=25, pady=(25, 15))

        selector = tk.Frame(self, bg=BLANCO)
        selector.pack(pady=10)

        tk.Button(
            selector, text="−", font=("Segoe UI", 16, "bold"), width=3,
            relief="flat", bg=CREMA, cursor="hand2", command=self._restar_cuenta
        ).pack(side="left", padx=8)

        self.lbl_numero = tk.Label(
            selector, text=str(self.num_cuentas), font=("Segoe UI", 28, "bold"),
            fg=ROJO, bg=BLANCO, width=3
        )
        self.lbl_numero.pack(side="left", padx=15)

        tk.Button(
            selector, text="+", font=("Segoe UI", 16, "bold"), width=3,
            relief="flat", bg=CREMA, cursor="hand2", command=self._sumar_cuenta
        ).pack(side="left", padx=8)

        tk.Button(
            self, text="Continuar", font=("Segoe UI", 12, "bold"), bg=ROJO_CLARO,
            fg="white", activebackground=ROJO, activeforeground="white",
            relief="flat", cursor="hand2", command=self._pedir_asignacion
        ).pack(fill="x", padx=25, pady=(20, 25), ipady=8)

        self._centrar(340, 260)

    def _restar_cuenta(self):

        if self.num_cuentas > 2:
            self.num_cuentas -= 1
            self.lbl_numero.configure(text=str(self.num_cuentas))

    def _sumar_cuenta(self):

        if self.num_cuentas < 6:
            self.num_cuentas += 1
            self.lbl_numero.configure(text=str(self.num_cuentas))

    # ========================================================
    # PASO 2: ASIGNAR PRODUCTOS A CADA CUENTA
    # ========================================================

    def _pedir_asignacion(self):

        for widget in self.winfo_children():
            widget.destroy()

        # asignaciones[indice_del_producto][indice_de_cuenta] = unidades
        self.asignaciones = [[0] * self.num_cuentas for _ in self.carrito]

        # Por defecto, todo se manda a la Cuenta 1: el cajero solo
        # tiene que "mover" con las flechas lo que le toca a las
        # demás cuentas, en vez de repartir todo desde cero.
        for indice, item in enumerate(self.carrito):
            self.asignaciones[indice][0] = item["cantidad"]

        tk.Label(
            self, text="Asigna cada producto a una cuenta", font=("Segoe UI", 13, "bold"),
            fg=TEXTO, bg=BLANCO
        ).pack(anchor="w", padx=20, pady=(18, 2))

        tk.Label(
            self, text="Usa las flechas para mover unidades entre cuentas.",
            font=("Segoe UI", 9), fg=GRIS, bg=BLANCO
        ).pack(anchor="w", padx=20, pady=(0, 10))

        cuerpo = tk.Frame(self, bg=BLANCO)
        cuerpo.pack(fill="both", expand=True, padx=20)

        self.labels_cantidad = {}

        for indice, item in enumerate(self.carrito):

            fila = tk.Frame(cuerpo, bg=CREMA, highlightbackground=BORDE, highlightthickness=1)
            fila.pack(fill="x", pady=4)

            tk.Label(
                fila, text=f"{item['cantidad']}x {item['nombre']}", font=("Segoe UI", 10, "bold"),
                fg=TEXTO, bg=CREMA, anchor="w"
            ).pack(fill="x", padx=10, pady=(8, 4))

            fila_cuentas = tk.Frame(fila, bg=CREMA)
            fila_cuentas.pack(fill="x", padx=10, pady=(0, 8))

            for cuenta in range(self.num_cuentas):

                celda = tk.Frame(
                    fila_cuentas, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1
                )
                celda.pack(side="left", padx=3, fill="x", expand=True)

                tk.Label(
                    celda, text=f"Cuenta {cuenta + 1}", font=("Segoe UI", 8),
                    fg=GRIS, bg=BLANCO
                ).pack(pady=(4, 0))

                controles = tk.Frame(celda, bg=BLANCO)
                controles.pack(pady=(0, 4))

                tk.Button(
                    controles, text="−", font=("Segoe UI", 9, "bold"), width=2,
                    relief="flat", bg=CREMA, cursor="hand2",
                    command=lambda i=indice, c=cuenta: self._mover(i, c, -1)
                ).pack(side="left")

                etiqueta = tk.Label(
                    controles, text="0", font=("Segoe UI", 10, "bold"), width=2,
                    fg=ROJO, bg=BLANCO
                )
                etiqueta.pack(side="left", padx=4)
                self.labels_cantidad[(indice, cuenta)] = etiqueta

                tk.Button(
                    controles, text="+", font=("Segoe UI", 9, "bold"), width=2,
                    relief="flat", bg=CREMA, cursor="hand2",
                    command=lambda i=indice, c=cuenta: self._mover(i, c, 1)
                ).pack(side="left")

        self.lbl_estado = tk.Label(self, text="", font=("Segoe UI", 10, "bold"), bg=BLANCO)
        self.lbl_estado.pack(pady=(8, 0))

        botones = tk.Frame(self, bg=BLANCO)
        botones.pack(fill="x", padx=20, pady=18)

        tk.Button(
            botones, text="Cancelar", font=("Segoe UI", 11), bg=BLANCO,
            relief="solid", bd=1, cursor="hand2", command=self.destroy
        ).pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=8)

        tk.Button(
            botones, text="Confirmar división", font=("Segoe UI", 11, "bold"),
            bg=ROJO_CLARO, fg="white", activebackground=ROJO, activeforeground="white",
            relief="flat", cursor="hand2", command=self._confirmar
        ).pack(side="left", fill="x", expand=True, padx=(5, 0), ipady=8)

        self._refrescar_labels()
        self._centrar(580, min(700, 260 + 95 * len(self.carrito)))

    def _mover(self, indice_item, indice_cuenta, delta):

        actual = self.asignaciones[indice_item][indice_cuenta]
        nuevo = actual + delta

        if nuevo < 0:
            return

        total_item = self.carrito[indice_item]["cantidad"]
        asignado_en_otras_cuentas = sum(self.asignaciones[indice_item]) - actual

        if asignado_en_otras_cuentas + nuevo > total_item:
            return

        self.asignaciones[indice_item][indice_cuenta] = nuevo
        self._refrescar_labels()

    def _refrescar_labels(self):

        completo = True

        for indice, item in enumerate(self.carrito):

            for cuenta in range(self.num_cuentas):
                self.labels_cantidad[(indice, cuenta)].configure(
                    text=str(self.asignaciones[indice][cuenta])
                )

            if sum(self.asignaciones[indice]) != item["cantidad"]:
                completo = False

        if completo:
            self.lbl_estado.configure(text="✔  Todo asignado", fg=VERDE)
        else:
            self.lbl_estado.configure(text="Aún falta asignar productos", fg=ROJO)

    def _confirmar(self):

        for indice, item in enumerate(self.carrito):
            if sum(self.asignaciones[indice]) != item["cantidad"]:
                messagebox.showwarning(
                    "Mr.Burger", "Todavía hay productos sin asignar a una cuenta.",
                    parent=self
                )
                return

        cuentas = []

        for cuenta in range(self.num_cuentas):

            items_cuenta = []

            for indice, item in enumerate(self.carrito):

                cantidad = self.asignaciones[indice][cuenta]

                if cantidad > 0:
                    items_cuenta.append({
                        "id": item.get("id"),
                        "nombre": item["nombre"],
                        "precio": item["precio"],
                        "cantidad": cantidad,
                    })

            if items_cuenta:
                cuentas.append(items_cuenta)

        if len(cuentas) < 2:
            messagebox.showwarning(
                "Mr.Burger",
                "Asigna al menos un producto a más de una cuenta para poder dividir.",
                parent=self
            )
            return

        self.al_confirmar(cuentas)
        self.destroy()
