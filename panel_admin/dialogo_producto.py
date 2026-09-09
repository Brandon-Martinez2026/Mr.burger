"""
dialogo_producto.py
------------------------------------------------------------
Formulario para crear un producto nuevo o editar uno existente
dentro del inventario del Panel de Administrador.
------------------------------------------------------------
"""

import tkinter as tk
from tkinter import ttk, messagebox

from estilos import ROJO, ROJO_CLARO, BLANCO, TEXTO
from panel_admin.datos_admin import PERIODOS


class DialogoProducto(tk.Toplevel):
    """Formulario para crear un producto nuevo o editar uno
    existente. Si 'producto' es None, se está creando uno nuevo;
    si no, se editan sus valores directamente."""

    def __init__(self, padre, categorias, producto, al_guardar):

        super().__init__(padre)

        self.padre = padre
        self.categorias = categorias
        self.producto = producto
        self.al_guardar = al_guardar

        self.title("Editar Producto" if producto else "Agregar Producto")
        self.configure(bg=BLANCO)
        self.geometry("420x560")
        self.resizable(False, False)
        self.transient(padre)
        self.grab_set()

        self._crear_interfaz()

    def _campo(self, etiqueta):

        tk.Label(
            self, text=etiqueta, font=("Segoe UI", 10, "bold"),
            fg=TEXTO, bg=BLANCO
        ).pack(anchor="w", padx=22, pady=(12, 3))

    def _crear_interfaz(self):

        tk.Label(
            self,
            text="Editar Producto" if self.producto else "Nuevo Producto",
            font=("Segoe UI", 16, "bold"), fg=ROJO, bg=BLANCO
        ).pack(anchor="w", padx=22, pady=(18, 0))

        # Nombre
        self._campo("Nombre")
        self.entry_nombre = tk.Entry(self, font=("Segoe UI", 11), bd=1, relief="solid")
        self.entry_nombre.pack(padx=22, fill="x", ipady=6)

        # Descripción
        self._campo("Descripción (opcional)")
        self.entry_descripcion = tk.Entry(self, font=("Segoe UI", 11), bd=1, relief="solid")
        self.entry_descripcion.pack(padx=22, fill="x", ipady=6)

        # Emoji
        self._campo("Emoji / ícono")
        self.entry_emoji = tk.Entry(self, font=("Segoe UI", 11), bd=1, relief="solid")
        self.entry_emoji.pack(padx=22, fill="x", ipady=6)

        fila_precio_stock = tk.Frame(self, bg=BLANCO)
        fila_precio_stock.pack(fill="x", padx=22, pady=(12, 0))

        col_precio = tk.Frame(fila_precio_stock, bg=BLANCO)
        col_precio.pack(side="left", fill="x", expand=True, padx=(0, 6))

        tk.Label(col_precio, text="Precio (Q)", font=("Segoe UI", 10, "bold"), fg=TEXTO, bg=BLANCO).pack(anchor="w")
        self.entry_precio = tk.Entry(col_precio, font=("Segoe UI", 11), bd=1, relief="solid")
        self.entry_precio.pack(fill="x", ipady=6, pady=(3, 0))

        col_stock = tk.Frame(fila_precio_stock, bg=BLANCO)
        col_stock.pack(side="left", fill="x", expand=True, padx=(6, 0))

        tk.Label(col_stock, text="Stock", font=("Segoe UI", 10, "bold"), fg=TEXTO, bg=BLANCO).pack(anchor="w")
        self.entry_stock = tk.Entry(col_stock, font=("Segoe UI", 11), bd=1, relief="solid")
        self.entry_stock.pack(fill="x", ipady=6, pady=(3, 0))

        fila_cat_periodo = tk.Frame(self, bg=BLANCO)
        fila_cat_periodo.pack(fill="x", padx=22, pady=(12, 0))

        col_cat = tk.Frame(fila_cat_periodo, bg=BLANCO)
        col_cat.pack(side="left", fill="x", expand=True, padx=(0, 6))

        tk.Label(col_cat, text="Categoría", font=("Segoe UI", 10, "bold"), fg=TEXTO, bg=BLANCO).pack(anchor="w")
        self.combo_categoria = ttk.Combobox(col_cat, values=self.categorias, state="readonly")
        self.combo_categoria.pack(fill="x", ipady=4, pady=(3, 0))

        col_periodo = tk.Frame(fila_cat_periodo, bg=BLANCO)
        col_periodo.pack(side="left", fill="x", expand=True, padx=(6, 0))

        tk.Label(col_periodo, text="Periodo", font=("Segoe UI", 10, "bold"), fg=TEXTO, bg=BLANCO).pack(anchor="w")
        self.combo_periodo = ttk.Combobox(col_periodo, values=PERIODOS, state="readonly")
        self.combo_periodo.pack(fill="x", ipady=4, pady=(3, 0))

        # ----------------------------------------------------
        # Precargar valores si se está editando
        # ----------------------------------------------------

        if self.producto:

            self.entry_nombre.insert(0, self.producto["nombre"].replace("\n", " "))
            self.entry_descripcion.insert(0, self.producto.get("descripcion", "").replace("\n", " "))
            self.entry_emoji.insert(0, self.producto.get("emoji", ""))
            self.entry_precio.insert(0, str(self.producto["precio"]))
            self.entry_stock.insert(0, str(self.producto.get("stock", 0)))
            self.combo_categoria.set(self.producto["categoria"])
            self.combo_periodo.set(self.producto["periodo"])

        else:

            self.combo_categoria.set(self.categorias[0] if self.categorias else "")
            self.combo_periodo.set(PERIODOS[0])
            self.entry_emoji.insert(0, "🍽")
            self.entry_stock.insert(0, "10")

        # ----------------------------------------------------
        # BOTONES
        # ----------------------------------------------------

        botones = tk.Frame(self, bg=BLANCO)
        botones.pack(fill="x", padx=22, pady=22, side="bottom")

        tk.Button(
            botones, text="Cancelar", font=("Segoe UI", 11), bg=BLANCO,
            relief="solid", bd=1, command=self.destroy
        ).pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=9)

        tk.Button(
            botones, text="Guardar", font=("Segoe UI", 11, "bold"),
            bg=ROJO_CLARO, fg="white", relief="flat",
            activebackground=ROJO, activeforeground="white",
            command=self._guardar
        ).pack(side="left", fill="x", expand=True, padx=(5, 0), ipady=9)

    def _guardar(self):

        nombre = self.entry_nombre.get().strip()

        if not nombre:
            messagebox.showwarning("Mr.Burger", "Ingresa el nombre del producto.", parent=self)
            return

        try:
            precio = float(self.entry_precio.get())
        except ValueError:
            messagebox.showwarning("Mr.Burger", "Ingresa un precio válido.", parent=self)
            return

        try:
            stock = int(self.entry_stock.get())
        except ValueError:
            messagebox.showwarning("Mr.Burger", "Ingresa un stock válido (número entero).", parent=self)
            return

        categoria = self.combo_categoria.get()
        periodo = self.combo_periodo.get()

        if not categoria or not periodo:
            messagebox.showwarning("Mr.Burger", "Selecciona categoría y periodo.", parent=self)
            return

        if self.producto is not None:

            # Editar en el mismo diccionario para que la referencia
            # dentro del repositorio quede actualizada.
            self.producto["nombre"] = nombre
            self.producto["descripcion"] = self.entry_descripcion.get().strip()
            self.producto["emoji"] = self.entry_emoji.get().strip() or "🍽"
            self.producto["precio"] = precio
            self.producto["stock"] = stock
            self.producto["categoria"] = categoria
            self.producto["periodo"] = periodo

            self.al_guardar(self.producto)

        else:

            nuevo = {
                "nombre": nombre,
                "descripcion": self.entry_descripcion.get().strip(),
                "emoji": self.entry_emoji.get().strip() or "🍽",
                "precio": precio,
                "stock": stock,
                "categoria": categoria,
                "periodo": periodo
            }

            self.al_guardar(nuevo)

        self.destroy()
