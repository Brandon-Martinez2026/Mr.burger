"""
vista_comprar.py
------------------------------------------------------------
Sección "Comprar Productos" del Panel de Administrador: permite
armar una orden de compra (producto + cantidad + costo unitario)
a un proveedor y registrarla. Cada línea aumenta el stock real
del producto (ver sp_agregar_producto_compra en
migraciones/003_cocina_y_compras.sql).
------------------------------------------------------------
"""

import tkinter as tk
from tkinter import ttk, messagebox

from estilos import (
    ROJO, ROJO_CLARO, CREMA, BLANCO, TEXTO, GRIS, BORDE, VERDE,
    crear_encabezado, preparar_estilo_tabla
)

from basedatos import repositorio_compras
from basedatos.conexion import ErrorBaseDatos

from panel_admin.dialogo_compra import DialogoCantidadCompra


class VistaComprar(tk.Frame):

    def __init__(self, parent, controlador):

        super().__init__(parent, bg=CREMA)

        self.controlador = controlador
        self.repo = controlador.repo

        # Líneas de la orden de compra en curso (todavía no
        # guardada): [{"id_producto","nombre","cantidad","costo_unitario"}]
        self.carrito_compra = []

        self._crear_interfaz()

    # ========================================================
    def _crear_interfaz(self):

        crear_encabezado(
            self, "Comprar Productos",
            "Registra compras a proveedores y reabastece el inventario"
        )

        cuerpo = tk.Frame(self, bg=CREMA)
        cuerpo.pack(fill="both", expand=True)

        self._crear_catalogo(cuerpo)
        self._crear_orden_compra(cuerpo)

    # --------------------------------------------------------
    # CATÁLOGO (izquierda): productos disponibles para comprar
    # --------------------------------------------------------

    def _crear_catalogo(self, cuerpo):

        izquierda = tk.Frame(cuerpo, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
        izquierda.pack(side="left", fill="both", expand=True, padx=(0, 15))

        barra = tk.Frame(izquierda, bg=BLANCO)
        barra.pack(fill="x", padx=12, pady=10)

        tk.Label(
            barra, text="Buscar producto:", font=("Segoe UI", 10, "bold"),
            fg=TEXTO, bg=BLANCO
        ).pack(side="left")

        self.entry_buscar = tk.Entry(barra, font=("Segoe UI", 10), bd=1, relief="solid")
        self.entry_buscar.pack(side="left", padx=(8, 0), fill="x", expand=True, ipady=4)
        self.entry_buscar.bind("<KeyRelease>", lambda e: self._filtrar())

        preparar_estilo_tabla(self)

        marco_tabla = tk.Frame(izquierda, bg=BLANCO)
        marco_tabla.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        columnas = ("emoji", "nombre", "categoria", "stock")

        self.tabla_productos = ttk.Treeview(
            marco_tabla, columns=columnas, show="headings",
            style="Mr.Treeview", selectmode="browse"
        )

        titulos = {"emoji": "", "nombre": "Producto", "categoria": "Categoría", "stock": "Stock actual"}
        anchos = {"emoji": 40, "nombre": 220, "categoria": 130, "stock": 100}

        for col in columnas:
            self.tabla_productos.heading(col, text=titulos[col])
            self.tabla_productos.column(col, width=anchos[col], anchor="center" if col != "nombre" else "w")

        scroll = ttk.Scrollbar(marco_tabla, orient="vertical", command=self.tabla_productos.yview)
        self.tabla_productos.configure(yscrollcommand=scroll.set)

        self.tabla_productos.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.tabla_productos.bind("<Double-1>", lambda e: self._agregar_a_compra())

        tk.Button(
            izquierda, text="+ Agregar Cantidad a Comprar", font=("Segoe UI", 10, "bold"),
            bg=ROJO_CLARO, fg="white", relief="flat",
            activebackground=ROJO, activeforeground="white",
            command=self._agregar_a_compra, cursor="hand2"
        ).pack(fill="x", padx=12, pady=(0, 12), ipady=6)

        self._filtrar()

    def _filtrar(self):

        for fila in self.tabla_productos.get_children():
            self.tabla_productos.delete(fila)

        busqueda = self.entry_buscar.get().strip().lower()

        for producto in self.repo.productos:

            nombre_plano = producto["nombre"].replace("\n", " ")

            if busqueda and busqueda not in nombre_plano.lower():
                continue

            self.tabla_productos.insert(
                "", "end", iid=str(producto["id"]),
                values=(
                    producto.get("emoji", ""), nombre_plano,
                    producto["categoria"].capitalize(), producto.get("stock", 0)
                )
            )

    def _producto_seleccionado(self):

        seleccion = self.tabla_productos.selection()

        if not seleccion:
            messagebox.showinfo("Mr.Burger", "Selecciona un producto de la lista.")
            return None

        return self.repo.buscar_producto_por_id(int(seleccion[0]))

    def _agregar_a_compra(self):

        producto = self._producto_seleccionado()

        if producto is None:
            return

        DialogoCantidadCompra(self.controlador, producto, self._agregar_linea)

    # --------------------------------------------------------
    # ORDEN DE COMPRA (derecha): carrito + proveedor + registrar
    # --------------------------------------------------------

    def _crear_orden_compra(self, cuerpo):

        derecha = tk.Frame(cuerpo, bg=BLANCO, width=380, highlightbackground=BORDE, highlightthickness=1)
        derecha.pack(side="left", fill="y")
        derecha.pack_propagate(False)

        tk.Label(
            derecha, text="Orden de Compra", font=("Segoe UI", 14, "bold"),
            fg=TEXTO, bg=BLANCO
        ).pack(anchor="w", padx=18, pady=(15, 10))

        tk.Label(
            derecha, text="Proveedor (opcional)", font=("Segoe UI", 9, "bold"),
            fg=TEXTO, bg=BLANCO
        ).pack(anchor="w", padx=18)

        self.entry_proveedor = tk.Entry(derecha, font=("Segoe UI", 10), bd=1, relief="solid")
        self.entry_proveedor.pack(fill="x", padx=18, pady=(2, 10), ipady=4)

        self.lista_carrito = tk.Frame(derecha, bg=BLANCO)
        self.lista_carrito.pack(fill="both", expand=True, padx=18)

        self.lbl_total = tk.Label(
            derecha, text="Total: Q0.00", font=("Segoe UI", 13, "bold"),
            fg=TEXTO, bg=BLANCO
        )
        self.lbl_total.pack(anchor="e", padx=18, pady=10)

        tk.Label(
            derecha, text="Notas (opcional)", font=("Segoe UI", 9, "bold"),
            fg=TEXTO, bg=BLANCO
        ).pack(anchor="w", padx=18)

        self.entry_notas = tk.Entry(derecha, font=("Segoe UI", 10), bd=1, relief="solid")
        self.entry_notas.pack(fill="x", padx=18, pady=(2, 15), ipady=4)

        tk.Button(
            derecha, text="Registrar Compra", font=("Segoe UI", 12, "bold"),
            bg=VERDE, fg="white", relief="flat",
            activebackground="#3E8E41", activeforeground="white",
            command=self._registrar_compra, cursor="hand2"
        ).pack(fill="x", padx=18, pady=(0, 18), ipady=8)

        self._actualizar_carrito()

    def _agregar_linea(self, id_producto, nombre, cantidad, costo_unitario):

        self.carrito_compra.append({
            "id_producto": id_producto,
            "nombre": nombre,
            "cantidad": cantidad,
            "costo_unitario": costo_unitario
        })

        self._actualizar_carrito()

    def _quitar_linea(self, indice):

        del self.carrito_compra[indice]
        self._actualizar_carrito()

    def _actualizar_carrito(self):

        for widget in self.lista_carrito.winfo_children():
            widget.destroy()

        if not self.carrito_compra:

            tk.Label(
                self.lista_carrito, text="Todavía no agregaste productos.",
                font=("Segoe UI", 10), fg=GRIS, bg=BLANCO
            ).pack(pady=10)

            self.lbl_total.configure(text="Total: Q0.00")
            return

        total = 0

        for indice, linea in enumerate(self.carrito_compra):

            subtotal = linea["cantidad"] * linea["costo_unitario"]
            total += subtotal

            fila = tk.Frame(self.lista_carrito, bg=BLANCO)
            fila.pack(fill="x", pady=6)

            tk.Button(
                fila, text="✕", font=("Segoe UI", 9), fg=ROJO, bg=BLANCO, bd=0,
                cursor="hand2", command=lambda i=indice: self._quitar_linea(i)
            ).pack(side="right", padx=(6, 0))

            tk.Label(
                fila, text=f"Q{subtotal:.2f}", font=("Segoe UI", 10, "bold"),
                fg=TEXTO, bg=BLANCO
            ).pack(side="right")

            tk.Label(
                fila, text=f"{linea['cantidad']}x {linea['nombre']}",
                font=("Segoe UI", 10), fg=TEXTO, bg=BLANCO, anchor="w"
            ).pack(side="left", fill="x", expand=True)

        self.lbl_total.configure(text=f"Total: Q{total:.2f}")

    def _registrar_compra(self):

        if not self.carrito_compra:
            messagebox.showwarning("Mr.Burger", "Agrega al menos un producto a la compra.")
            return

        compra = {
            "id_usuario": getattr(self.controlador, "id_usuario", None),
            "proveedor": self.entry_proveedor.get().strip() or None,
            "notas": self.entry_notas.get().strip() or None,
            "items": [
                {
                    "id_producto": linea["id_producto"],
                    "cantidad": linea["cantidad"],
                    "costo_unitario": linea["costo_unitario"]
                }
                for linea in self.carrito_compra
            ],
        }

        try:
            repositorio_compras.registrar_compra(compra)
        except ErrorBaseDatos as error:
            messagebox.showerror("No se pudo registrar la compra", str(error))
            return

        messagebox.showinfo(
            "Mr.Burger",
            "Compra registrada correctamente. El inventario ya se actualizó."
        )

        self.carrito_compra.clear()
        self._actualizar_carrito()

        self.entry_proveedor.delete(0, tk.END)
        self.entry_notas.delete(0, tk.END)

        # El stock mostrado en la tabla de la izquierda ya cambió
        # (se acaba de reabastecer), así que se refresca.
        self._filtrar()
