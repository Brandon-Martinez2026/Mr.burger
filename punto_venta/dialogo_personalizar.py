"""
dialogo_personalizar.py
------------------------------------------------------------
Ventana que se abre al hacer clic sobre un producto ya agregado
en el carrito (panel derecho del Punto de Venta), para poder
quitarle ingredientes (por ejemplo "sin tomate") o agregarle una
instrucción especial antes de mandarlo a cocina.

Los ingredientes que se muestran vienen de punto_venta/ingredientes.py,
que por ahora es solo una lista de respaldo (ver ese archivo para
más detalle) mientras la base de datos tiene su propia tabla.
------------------------------------------------------------
"""

import tkinter as tk

from estilos import ROJO, ROJO_CLARO, BLANCO, TEXTO, GRIS, crear_area_desplazable
from punto_venta import ingredientes as _ingredientes


class DialogoPersonalizar(tk.Toplevel):
    """'item' es el diccionario de la línea del carrito (ver
    PanelCarrito.agregar_producto). 'al_guardar' se llama con
    (lista_de_ingredientes_quitados, instrucciones_texto) cuando el
    cajero confirma los cambios; si cancela, no se llama a nada."""

    def __init__(self, padre, item, al_guardar):

        super().__init__(padre)

        self.al_guardar = al_guardar
        self.item = item

        self.title("Personalizar producto")
        self.configure(bg=BLANCO)
        self.geometry("380x540")
        self.minsize(340, 340)
        self.transient(padre)
        self.grab_set()

        self._lista_ingredientes = _ingredientes.obtener_ingredientes_editables(item)
        self._variables = {}

        self._crear_interfaz()

    # ========================================================
    # INTERFAZ
    # ========================================================

    def _crear_interfaz(self):

        tk.Label(
            self, text=self.item["nombre"], font=("Segoe UI", 15, "bold"),
            fg=ROJO, bg=BLANCO, wraplength=330, justify="left"
        ).pack(anchor="w", padx=20, pady=(18, 2))

        tk.Label(
            self, text=f"{self.item['cantidad']}x  ·  Q{self.item['precio']:.2f} c/u",
            font=("Segoe UI", 10), fg=GRIS, bg=BLANCO
        ).pack(anchor="w", padx=20, pady=(0, 12))

        # ----------------------------------------------------
        # INGREDIENTES (desmarcar = quitárselo al producto)
        # ----------------------------------------------------

        if self._lista_ingredientes:

            tk.Label(
                self, text="Ingredientes", font=("Segoe UI", 11, "bold"),
                fg=TEXTO, bg=BLANCO
            ).pack(anchor="w", padx=20)

            tk.Label(
                self, text="Desmarca lo que el cliente no quiere.",
                font=("Segoe UI", 9), fg=GRIS, bg=BLANCO
            ).pack(anchor="w", padx=20, pady=(0, 6))

            # Con scroll por si algún producto llega a tener muchos
            # ingredientes registrados y no caben todos de una vez.
            contenedor, interior = crear_area_desplazable(self, bg=BLANCO)
            contenedor.pack(fill="both", expand=True, padx=15, pady=(0, 10))

            quitados_actuales = set(self.item.get("ingredientes_quitados") or [])

            for ingrediente in self._lista_ingredientes:

                var = tk.BooleanVar(value=ingrediente not in quitados_actuales)
                self._variables[ingrediente] = var

                tk.Checkbutton(
                    interior, text=ingrediente, variable=var,
                    font=("Segoe UI", 11), fg=TEXTO, bg=BLANCO,
                    activebackground=BLANCO, selectcolor=BLANCO,
                    anchor="w", cursor="hand2"
                ).pack(fill="x", padx=5, pady=3)

        else:

            tk.Label(
                self,
                text=(
                    "Este producto todavía no tiene ingredientes "
                    "configurados para personalizar."
                ),
                font=("Segoe UI", 10), fg=GRIS, bg=BLANCO, wraplength=330,
                justify="left"
            ).pack(anchor="w", padx=20, pady=(4, 10))

        # ----------------------------------------------------
        # INSTRUCCIONES ESPECIALES
        # ----------------------------------------------------

        tk.Label(
            self, text="Instrucciones especiales (opcional)",
            font=("Segoe UI", 11, "bold"), fg=TEXTO, bg=BLANCO
        ).pack(anchor="w", padx=20, pady=(6, 4))

        self.entrada_instrucciones = tk.Text(
            self, height=3, font=("Segoe UI", 10), fg=TEXTO, bd=1, relief="solid"
        )
        self.entrada_instrucciones.insert("1.0", self.item.get("instrucciones", ""))
        self.entrada_instrucciones.pack(fill="x", padx=20, pady=(0, 15))

        # ----------------------------------------------------
        # BOTONES
        # ----------------------------------------------------

        botones = tk.Frame(self, bg=BLANCO)
        botones.pack(fill="x", padx=20, pady=(0, 18), side="bottom")

        tk.Button(
            botones, text="Cancelar", font=("Segoe UI", 11), bg=BLANCO,
            relief="solid", bd=1, command=self.destroy
        ).pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=8)

        tk.Button(
            botones, text="Guardar", font=("Segoe UI", 11, "bold"),
            bg=ROJO_CLARO, fg="white", relief="flat",
            activebackground=ROJO, activeforeground="white",
            command=self._guardar
        ).pack(side="left", fill="x", expand=True, padx=(5, 0), ipady=8)

    # ========================================================
    # GUARDAR
    # ========================================================

    def _guardar(self):

        quitados = [
            ingrediente for ingrediente, var in self._variables.items()
            if not var.get()
        ]

        instrucciones = self.entrada_instrucciones.get("1.0", "end").strip()

        self.al_guardar(quitados, instrucciones)
        self.destroy()
