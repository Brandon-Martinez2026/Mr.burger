"""
vista_cajeros.py
------------------------------------------------------------
Sección "Cajeros" del Panel de Administrador: supervisa las
ventas realizadas por cada cajero.
------------------------------------------------------------
"""

import tkinter as tk
from tkinter import ttk, messagebox

from estilos import CREMA, BLANCO, TEXTO, GRIS, BORDE, ROJO, ROJO_CLARO, crear_encabezado, preparar_estilo_tabla
from panel_admin.datos_admin import METODOS_PAGO
from panel_admin.dialogo_detalle_venta import mostrar_detalle_venta
from basedatos.repositorio_usuarios import crear_usuario

import datos_ventas


class VistaCajeros(tk.Frame):

    def __init__(self, parent, controlador):

        super().__init__(parent, bg=CREMA)

        self.controlador = controlador

        self._crear_interfaz()

    # ========================================================
    def _crear_interfaz(self):

        encabezado = crear_encabezado(self, "Cajeros", "Supervisa las ventas realizadas por cada cajero")

        tk.Button(
            encabezado, text="+ Crear Cajero / Cocinero", font=("Segoe UI", 10, "bold"),
            bg=ROJO_CLARO, fg="white", relief="flat", bd=0, cursor="hand2",
            activebackground=ROJO, activeforeground="white",
            command=self._crear_personal
        ).pack(side="right", padx=(15, 0), ipady=6, ipadx=10)

        cuerpo = tk.Frame(self, bg=CREMA)
        cuerpo.pack(fill="both", expand=True)

        # ----------------------------------------------------
        # LISTA DE CAJEROS (izquierda)
        # ----------------------------------------------------

        izquierda = tk.Frame(cuerpo, bg=BLANCO, width=380, highlightbackground=BORDE, highlightthickness=1)
        izquierda.pack(side="left", fill="y", padx=(0, 15))
        izquierda.pack_propagate(False)

        preparar_estilo_tabla(self)

        columnas = ("cajero", "ventas", "total")

        self.tabla_cajeros = ttk.Treeview(
            izquierda, columns=columnas, show="headings",
            style="Mr.Treeview", selectmode="browse"
        )

        self.tabla_cajeros.heading("cajero", text="Cajero")
        self.tabla_cajeros.heading("ventas", text="Nº Ventas")
        self.tabla_cajeros.heading("total", text="Total Vendido")

        self.tabla_cajeros.column("cajero", width=150, anchor="w")
        self.tabla_cajeros.column("ventas", width=90, anchor="center")
        self.tabla_cajeros.column("total", width=120, anchor="e")

        self.tabla_cajeros.pack(fill="both", expand=True, padx=1, pady=1)
        self.tabla_cajeros.bind("<<TreeviewSelect>>", lambda e: self._mostrar_ventas_cajero())

        agrupadas = datos_ventas.ventas_por_cajero()

        for cajero, ventas in sorted(agrupadas.items(), key=lambda kv: -datos_ventas.total_de(kv[1])):

            self.tabla_cajeros.insert(
                "", "end", iid=cajero,
                values=(cajero, len(ventas), f"Q{datos_ventas.total_de(ventas):.2f}")
            )

        if not agrupadas:
            tk.Label(
                izquierda, text="Todavía no hay ventas registradas.",
                font=("Segoe UI", 10), fg=GRIS, bg=BLANCO
            ).pack(pady=20)

        # ----------------------------------------------------
        # VENTAS DEL CAJERO SELECCIONADO (derecha)
        # ----------------------------------------------------

        derecha = tk.Frame(cuerpo, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
        derecha.pack(side="left", fill="both", expand=True)

        self.lbl_cajero_detalle = tk.Label(
            derecha, text="Selecciona un cajero para ver sus ventas",
            font=("Segoe UI", 12, "bold"), fg=TEXTO, bg=BLANCO
        )
        self.lbl_cajero_detalle.pack(anchor="w", padx=15, pady=12)

        columnas_v = ("id", "fecha", "tipo", "metodo", "total")

        self.tabla_ventas_cajero = ttk.Treeview(
            derecha, columns=columnas_v, show="headings", style="Mr.Treeview"
        )

        titulos_v = {"id": "#", "fecha": "Fecha", "tipo": "Pedido", "metodo": "Método", "total": "Total"}
        anchos_v = {"id": 50, "fecha": 160, "tipo": 130, "metodo": 100, "total": 100}

        for col in columnas_v:
            self.tabla_ventas_cajero.heading(col, text=titulos_v[col])
            self.tabla_ventas_cajero.column(col, width=anchos_v[col], anchor="center")

        self.tabla_ventas_cajero.pack(fill="both", expand=True, padx=1, pady=(0, 1))
        self.tabla_ventas_cajero.bind("<Double-1>", lambda e: self._ver_detalle_venta())

    # ========================================================
    def _crear_personal(self):

        ventana = tk.Toplevel(self)
        ventana.title("Crear personal")
        ventana.configure(bg=BLANCO)
        ventana.geometry("430x430")
        ventana.resizable(False, False)
        ventana.transient(self)
        ventana.grab_set()

        tk.Label(
            ventana, text="Crear Cajero / Cocinero",
            font=("Segoe UI", 17, "bold"), fg=TEXTO, bg=BLANCO
        ).pack(pady=(22, 4))

        tk.Label(
            ventana, text="El cajero usa el rol 'usuario' de la base de datos.",
            font=("Segoe UI", 9), fg=GRIS, bg=BLANCO
        ).pack(pady=(0, 18))

        formulario = tk.Frame(ventana, bg=BLANCO)
        formulario.pack(fill="x", padx=30)

        campos = {}
        for clave, texto in (("nombre", "Nombre completo"), ("usuario", "Usuario"), ("password", "Contraseña")):
            tk.Label(
                formulario, text=texto, font=("Segoe UI", 10, "bold"),
                fg=TEXTO, bg=BLANCO
            ).pack(anchor="w", pady=(5, 4))
            entrada = tk.Entry(formulario, font=("Segoe UI", 11), bd=1, relief="solid", show="•" if clave == "password" else "")
            entrada.pack(fill="x", ipady=7, pady=(0, 8))
            campos[clave] = entrada

        tk.Label(
            formulario, text="Tipo de personal", font=("Segoe UI", 10, "bold"),
            fg=TEXTO, bg=BLANCO
        ).pack(anchor="w", pady=(3, 4))

        rol = tk.StringVar(value="usuario")
        opciones = tk.Frame(formulario, bg=BLANCO)
        opciones.pack(fill="x", pady=(0, 15))

        for valor, texto in (("usuario", "🧾 Cajero"), ("cocinero", "🧑‍🍳 Cocinero")):
            tk.Radiobutton(
                opciones, text=texto, variable=rol, value=valor,
                font=("Segoe UI", 10), fg=TEXTO, bg=BLANCO,
                activebackground=BLANCO, selectcolor=CREMA
            ).pack(side="left", padx=(0, 25))

        def guardar():
            ok, error = crear_usuario(
                campos["nombre"].get(), campos["usuario"].get(),
                campos["password"].get(), rol.get()
            )
            if not ok:
                messagebox.showwarning("Mr.Burger", error, parent=ventana)
                return

            messagebox.showinfo(
                "Personal creado",
                "La cuenta fue creada correctamente y ya puede iniciar sesión.",
                parent=ventana
            )
            ventana.destroy()

        tk.Button(
            ventana, text="Crear cuenta", font=("Segoe UI", 11, "bold"),
            bg=ROJO_CLARO, fg="white", activebackground=ROJO, activeforeground="white",
            relief="flat", cursor="hand2", command=guardar
        ).pack(fill="x", padx=30, ipady=9, pady=(0, 18))

    # ========================================================
    def _mostrar_ventas_cajero(self):

        seleccion = self.tabla_cajeros.selection()

        for fila in self.tabla_ventas_cajero.get_children():
            self.tabla_ventas_cajero.delete(fila)

        if not seleccion:
            return

        cajero = seleccion[0]
        self.lbl_cajero_detalle.configure(text=f"Ventas de {cajero}")

        ventas = datos_ventas.ventas_por_cajero(cajero)

        for venta in sorted(ventas, key=lambda v: v.get("fecha", ""), reverse=True):

            tipo = f"Mesa {venta['mesa']}" if venta.get("tipo_pedido") == "mesa" else "Para Llevar"

            self.tabla_ventas_cajero.insert(
                "", "end", iid=str(venta["id"]),
                values=(
                    venta["id"], venta.get("fecha", ""), tipo,
                    METODOS_PAGO.get(venta.get("metodo_pago"), venta.get("metodo_pago")),
                    f"Q{venta.get('total', 0):.2f}"
                )
            )

    # ========================================================
    def _ver_detalle_venta(self):

        seleccion = self.tabla_ventas_cajero.selection()

        if not seleccion:
            return

        id_venta = int(seleccion[0])
        venta = next((v for v in datos_ventas.cargar_ventas() if v["id"] == id_venta), None)

        if venta is None:
            return

        mostrar_detalle_venta(self, venta)
