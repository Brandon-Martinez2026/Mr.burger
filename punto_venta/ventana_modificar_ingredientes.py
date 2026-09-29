import tkinter as tk
from tkinter import messagebox

from estilos import ROJO, ROJO_CLARO, BLANCO, CREMA, TEXTO, GRIS, BORDE, VERDE, crear_area_desplazable
from punto_venta import ingredientes as _ingredientes


class VentanaModificarIngredientes(tk.Toplevel):
    """Ventana independiente para elegir los ingredientes de las
    hamburguesas del pedido actual.

    Funciona como Cobro/Dividir Cuenta: el cajero entra a una ventana
    propia, selecciona una hamburguesa y modifica sus ingredientes.
    """

    def __init__(self, padre, carrito, al_guardar):
        super().__init__(padre)
        self.padre = padre
        self.carrito = carrito
        self.al_guardar = al_guardar
        self.item_actual = None
        self._variables = {}
        self._ingredientes = []

        self.title("Modificar ingredientes")
        self.configure(bg=CREMA)
        self.geometry("980x650")
        self.minsize(850, 560)
        self.transient(padre)
        self.grab_set()

        self._crear_interfaz()
        self._cargar_hamburguesas()

    def _crear_interfaz(self):
        encabezado = tk.Frame(self, bg=ROJO, height=82)
        encabezado.pack(fill="x")
        encabezado.pack_propagate(False)

        tk.Label(encabezado, text="Modificar ingredientes",
                 font=("Segoe UI", 22, "bold"), fg="white", bg=ROJO).pack(anchor="w", padx=28, pady=(15, 0))
        tk.Label(encabezado, text="Selecciona una hamburguesa y decide qué ingredientes lleva",
                 font=("Segoe UI", 10), fg="#FCE5E0", bg=ROJO).pack(anchor="w", padx=30)

        cuerpo = tk.Frame(self, bg=CREMA)
        cuerpo.pack(fill="both", expand=True, padx=22, pady=18)

        # Lista izquierda: productos del pedido.
        izquierda = tk.Frame(cuerpo, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1, width=300)
        izquierda.pack(side="left", fill="y", padx=(0, 12))
        izquierda.pack_propagate(False)

        tk.Label(izquierda, text="Hamburguesas del pedido", font=("Segoe UI", 13, "bold"),
                 fg=TEXTO, bg=BLANCO).pack(anchor="w", padx=18, pady=(18, 4))
        tk.Label(izquierda, text="Elige cuál quieres modificar.", font=("Segoe UI", 9),
                 fg=GRIS, bg=BLANCO).pack(anchor="w", padx=18, pady=(0, 12))

        self.lista_productos = tk.Frame(izquierda, bg=BLANCO)
        self.lista_productos.pack(fill="both", expand=True, padx=10, pady=(0, 12))

        # Panel derecho: ingredientes.
        derecha = tk.Frame(cuerpo, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
        derecha.pack(side="left", fill="both", expand=True)

        self.lbl_producto = tk.Label(derecha, text="Selecciona una hamburguesa",
                                     font=("Segoe UI", 17, "bold"), fg=ROJO, bg=BLANCO)
        self.lbl_producto.pack(anchor="w", padx=22, pady=(18, 2))

        self.lbl_info = tk.Label(derecha, text="", font=("Segoe UI", 9), fg=GRIS, bg=BLANCO)
        self.lbl_info.pack(anchor="w", padx=22, pady=(0, 10))

        self._contenedor, self.interior = crear_area_desplazable(derecha, bg=BLANCO)
        self._contenedor.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        botones = tk.Frame(derecha, bg=BLANCO)
        botones.pack(fill="x", padx=20, pady=(0, 18))

        tk.Button(botones, text="Cancelar", font=("Segoe UI", 10), bg=BLANCO, fg=ROJO,
                  relief="solid", bd=1, cursor="hand2", command=self.destroy).pack(
                      side="left", fill="x", expand=True, padx=(0, 5), ipady=8)
        self.btn_guardar = tk.Button(botones, text="Guardar cambios", font=("Segoe UI", 10, "bold"),
                                     bg=ROJO_CLARO, fg="white", activebackground=ROJO,
                                     activeforeground="white", relief="flat", cursor="hand2",
                                     command=self._guardar_actual)
        self.btn_guardar.pack(side="left", fill="x", expand=True, padx=(5, 0), ipady=8)

    def _cargar_hamburguesas(self):
        for widget in self.lista_productos.winfo_children():
            widget.destroy()

        hamburguesas = []
        for item in self.carrito:
            ingredientes = _ingredientes.obtener_ingredientes_editables(item)
            if ingredientes:
                hamburguesas.append((item, ingredientes))

        if not hamburguesas:
            tk.Label(self.lista_productos,
                     text="No hay hamburguesas configurables en este pedido.",
                     font=("Segoe UI", 10), fg=GRIS, bg=BLANCO,
                     wraplength=240, justify="left").pack(anchor="w", padx=10, pady=20)
            self.btn_guardar.configure(state="disabled")
            return

        self.btn_guardar.configure(state="normal")

        for indice, (item, ingredientes) in enumerate(hamburguesas):
            boton = tk.Button(
                self.lista_productos,
                text=f"{item['cantidad']}x  {item['nombre']}",
                font=("Segoe UI", 10, "bold"),
                anchor="w", justify="left", wraplength=245,
                bg=BLANCO, fg=TEXTO, activebackground="#FFF0D5",
                relief="flat", bd=0, cursor="hand2",
                padx=12, pady=12,
                command=lambda it=item, ing=ingredientes: self._seleccionar(it, ing)
            )
            boton.pack(fill="x", pady=3)

        self._seleccionar(*hamburguesas[0])

    def _seleccionar(self, item, ingredientes):
        self.item_actual = item
        self._ingredientes = ingredientes
        self._variables = {}

        self.lbl_producto.configure(text=item["nombre"])
        self.lbl_info.configure(text=f"{item['cantidad']} unidad(es)  ·  Selecciona los ingredientes que quieres quitar o agregar como extra.")

        for widget in self.interior.winfo_children():
            widget.destroy()

        actuales = {x.get("id_insumo"): x for x in (item.get("modificadores") or [])}

        for ing in ingredientes:
            iid = int(ing["id_insumo"])
            actual = actuales.get(iid, {})
            incluido = bool(ing["incluido"])
            quitar = tk.BooleanVar(value=bool(actual.get("quitar", False)))
            extra = tk.IntVar(value=int(actual.get("extra", 0) or 0))
            self._variables[iid] = (ing, quitar, extra)

            card = tk.Frame(self.interior, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
            card.pack(fill="x", padx=7, pady=5)

            fila = tk.Frame(card, bg=BLANCO)
            fila.pack(fill="x", padx=12, pady=(9, 4))

            tk.Label(fila, text=ing["nombre_insumo"], font=("Segoe UI", 11, "bold"),
                     fg=TEXTO, bg=BLANCO).pack(side="left")
            tk.Label(fila, text="Incluido" if incluido else "Opcional",
                     font=("Segoe UI", 8), fg=GRIS, bg=BLANCO).pack(side="right")

            controles = tk.Frame(card, bg=BLANCO)
            controles.pack(fill="x", padx=12, pady=(0, 9))

            if incluido and bool(ing["permite_quitar"]):
                tk.Checkbutton(controles, text="Quitar ingrediente", variable=quitar,
                               font=("Segoe UI", 10), fg=ROJO, bg=BLANCO,
                               activebackground=BLANCO, selectcolor=BLANCO,
                               cursor="hand2").pack(side="left")
            else:
                tk.Label(controles, text="Agregar como extra", font=("Segoe UI", 9),
                         fg=GRIS, bg=BLANCO).pack(side="left")

            if bool(ing["permite_extra"]):
                tk.Label(controles, text="Extra", font=("Segoe UI", 9, "bold"),
                         fg=TEXTO, bg=BLANCO).pack(side="right", padx=(8, 5))
                tk.Button(controles, text="+", width=3, relief="solid", bd=1, bg=BLANCO,
                          cursor="hand2", command=lambda v=extra: v.set(min(5, v.get() + 1))).pack(side="right")
                tk.Label(controles, textvariable=extra, width=3, font=("Segoe UI", 10, "bold"),
                         fg=TEXTO, bg=BLANCO).pack(side="right")
                tk.Button(controles, text="−", width=3, relief="solid", bd=1, bg=BLANCO,
                          cursor="hand2", command=lambda v=extra: v.set(max(0, v.get() - 1))).pack(side="right")

    def _guardar_actual(self):
        if not self.item_actual:
            return

        modificadores = []
        for iid, (ing, quitar, extra) in self._variables.items():
            if quitar.get() or extra.get() > 0:
                modificadores.append({
                    "id_insumo": iid,
                    "nombre": ing["nombre_insumo"],
                    "quitar": bool(quitar.get()),
                    "extra": 0 if quitar.get() else int(extra.get()),
                    "cantidad_base": float(ing["cantidad_base"] or 0),
                })

        self.item_actual["modificadores"] = modificadores
        self.al_guardar()

        messagebox.showinfo("Mr.Burger", "Los ingredientes de la hamburguesa fueron actualizados.", parent=self)
        self.destroy()
