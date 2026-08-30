"""
vista_inventario.py
------------------------------------------------------------
Sección "Inventario" del Panel de Administrador: filtros,
tabla de productos y botones para agregar/editar/eliminar.
------------------------------------------------------------
"""

import tkinter as tk
from tkinter import ttk, messagebox

from estilos import (
    CREMA, BLANCO, TEXTO, GRIS, BORDE, ROJO, ROJO_CLARO,
    crear_encabezado, preparar_estilo_tabla
)
from panel_admin.dialogo_producto import DialogoProducto


class VistaInventario(tk.Frame):
    """'controlador' es la instancia de MenuAdministrador
    (panel_admin/app.py), que expone controlador.repo
    (RepositorioProductos)."""

    def __init__(self, parent, controlador):

        super().__init__(parent, bg=CREMA)

        self.controlador = controlador
        self.repo = controlador.repo

        self._crear_interfaz()

    # ========================================================
    def _crear_interfaz(self):

        crear_encabezado(
            self, "Inventario",
            "Gestiona productos, precios y existencias del catálogo"
        )

        # ----------------------------------------------------
        # BARRA DE FILTROS Y ACCIONES
        # ----------------------------------------------------

        barra = tk.Frame(self, bg=CREMA)
        barra.pack(fill="x", pady=(0, 12))

        tk.Label(
            barra, text="Categoría:", font=("Segoe UI", 10, "bold"),
            fg=TEXTO, bg=CREMA
        ).pack(side="left")

        self.combo_filtro_categoria = ttk.Combobox(
            barra, values=["todas"] + self.repo.categorias, state="readonly", width=14
        )
        self.combo_filtro_categoria.set(self.controlador.filtro_categoria)
        self.combo_filtro_categoria.pack(side="left", padx=(6, 18))
        self.combo_filtro_categoria.bind("<<ComboboxSelected>>", lambda e: self._filtrar())

        tk.Label(
            barra, text="Periodo:", font=("Segoe UI", 10, "bold"),
            fg=TEXTO, bg=CREMA
        ).pack(side="left")

        self.combo_filtro_periodo = ttk.Combobox(
            barra, values=["todos"] + ["desayuno", "almuerzo"], state="readonly", width=12
        )
        self.combo_filtro_periodo.set(self.controlador.filtro_periodo)
        self.combo_filtro_periodo.pack(side="left", padx=(6, 18))
        self.combo_filtro_periodo.bind("<<ComboboxSelected>>", lambda e: self._filtrar())

        self.entry_buscar_producto = tk.Entry(
            barra, font=("Segoe UI", 10), width=24, bd=1, relief="solid"
        )
        self.entry_buscar_producto.pack(side="left", ipady=4, padx=(0, 18))
        self.entry_buscar_producto.insert(0, "Buscar producto...")
        self.entry_buscar_producto.bind("<KeyRelease>", lambda e: self._filtrar())

        tk.Button(
            barra, text="+ Agregar Producto", font=("Segoe UI", 10, "bold"),
            bg=ROJO_CLARO, fg="white", relief="flat",
            activebackground=ROJO, activeforeground="white",
            command=self._agregar_producto, cursor="hand2"
        ).pack(side="right", ipady=5, ipadx=8)

        # ----------------------------------------------------
        # TABLA DE PRODUCTOS
        # ----------------------------------------------------

        preparar_estilo_tabla(self)

        marco_tabla = tk.Frame(self, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
        marco_tabla.pack(fill="both", expand=True)

        columnas = ("emoji", "nombre", "categoria", "periodo", "precio", "stock")

        self.tabla_inventario = ttk.Treeview(
            marco_tabla, columns=columnas, show="headings",
            style="Mr.Treeview", selectmode="browse"
        )

        titulos = {
            "emoji": "", "nombre": "Producto", "categoria": "Categoría",
            "periodo": "Periodo", "precio": "Precio", "stock": "Stock"
        }
        anchos = {
            "emoji": 40, "nombre": 260, "categoria": 130,
            "periodo": 110, "precio": 100, "stock": 100
        }

        for col in columnas:
            self.tabla_inventario.heading(col, text=titulos[col])
            self.tabla_inventario.column(
                col, width=anchos[col], anchor="center" if col != "nombre" else "w"
            )

        scroll = ttk.Scrollbar(marco_tabla, orient="vertical", command=self.tabla_inventario.yview)
        self.tabla_inventario.configure(yscrollcommand=scroll.set)

        self.tabla_inventario.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.tabla_inventario.bind("<Double-1>", lambda e: self._editar_producto())

        # ----------------------------------------------------
        # BOTONES DE ACCIÓN SOBRE LA TABLA
        # ----------------------------------------------------

        acciones = tk.Frame(self, bg=CREMA)
        acciones.pack(fill="x", pady=(10, 0))

        tk.Button(
            acciones, text="✎ Editar Seleccionado", font=("Segoe UI", 10),
            bg=BLANCO, relief="solid", bd=1, cursor="hand2",
            command=self._editar_producto
        ).pack(side="left", ipady=6, ipadx=8, padx=(0, 8))

        tk.Button(
            acciones, text="🗑 Eliminar Seleccionado", font=("Segoe UI", 10),
            bg=BLANCO, fg=ROJO, relief="solid", bd=1, cursor="hand2",
            command=self._eliminar_producto
        ).pack(side="left", ipady=6, ipadx=8)

        self._filtrar()

    # ========================================================
    def _filtrar(self):

        for fila in self.tabla_inventario.get_children():
            self.tabla_inventario.delete(fila)

        categoria = self.combo_filtro_categoria.get()
        periodo = self.combo_filtro_periodo.get()
        busqueda = self.entry_buscar_producto.get().strip().lower()

        if busqueda == "buscar producto...":
            busqueda = ""

        self.controlador.filtro_categoria = categoria
        self.controlador.filtro_periodo = periodo

        for producto in self.repo.listar_productos(categoria, periodo, busqueda):

            stock = producto.get("stock")

            self.tabla_inventario.insert(
                "", "end", iid=str(producto["id"]),
                values=(
                    producto.get("emoji", ""),
                    producto["nombre"].replace("\n", " "),
                    producto["categoria"].capitalize(),
                    producto["periodo"].capitalize(),
                    f"Q{producto['precio']:.2f}",
                    stock if stock is not None else "—"
                )
            )

    # ========================================================
    def _producto_seleccionado(self):

        seleccion = self.tabla_inventario.selection()

        if not seleccion:
            messagebox.showinfo("Mr.Burger", "Selecciona un producto de la tabla.")
            return None

        return self.repo.buscar_producto_por_id(int(seleccion[0]))

    # ========================================================
    def _agregar_producto(self):

        DialogoProducto(self, self.repo.categorias, None, self._guardar_producto_nuevo)

    def _guardar_producto_nuevo(self, valores):

        try:
            self.repo.agregar_producto(valores)
        except Exception as error:
            messagebox.showerror("Mr.Burger", str(error))
            return

        self._filtrar()

    # ========================================================
    def _editar_producto(self):

        producto = self._producto_seleccionado()

        if producto is None:
            return

        DialogoProducto(self, self.repo.categorias, producto, self._guardar_producto_editado)

    def _guardar_producto_editado(self, valores):

        try:
            self.repo.actualizar_producto(valores["id"], valores)
        except Exception as error:
            messagebox.showerror("Mr.Burger", str(error))
            return

        self._filtrar()

    # ========================================================
    def _eliminar_producto(self):

        producto = self._producto_seleccionado()

        if producto is None:
            return

        nombre = producto["nombre"].replace("\n", " ")

        confirmar = messagebox.askyesno(
            "Eliminar producto",
            f"¿Deseas eliminar \"{nombre}\" del inventario?\n"
            "Esta acción no se puede deshacer."
        )

        if not confirmar:
            return

        try:
            self.repo.eliminar_producto(producto["id"])
        except Exception as error:
            messagebox.showerror("Mr.Burger", str(error))
            return

        self._filtrar()
