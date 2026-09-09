"""
dialogo_detalle_venta.py
------------------------------------------------------------
Pequeña ventana con el detalle (productos y total) de una
venta. La usan tanto vista_cajeros.py como vista_ventas.py al
hacer doble clic sobre una fila.
------------------------------------------------------------
"""

import tkinter as tk

from estilos import ROJO, BLANCO, TEXTO, BORDE
from panel_admin.datos_admin import METODOS_PAGO


def mostrar_detalle_venta(padre, venta):

    ventana = tk.Toplevel(padre)
    ventana.title(f"Venta #{venta['id']}")
    ventana.configure(bg=BLANCO)
    ventana.geometry("400x460")
    ventana.resizable(False, False)
    ventana.transient(padre)
    ventana.grab_set()

    tipo = f"Mesa {venta['mesa']}" if venta.get("tipo_pedido") == "mesa" else "Para Llevar"

    tk.Label(
        ventana, text=f"Venta #{venta['id']}", font=("Segoe UI", 16, "bold"),
        fg=ROJO, bg=BLANCO
    ).pack(anchor="w", padx=20, pady=(18, 4))

    info = (
        f"Fecha: {venta.get('fecha', '')}\n"
        f"Cajero: {venta.get('cajero', '')}\n"
        f"Pedido: {tipo}\n"
        f"Método de pago: {METODOS_PAGO.get(venta.get('metodo_pago'), venta.get('metodo_pago'))}"
    )

    tk.Label(
        ventana, text=info, font=("Segoe UI", 10), fg=TEXTO, bg=BLANCO, justify="left"
    ).pack(anchor="w", padx=20, pady=(0, 10))

    tk.Frame(ventana, bg=BORDE, height=1).pack(fill="x", padx=20, pady=5)

    lista = tk.Frame(ventana, bg=BLANCO)
    lista.pack(fill="both", expand=True, padx=20)

    for item in venta.get("items", []):

        fila = tk.Frame(lista, bg=BLANCO)
        fila.pack(fill="x", pady=4)

        tk.Label(
            fila, text=f"{item['cantidad']}x {item['nombre']}",
            font=("Segoe UI", 10), fg=TEXTO, bg=BLANCO
        ).pack(side="left")

        tk.Label(
            fila, text=f"Q{item['precio'] * item['cantidad']:.2f}",
            font=("Segoe UI", 10, "bold"), fg=TEXTO, bg=BLANCO
        ).pack(side="right")

    tk.Frame(ventana, bg=BORDE, height=1).pack(fill="x", padx=20, pady=8)

    tk.Label(
        ventana, text=f"Total: Q{venta.get('total', 0):.2f}",
        font=("Segoe UI", 15, "bold"), fg=TEXTO, bg=BLANCO
    ).pack(anchor="e", padx=20, pady=(0, 18))

    return ventana
