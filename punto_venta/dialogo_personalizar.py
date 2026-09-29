import tkinter as tk

from estilos import ROJO, ROJO_CLARO, BLANCO, TEXTO, GRIS, BORDE, crear_area_desplazable
from punto_venta import ingredientes as _ingredientes


class DialogoPersonalizar(tk.Toplevel):
    """Permite modificar directamente cada ingrediente de una línea.
    No depende de notas: la selección se guarda como datos estructurados.
    """

    def __init__(self, padre, item, al_guardar):
        super().__init__(padre)
        self.al_guardar = al_guardar
        self.item = item
        self.title("Personalizar hamburguesa")
        self.configure(bg=BLANCO)
        self.geometry("460x620")
        self.minsize(420, 520)
        self.transient(padre)
        self.grab_set()

        self._ingredientes = _ingredientes.obtener_ingredientes_editables(item)
        self._variables = {}
        self._crear_interfaz()

    def _crear_interfaz(self):
        tk.Label(self, text=self.item["nombre"], font=("Segoe UI", 16, "bold"),
                 fg=ROJO, bg=BLANCO, wraplength=410, justify="left").pack(anchor="w", padx=22, pady=(18, 2))
        tk.Label(self, text=f"{self.item['cantidad']}x  ·  Q{self.item['precio']:.2f} c/u",
                 font=("Segoe UI", 10), fg=GRIS, bg=BLANCO).pack(anchor="w", padx=22, pady=(0, 12))

        tk.Label(self, text="Ingredientes", font=("Segoe UI", 12, "bold"),
                 fg=TEXTO, bg=BLANCO).pack(anchor="w", padx=22)
        tk.Label(self, text="Elige qué quitar y qué agregar como extra.",
                 font=("Segoe UI", 9), fg=GRIS, bg=BLANCO).pack(anchor="w", padx=22, pady=(0, 7))

        contenedor, interior = crear_area_desplazable(self, bg=BLANCO)
        contenedor.pack(fill="both", expand=True, padx=17, pady=(0, 8))

        actuales = {x.get("id_insumo"): x for x in (self.item.get("modificadores") or [])}

        if not self._ingredientes:
            tk.Label(interior, text="Este producto no tiene una receta configurable en la base de datos.",
                     font=("Segoe UI", 10), fg=GRIS, bg=BLANCO, wraplength=380, justify="left").pack(padx=10, pady=20)
        else:
            for ing in self._ingredientes:
                iid = int(ing["id_insumo"])
                actual = actuales.get(iid, {})
                base = float(ing["cantidad_base"] or 0)
                incluido = bool(ing["incluido"])
                quitar = tk.BooleanVar(value=bool(actual.get("quitar", False)))
                extra = tk.IntVar(value=int(actual.get("extra", 0) or 0))
                self._variables[iid] = (ing, quitar, extra)

                card = tk.Frame(interior, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
                card.pack(fill="x", padx=6, pady=5)

                fila = tk.Frame(card, bg=BLANCO)
                fila.pack(fill="x", padx=10, pady=(8, 3))
                tk.Label(fila, text=ing["nombre_insumo"], font=("Segoe UI", 11, "bold"),
                         fg=TEXTO, bg=BLANCO).pack(side="left")
                estado = "incluido" if incluido else "opcional"
                tk.Label(fila, text=estado, font=("Segoe UI", 8), fg=GRIS, bg=BLANCO).pack(side="right")

                controles = tk.Frame(card, bg=BLANCO)
                controles.pack(fill="x", padx=10, pady=(0, 8))

                if incluido and bool(ing["permite_quitar"]):
                    tk.Checkbutton(controles, text="Quitar", variable=quitar,
                                    font=("Segoe UI", 10), fg=ROJO, bg=BLANCO,
                                    activebackground=BLANCO, selectcolor=BLANCO, cursor="hand2").pack(side="left")
                else:
                    tk.Label(controles, text="Disponible como extra", font=("Segoe UI", 9),
                             fg=GRIS, bg=BLANCO).pack(side="left")

                if bool(ing["permite_extra"]):
                    tk.Label(controles, text="Extra:", font=("Segoe UI", 9), fg=TEXTO, bg=BLANCO).pack(side="right", padx=(8, 4))
                    tk.Button(controles, text="−", width=2, command=lambda v=extra: v.set(max(0, v.get()-1)),
                              relief="flat", bg=BLANCO, fg=TEXTO).pack(side="right")
                    tk.Label(controles, textvariable=extra, width=2, font=("Segoe UI", 10, "bold"),
                             fg=TEXTO, bg=BLANCO).pack(side="right")
                    tk.Button(controles, text="+", width=2, command=lambda v=extra: v.set(min(5, v.get()+1)),
                              relief="flat", bg=BLANCO, fg=TEXTO).pack(side="right")

                tk.Label(card, text=f"Porción base: {base:g}", font=("Segoe UI", 8), fg=GRIS, bg=BLANCO).pack(anchor="w", padx=10, pady=(0, 7))

        tk.Label(self, text="Instrucciones especiales (opcional)", font=("Segoe UI", 11, "bold"),
                 fg=TEXTO, bg=BLANCO).pack(anchor="w", padx=22, pady=(5, 4))
        self.entrada_instrucciones = tk.Text(self, height=3, font=("Segoe UI", 10), fg=TEXTO, bd=1, relief="solid")
        self.entrada_instrucciones.insert("1.0", self.item.get("instrucciones", ""))
        self.entrada_instrucciones.pack(fill="x", padx=22, pady=(0, 12))

        botones = tk.Frame(self, bg=BLANCO)
        botones.pack(fill="x", padx=22, pady=(0, 18), side="bottom")
        tk.Button(botones, text="Cancelar", font=("Segoe UI", 11), bg=BLANCO, relief="solid", bd=1,
                  command=self.destroy).pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=8)
        tk.Button(botones, text="Guardar cambios", font=("Segoe UI", 11, "bold"), bg=ROJO_CLARO, fg="white",
                  relief="flat", activebackground=ROJO, activeforeground="white", command=self._guardar).pack(side="left", fill="x", expand=True, padx=(5, 0), ipady=8)

    def _guardar(self):
        modificadores = []
        for iid, (ing, quitar, extra) in self._variables.items():
            if quitar.get() or extra.get() > 0:
                # Quitar y extra son estados excluyentes para evitar
                # consumir una cantidad adicional de un ingrediente que
                # el cliente pidió eliminar.
                cantidad_extra = 0 if quitar.get() else int(extra.get())
                modificadores.append({
                    "id_insumo": iid,
                    "nombre": ing["nombre_insumo"],
                    "quitar": bool(quitar.get()),
                    "extra": cantidad_extra,
                    "cantidad_base": float(ing["cantidad_base"] or 0),
                })
        instrucciones = self.entrada_instrucciones.get("1.0", "end").strip()
        self.al_guardar(modificadores, instrucciones)
        self.destroy()
