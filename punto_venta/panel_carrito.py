"""
panel_carrito.py
------------------------------------------------------------
Panel derecho del Punto de Venta: tipo de pedido (mesa / para
llevar), productos agregados al carrito, total y los botones
para pagar, guardar o cancelar el pedido.
------------------------------------------------------------
"""

import datetime

import tkinter as tk
from tkinter import messagebox

from estilos import ROJO, ROJO_CLARO, BLANCO, TEXTO, GRIS, NARANJA, BORDE, crear_area_desplazable
from punto_venta import catalogo
from punto_venta.ventana_pago import VentanaMetodoPago
from punto_venta.dialogo_personalizar import DialogoPersonalizar

import datos_ventas
from basedatos.conexion import ErrorBaseDatos


class PanelCarrito(tk.Frame):
    """Frame que se coloca a la derecha de la ventana principal
    del Punto de Venta. Guarda el carrito de la venta actual y
    todo lo relacionado con el cobro."""

    def __init__(self, parent, controlador):

        super().__init__(
            parent, bg=BLANCO, width=430,
            highlightbackground=BORDE, highlightthickness=1
        )

        self.controlador = controlador

        # Carrito de la venta que se está armando actualmente.
        self.carrito = []

        # Tipo de pedido: "mesa" o "llevar".
        self.tipo_pedido = "mesa"
        self.numero_mesa = 4

        self.pack_propagate(False)

        self._crear_interfaz()

    # ========================================================
    # INTERFAZ
    # ========================================================

    def _crear_interfaz(self):

        tk.Label(
            self, text="Resumen del Pedido", font=("Segoe UI", 22, "bold"),
            fg=TEXTO, bg=BLANCO
        ).pack(anchor="w", padx=25, pady=(25, 18))

        # ----------------------------------------------------
        # TIPO DE PEDIDO: MESA / PARA LLEVAR
        # ----------------------------------------------------

        mesa = tk.Frame(self, bg="#FFF0D5")
        mesa.pack(fill="x", padx=25)

        self.btn_tipo_mesa = tk.Button(
            mesa, font=("Segoe UI", 12, "bold"), relief="flat", bd=0,
            cursor="hand2", command=self.elegir_mesa
        )
        self.btn_tipo_mesa.pack(side="left", padx=(15, 5), pady=10, ipadx=6, ipady=4)

        self.btn_tipo_llevar = tk.Button(
            mesa, text="🛍  Para Llevar", font=("Segoe UI", 11), relief="flat",
            bd=0, cursor="hand2", command=self.elegir_para_llevar
        )
        self.btn_tipo_llevar.pack(side="right", padx=(5, 15), pady=10, ipadx=6, ipady=4)

        self._actualizar_botones_tipo_pedido()

        # ----------------------------------------------------
        # PRODUCTOS DEL CARRITO
        # ----------------------------------------------------

        # Con scroll: si se agregan varios productos (por ejemplo un
        # combo familiar más varios extras) la lista puede volverse
        # más alta que el espacio disponible en el panel derecho.
        self._contenedor_lista_carrito, self.lista_carrito = crear_area_desplazable(self, bg=BLANCO)
        self._contenedor_lista_carrito.pack(fill="both", expand=True, padx=25, pady=15)

        tk.Label(
            self.lista_carrito, text="Aún no has agregado productos.",
            font=("Segoe UI", 10), fg=GRIS, bg=BLANCO
        ).pack(pady=10)

        # ----------------------------------------------------
        # TOTAL
        # ----------------------------------------------------

        self.total_frame = tk.Frame(self, bg=BLANCO)
        self.total_frame.pack(fill="x", padx=25)

        self.lbl_total = tk.Label(
            self.total_frame, text="Total:                    Q0.00",
            font=("Segoe UI", 15, "bold"), fg=TEXTO, bg=BLANCO
        )
        self.lbl_total.pack(pady=12)

        # ----------------------------------------------------
        # MODIFICADORES
        # ----------------------------------------------------

        tk.Button(
            self, text="Modificadores                         ⌄",
            font=("Segoe UI", 11), bg=BLANCO, fg=GRIS, relief="flat",
            anchor="w", bd=1
        ).pack(fill="x", padx=25, pady=5)

        # ----------------------------------------------------
        # NOTAS
        # ----------------------------------------------------

        self.entrada_notas = tk.Text(self, height=3, font=("Segoe UI", 10), fg=GRIS, bd=1, relief="solid")
        self.entrada_notas.insert("1.0", "Notas")
        self.entrada_notas.pack(fill="x", padx=25, pady=5)

        # ----------------------------------------------------
        # BOTONES
        # ----------------------------------------------------

        botones = tk.Frame(self, bg=BLANCO)
        botones.pack(fill="x", padx=25, pady=8)

        tk.Button(
            botones, text="⚖\nDividir Cuenta", font=("Segoe UI", 10),
            bg=BLANCO, relief="solid", bd=1
        ).pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=8)

        tk.Button(
            botones, text="%\nAplicar Descuento", font=("Segoe UI", 10),
            bg=BLANCO, relief="solid", bd=1
        ).pack(side="left", fill="x", expand=True, padx=(5, 0), ipady=8)

        # ----------------------------------------------------
        # PAGAR
        # ----------------------------------------------------

        self.btn_pagar = tk.Button(
            self, text="Pagar: Q0.00", font=("Segoe UI", 14, "bold"),
            bg=ROJO_CLARO, fg="white", activebackground=ROJO, activeforeground="white",
            relief="flat", command=self.pagar
        )
        self.btn_pagar.pack(fill="x", padx=25, pady=10, ipady=8)

        # ----------------------------------------------------
        # GUARDAR / CANCELAR
        # ----------------------------------------------------

        abajo = tk.Frame(self, bg=BLANCO)
        abajo.pack(fill="x", padx=25, pady=(0, 20))

        tk.Button(
            abajo, text="Guardar Pedido", font=("Segoe UI", 10),
            bg=BLANCO, relief="solid", bd=1
        ).pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=7)

        tk.Button(
            abajo, text="Cancelar", font=("Segoe UI", 10), bg=BLANCO,
            relief="solid", bd=1, command=self.cancelar
        ).pack(side="left", fill="x", expand=True, padx=(5, 0), ipady=7)

    # ========================================================
    # TIPO DE PEDIDO (MESA / PARA LLEVAR)
    # ========================================================

    def elegir_mesa(self):
        """Al presionar el botón de mesa se despliega un menú con
        los números de mesa disponibles para elegir."""

        menu = tk.Menu(self, tearoff=0)

        for numero in range(1, 13):
            menu.add_command(
                label=f"Mesa {numero}", command=lambda n=numero: self._set_mesa(n)
            )

        x = self.btn_tipo_mesa.winfo_rootx()
        y = self.btn_tipo_mesa.winfo_rooty() + self.btn_tipo_mesa.winfo_height()

        menu.tk_popup(x, y)

    def _set_mesa(self, numero):

        self.tipo_pedido = "mesa"
        self.numero_mesa = numero

        self._actualizar_botones_tipo_pedido()

    def elegir_para_llevar(self):

        self.tipo_pedido = "llevar"

        self._actualizar_botones_tipo_pedido()

    def _actualizar_botones_tipo_pedido(self):

        es_mesa = self.tipo_pedido == "mesa"

        self.btn_tipo_mesa.configure(
            text=f"▰  Mesa {self.numero_mesa}",
            bg=ROJO_CLARO if es_mesa else "#FFF0D5",
            fg="white" if es_mesa else TEXTO
        )

        self.btn_tipo_llevar.configure(
            bg=ROJO_CLARO if not es_mesa else "#FFF0D5",
            fg="white" if not es_mesa else TEXTO
        )

    # ========================================================
    # AGREGAR PRODUCTO
    # ========================================================

    def agregar_producto(self, producto):

        stock = producto.get("stock")

        if stock is not None:

            en_carrito = sum(
                item["cantidad"] for item in self.carrito
                if item.get("id") == producto.get("id")
            )

            if en_carrito >= stock:
                messagebox.showwarning(
                    "Sin inventario",
                    f"No hay más stock disponible de "
                    f"\"{producto['nombre'].replace(chr(10), ' ')}\"."
                )
                return

        for item in self.carrito:

            if item.get("id") == producto.get("id"):
                item["cantidad"] += 1
                self.actualizar_resumen()
                return

        self.carrito.append({
            "id": producto.get("id"),
            "nombre": producto["nombre"].replace("\n", " "),
            "precio": producto["precio"],
            "cantidad": 1,
            # Se guarda la categoría del producto (no solo su
            # nombre/precio) porque DialogoPersonalizar la necesita
            # para saber qué ingredientes ofrecer al editarlo.
            "categoria": producto.get("categoria"),
            # Personalización del producto (quitar ingredientes,
            # instrucciones especiales). Se editan haciendo clic en
            # la línea del carrito; ver DialogoPersonalizar.
            "ingredientes_quitados": [],
            "instrucciones": "",
        })
        # Nota: conservamos "id" (id_producto) en cada línea del
        # carrito porque es lo que se usa para registrar el pedido
        # de verdad en la base de datos (detalle_pedido).

        self.actualizar_resumen()

    # ========================================================
    # ACTUALIZAR RESUMEN
    # ========================================================

    def actualizar_resumen(self):

        for widget in self.lista_carrito.winfo_children():
            widget.destroy()

        if not self.carrito:
            tk.Label(
                self.lista_carrito, text="Aún no has agregado productos.",
                font=("Segoe UI", 10), fg=GRIS, bg=BLANCO
            ).pack(pady=10)

        total = 0

        for item in self.carrito:

            subtotal = item["precio"] * item["cantidad"]
            total += subtotal

            # Bloque completo de la línea (cantidad/nombre/precio +
            # el resumen de personalización). Todo el bloque es
            # clickeable para poder editar el producto: quitarle
            # ingredientes o agregarle instrucciones especiales.
            bloque = tk.Frame(self.lista_carrito, bg=BLANCO, cursor="hand2")
            bloque.pack(fill="x", pady=8)

            fila = tk.Frame(bloque, bg=BLANCO)
            fila.pack(fill="x")

            tk.Label(
                fila, text=f"{item['cantidad']}x", font=("Segoe UI", 11, "bold"),
                fg=ROJO, bg=BLANCO
            ).pack(side="left")

            tk.Label(
                fila, text=item["nombre"], font=("Segoe UI", 11),
                fg=TEXTO, bg=BLANCO
            ).pack(side="left", padx=12)

            tk.Label(
                fila, text=f"Q{subtotal:.2f}", font=("Segoe UI", 11, "bold"),
                fg=TEXTO, bg=BLANCO
            ).pack(side="right")

            # ----------------------------------------------------
            # RESUMEN DE PERSONALIZACIÓN + enlace para editar
            # ----------------------------------------------------

            quitados = item.get("ingredientes_quitados") or []
            instrucciones = (item.get("instrucciones") or "").strip()

            detalle_texto = ""
            if quitados:
                detalle_texto += "Sin " + ", ".join(quitados).lower()
            if instrucciones:
                detalle_texto += (" · " if detalle_texto else "") + instrucciones

            pie = tk.Frame(bloque, bg=BLANCO)
            pie.pack(fill="x", pady=(3, 0))

            tk.Label(
                pie, text=detalle_texto, font=("Segoe UI", 9, "italic"),
                fg=NARANJA, bg=BLANCO, wraplength=300, justify="left", anchor="w"
            ).pack(side="left", fill="x", expand=True)

            tk.Label(
                pie, text="✎ Editar", font=("Segoe UI", 9, "bold"),
                fg=ROJO, bg=BLANCO
            ).pack(side="right")

            tk.Frame(bloque, bg=BORDE, height=1).pack(fill="x", pady=(8, 0))

            # El bloque completo (y todos sus widgets hijos) abre el
            # editor al hacer clic en cualquier parte.
            widgets_clickeables = [bloque, fila, pie]
            widgets_clickeables.extend(fila.winfo_children())
            widgets_clickeables.extend(pie.winfo_children())

            for widget in widgets_clickeables:
                widget.bind("<Button-1>", lambda e, it=item: self._editar_item(it))

        self.lbl_total.configure(text=f"Total:                    Q{total:.2f}")
        self.btn_pagar.configure(text=f"Pagar: Q{total:.2f}")

    # ========================================================
    # EDITAR / PERSONALIZAR UN PRODUCTO DEL CARRITO
    # ========================================================

    def _editar_item(self, item):
        """Se llama al hacer clic sobre un producto ya agregado al
        carrito. Abre DialogoPersonalizar para que el cajero pueda
        quitarle ingredientes o escribir una instrucción especial
        (por ejemplo, 'sin tomate' en una hamburguesa)."""

        def _al_guardar(ingredientes_quitados, instrucciones):
            item["ingredientes_quitados"] = ingredientes_quitados
            item["instrucciones"] = instrucciones
            self.actualizar_resumen()

        DialogoPersonalizar(self, item, _al_guardar)

    # ========================================================
    # PAGAR
    # ========================================================

    def pagar(self):

        if not self.carrito:
            messagebox.showwarning("Mr.Burger", "No hay productos en el pedido.")
            return

        total = sum(item["precio"] * item["cantidad"] for item in self.carrito)

        VentanaMetodoPago(self.controlador, total, self._finalizar_venta)

    # ========================================================
    # FINALIZAR VENTA (tras elegir método de pago)
    # ========================================================

    def _finalizar_venta(self, metodo, detalle):

        total = sum(item["precio"] * item["cantidad"] for item in self.carrito)

        notas_texto = self.entrada_notas.get("1.0", "end").strip()

        if notas_texto == "Notas":
            notas_texto = ""

        # ----------------------------------------------------
        # PERSONALIZACIÓN DE CADA PRODUCTO (ingredientes quitados /
        # instrucciones especiales)
        # ----------------------------------------------------
        # La base de datos todavía no tiene una columna de notas
        # por línea de pedido (detalle_pedido), así que por ahora
        # esto se agrega al texto de notas general del pedido, que
        # sí llega a la pantalla de Cocina. Cada línea del carrito
        # de todas formas sigue guardando su propia personalización
        # ("ingredientes_quitados" / "instrucciones") para cuando el
        # equipo de base de datos agregue esa columna y se pueda
        # enviar tal cual, sin tener que rehacer esta pantalla.
        # ----------------------------------------------------

        lineas_personalizacion = []

        for item in self.carrito:

            partes = []

            if item.get("ingredientes_quitados"):
                partes.append("sin " + ", ".join(item["ingredientes_quitados"]).lower())

            if item.get("instrucciones"):
                partes.append(item["instrucciones"])

            if partes:
                lineas_personalizacion.append(f"{item['nombre']}: " + " / ".join(partes))

        if lineas_personalizacion:
            resumen_personalizacion = "\n".join(lineas_personalizacion)
            notas_texto = (
                f"{notas_texto}\n{resumen_personalizacion}".strip()
                if notas_texto else resumen_personalizacion
            )

        # ----------------------------------------------------
        # REGISTRAR LA VENTA EN LA BASE DE DATOS
        # ----------------------------------------------------
        # Esto crea el pedido, agrega cada producto, registra el
        # o los pagos y confirma el pedido (sp_confirmar_pedido),
        # que a su vez valida y descuenta el inventario real
        # dentro de MySQL. Si algo falla (por ejemplo, no hay
        # inventario suficiente) no se guarda nada y se avisa al
        # cajero sin perder el carrito.
        # ----------------------------------------------------

        venta = {
            "id_usuario": getattr(self.controlador, "id_usuario", None),
            "cajero": self.controlador.cajero_actual,
            "tipo_pedido": self.tipo_pedido,
            "mesa": self.numero_mesa if self.tipo_pedido == "mesa" else None,
            "notas": notas_texto or None,
            "metodo_pago": metodo,
            "detalle_pago": detalle,
            "items": [
                {
                    "id": item.get("id"),
                    "nombre": item["nombre"],
                    "precio": item["precio"],
                    "cantidad": item["cantidad"],
                    # Se guardan también aquí (aunque por ahora la
                    # base de datos los ignore) para que cuando se
                    # agregue soporte real de personalización por
                    # producto, los datos ya estén disponibles.
                    "ingredientes_quitados": item.get("ingredientes_quitados") or [],
                    "instrucciones": item.get("instrucciones") or "",
                }
                for item in self.carrito
            ],
            "total": round(total, 2)
        }

        try:
            datos_ventas.guardar_venta(venta)
        except ErrorBaseDatos as error:
            messagebox.showerror("No se pudo registrar la venta", str(error))
            return

        # ----------------------------------------------------
        # MENSAJE DE CONFIRMACIÓN
        # ----------------------------------------------------

        nombres_metodo = {
            "efectivo": "Efectivo",
            "tarjeta": "Tarjeta",
            "mixto": "Mixto (efectivo + tarjeta)"
        }

        mensaje = (
            f"Pago registrado correctamente.\n\n"
            f"Total: Q{total:.2f}\n"
            f"Método de pago: {nombres_metodo.get(metodo, metodo)}\n"
        )

        if metodo == "efectivo":
            mensaje += f"Cambio entregado: Q{detalle['cambio']:.2f}\n"
        elif metodo == "mixto":
            mensaje += (
                f"Efectivo: Q{detalle['efectivo']:.2f}  |  "
                f"Tarjeta: Q{detalle['tarjeta']:.2f}\n"
            )

        if self.tipo_pedido == "mesa":
            mensaje += f"Pedido: Mesa {self.numero_mesa}\n"
        else:
            mensaje += "Pedido: Para Llevar\n"

        # El pago queda registrado de inmediato, pero el pedido
        # todavía no se marca como entregado: pasa a la pantalla
        # de Cocina (estado "enviado_cocina") y se entrega solo
        # cuando el cocinero lo marca como listo.
        mensaje += "\n🍳 El pedido fue enviado a cocina."

        messagebox.showinfo("Pedido enviado a cocina", mensaje)

        self.carrito.clear()
        self.actualizar_resumen()

        self.entrada_notas.delete("1.0", "end")
        self.entrada_notas.insert("1.0", "Notas")

        # Refresca la cuadrícula de productos para reflejar el
        # stock que se acaba de descontar en la base de datos.
        if hasattr(self.controlador, "vista_productos"):
            self.controlador.vista_productos.dibujar_productos()

    # ========================================================
    # CANCELAR
    # ========================================================

    def cancelar(self):

        if not self.carrito:
            return

        confirmar = messagebox.askyesno("Cancelar pedido", "¿Deseas cancelar el pedido?")

        if confirmar:
            self.carrito.clear()
            self.actualizar_resumen()
