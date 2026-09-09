"""
vista_categorias.py
------------------------------------------------------------
Sección "Categorías" del Panel de Administrador.
------------------------------------------------------------
"""

import tkinter as tk
from tkinter import ttk, messagebox

from estilos import CREMA, BLANCO, TEXTO, BORDE, ROJO, ROJO_CLARO, crear_encabezado, preparar_estilo_tabla


class VistaCategorias(tk.Frame):

    def __init__(self, parent, controlador):

        super().__init__(parent, bg=CREMA)

        self.controlador = controlador
        self.repo = controlador.repo

        self._crear_interfaz()

    # ========================================================
    def _crear_interfaz(self):

        crear_encabezado(self, "Categorías", "Organiza los productos del menú por categoría")

        barra = tk.Frame(self, bg=CREMA)
        barra.pack(fill="x", pady=(0, 12))

        tk.Button(
            barra, text="+ Agregar Categoría", font=("Segoe UI", 10, "bold"),
            bg=ROJO_CLARO, fg="white", relief="flat",
            activebackground=ROJO, activeforeground="white",
            command=self._agregar_categoria, cursor="hand2"
        ).pack(side="right", ipady=5, ipadx=8)

        preparar_estilo_tabla(self)

        marco_tabla = tk.Frame(self, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
        marco_tabla.pack(fill="both", expand=True)

        columnas = ("icono", "categoria", "cantidad")

        self.tabla_categorias = ttk.Treeview(
            marco_tabla, columns=columnas, show="headings",
            style="Mr.Treeview", selectmode="browse"
        )

        self.tabla_categorias.heading("icono", text="")
        self.tabla_categorias.heading("categoria", text="Categoría")
        self.tabla_categorias.heading("cantidad", text="Nº de productos")

        self.tabla_categorias.column("icono", width=50, anchor="center")
        self.tabla_categorias.column("categoria", width=260, anchor="w")
        self.tabla_categorias.column("cantidad", width=150, anchor="center")

        self.tabla_categorias.pack(side="left", fill="both", expand=True)

        acciones = tk.Frame(self, bg=CREMA)
        acciones.pack(fill="x", pady=(10, 0))

        tk.Button(
            acciones, text="🗑 Eliminar Categoría", font=("Segoe UI", 10),
            bg=BLANCO, fg=ROJO, relief="solid", bd=1, cursor="hand2",
            command=self._eliminar_categoria
        ).pack(side="left", ipady=6, ipadx=8)

        self._llenar_tabla()

    # ========================================================
    def _llenar_tabla(self):

        for fila in self.tabla_categorias.get_children():
            self.tabla_categorias.delete(fila)

        for categoria in self.repo.categorias:

            self.tabla_categorias.insert(
                "", "end", iid=categoria,
                values=(
                    self.repo.icono_categoria(categoria),
                    categoria.capitalize(),
                    self.repo.cantidad_por_categoria(categoria)
                )
            )

    # ========================================================
    def _agregar_categoria(self):

        ventana = tk.Toplevel(self)
        ventana.title("Agregar Categoría")
        ventana.configure(bg=BLANCO)
        ventana.geometry("360x180")
        ventana.resizable(False, False)
        ventana.transient(self)
        ventana.grab_set()

        tk.Label(
            ventana, text="Nombre de la nueva categoría",
            font=("Segoe UI", 11, "bold"), fg=TEXTO, bg=BLANCO
        ).pack(padx=20, pady=(20, 6), anchor="w")

        entrada = tk.Entry(ventana, font=("Segoe UI", 12), bd=1, relief="solid")
        entrada.pack(padx=20, fill="x", ipady=6)
        entrada.focus_set()

        def guardar():

            ok, error = self.repo.agregar_categoria(entrada.get())

            if not ok:
                messagebox.showwarning("Mr.Burger", error, parent=ventana)
                return

            ventana.destroy()
            self._llenar_tabla()

        tk.Button(
            ventana, text="Guardar Categoría", font=("Segoe UI", 11, "bold"),
            bg=ROJO_CLARO, fg="white", relief="flat",
            activebackground=ROJO, activeforeground="white",
            command=guardar
        ).pack(padx=20, pady=20, fill="x", ipady=8)

    # ========================================================
    def _eliminar_categoria(self):

        seleccion = self.tabla_categorias.selection()

        if not seleccion:
            messagebox.showinfo("Mr.Burger", "Selecciona una categoría de la tabla.")
            return

        categoria = seleccion[0]

        en_uso = [p for p in self.repo.productos if p["categoria"] == categoria]

        if en_uso:
            messagebox.showwarning(
                "No se puede eliminar",
                f"La categoría \"{categoria}\" tiene {len(en_uso)} producto(s) "
                "asociado(s). Elimina o reasigna esos productos primero."
            )
            return

        confirmar = messagebox.askyesno(
            "Eliminar categoría", f"¿Deseas eliminar la categoría \"{categoria}\"?"
        )

        if not confirmar:
            return

        self.repo.eliminar_categoria(categoria)
        self._llenar_tabla()
