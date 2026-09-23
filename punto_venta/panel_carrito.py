"""
panel_carrito.py
------------------------------------------------------------
Panel derecho del Punto de Venta: tipo de pedido (mesa / para
llevar), productos agregados al carrito, total y los botones
para pagar, guardar, dividir cuenta, aplicar descuento o
cancelar el pedido.
------------------------------------------------------------
"""

import datetime

import tkinter as tk
from tkinter import messagebox

from estilos import ROJO, ROJO_CLARO, ROJO_OSCURO, BLANCO, CREMA, TEXTO, GRIS, BORDE, VERDE
from punto_venta import catalogo
from punto_venta.ventana_pago import VentanaMetodoPago
from punto_venta.ventana_dividir_cuenta import VentanaDividirCuenta

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

        # Tipo de pedido: "mesa" o "llevar". Por defecto arranca
        # en "Mesa 1" (la mesa predeterminada del negocio); el
        # cajero puede cambiarla con el selector de mesas.
        self.tipo_pedido = "mesa"
        self.numero_mesa = 1

        # Descuento aplicado al pedido actual (ninguno por
        # defecto). "tipo" es "porcentaje" o "monto" (fijo).
        self.descuento_tipo = None
        self.descuento_valor = 0.0

        # Estado del flujo de "Dividir Cuenta": mientras se están
        # cobrando las cuentas una por una, self._en_division es
        # True y self._cuentas_pendientes guarda las que faltan.
        self._en_division = False
        self._cuentas_pendientes = []
        self._cuenta_num_actual = 0
        self._cuenta_num_total = 0

        # El cuadro de notas empieza oculto; se muestra/oculta con
        # el botón "Modificadores".
        self._notas_visibles = False

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

        self.lista_carrito = tk.Frame(self, bg=BLANCO)
        self.lista_carrito.pack(fill="both", expand=True, padx=25, pady=15)

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
        # MODIFICADORES (muestra/oculta las notas del pedido)
        # ----------------------------------------------------

        self.btn_modificadores = tk.Button(
            self, text="Modificadores                         ⌄",
            font=("Segoe UI", 11), bg=BLANCO, fg=GRIS, relief="flat",
            anchor="w", bd=1, cursor="hand2", command=self._alternar_notas
        )
        self.btn_modificadores.pack(fill="x", padx=25, pady=5)

        # ----------------------------------------------------
        # NOTAS (ocultas hasta que se abren desde "Modificadores")
        # ----------------------------------------------------

        self.entrada_notas = tk.Text(self, height=3, font=("Segoe UI", 10), fg=GRIS, bd=1, relief="solid")
        self.entrada_notas.insert("1.0", "Notas")

        # ----------------------------------------------------
        # DIVIDIR CUENTA / APLICAR DESCUENTO
        # ----------------------------------------------------

        botones = tk.Frame(self, bg=BLANCO)
        botones.pack(fill="x", padx=25, pady=8)

        self.btn_dividir_cuenta = tk.Button(
            botones, text="⚖\nDividir Cuenta", font=("Segoe UI", 10),
            bg=BLANCO, relief="solid", bd=1, cursor="hand2", command=self.dividir_cuenta
        )
        self.btn_dividir_cuenta.pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=8)

        self.btn_descuento = tk.Button(
            botones, text="%\nAplicar Descuento", font=("Segoe UI", 10),
            bg=BLANCO, relief="solid", bd=1, cursor="hand2", command=self.abrir_descuento
        )
        self.btn_descuento.pack(side="left", fill="x", expand=True, padx=(5, 0), ipady=8)

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
            bg=BLANCO, relief="solid", bd=1, cursor="hand2", command=self.guardar_pedido
        ).pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=7)

        tk.Button(
            abajo, text="Cancelar", font=("Segoe UI", 10), bg=BLANCO,
            relief="solid", bd=1, cursor="hand2", command=self.cancelar
        ).pack(side="left", fill="x", expand=True, padx=(5, 0), ipady=7)

    # ========================================================
    # TIPO DE PEDIDO (MESA / PARA LLEVAR)
    # ========================================================

    def elegir_mesa(self):
        """Al presionar el botón de mesa se despliega un selector
        con los números de mesa disponibles, con el mismo estilo
        del resto de la app (no el menú gris del sistema
        operativo). La mesa actualmente elegida (Mesa 1 por
        defecto) queda resaltada en rojo."""

        ventana = tk.Toplevel(self)
        ventana.overrideredirect(True)
        ventana.configure(bg=BORDE)
        ventana.attributes("-topmost", True)

        contenedor = tk.Frame(ventana, bg=BLANCO)
        contenedor.pack(padx=1, pady=1)

        tk.Label(
            contenedor, text="Selecciona una mesa", font=("Segoe UI", 11, "bold"),
            fg=TEXTO, bg=BLANCO
        ).pack(anchor="w", padx=15, pady=(12, 8))

        cuadricula = tk.Frame(contenedor, bg=BLANCO)
        cuadricula.pack(padx=15, pady=(0, 15))

        columnas = 4

        for indice, numero in enumerate(range(1, 13)):

            activo = self.tipo_pedido == "mesa" and numero == self.numero_mesa

            boton = tk.Button(
                cuadricula, text=str(numero), font=("Segoe UI", 12, "bold"),
                width=4, height=2, relief="flat", bd=0, cursor="hand2",
                bg=ROJO_CLARO if activo else CREMA,
                fg="white" if activo else TEXTO,
                activebackground=ROJO, activeforeground="white",
                command=lambda n=numero: self._elegir_mesa_y_cerrar(n, ventana)
            )
            boton.grid(row=indice // columnas, column=indice % columnas, padx=4, pady=4)

        ventana.update_idletasks()

        x = self.btn_tipo_mesa.winfo_rootx()
        y = self.btn_tipo_mesa.winfo_rooty() + self.btn_tipo_mesa.winfo_height() + 4
        ventana.geometry(f"+{x}+{y}")

        ventana.bind("<FocusOut>", lambda e: ventana.destroy())
        ventana.focus_force()

    def _elegir_mesa_y_cerrar(self, numero, ventana):

        self._set_mesa(numero)
        ventana.destroy()

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
    # MODIFICADORES (mostrar/ocultar notas del pedido)
    # ========================================================

    def _alternar_notas(self):

        self._notas_visibles = not self._notas_visibles

        if self._notas_visibles:
            self.entrada_notas.pack(fill="x", padx=25, pady=5, after=self.btn_modificadores)
            self.btn_modificadores.configure(text="Modificadores                         ⌃")
        else:
            self.entrada_notas.pack_forget()
            self.btn_modificadores.configure(text="Modificadores                         ⌄")

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
            "cantidad": 1
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

        for item in self.carrito:

            subtotal = item["precio"] * item["cantidad"]

            fila = tk.Frame(self.lista_carrito, bg=BLANCO)
            fila.pack(fill="x", pady=8)

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

        subtotal_total, descuento_monto, total = self._calcular_totales()

        if descuento_monto > 0:

            fila_descuento = tk.Frame(self.lista_carrito, bg=BLANCO)
            fila_descuento.pack(fill="x", pady=(4, 0))

            texto_descuento = (
                f"Descuento ({self.descuento_valor:.0f}%)"
                if self.descuento_tipo == "porcentaje"
                else "Descuento"
            )

            tk.Label(
                fila_descuento, text=texto_descuento, font=("Segoe UI", 10),
                fg=VERDE, bg=BLANCO
            ).pack(side="left")

            tk.Label(
                fila_descuento, text=f"-Q{descuento_monto:.2f}", font=("Segoe UI", 10, "bold"),
                fg=VERDE, bg=BLANCO
            ).pack(side="right")

        self.btn_descuento.configure(
            text="%\nQuitar Descuento" if descuento_monto > 0 else "%\nAplicar Descuento"
        )

        self.lbl_total.configure(text=f"Total:                    Q{total:.2f}")
        self.btn_pagar.configure(text=f"Pagar: Q{total:.2f}")

    def _calcular_totales(self):
        """Devuelve (subtotal, monto_descontado, total) del
        carrito actual, aplicando el descuento activo (si hay)."""

        subtotal = sum(item["precio"] * item["cantidad"] for item in self.carrito)

        if self.descuento_tipo == "porcentaje":
            descuento_monto = subtotal * (self.descuento_valor / 100)
        elif self.descuento_tipo == "monto":
            descuento_monto = self.descuento_valor
        else:
            descuento_monto = 0.0

        descuento_monto = max(0.0, min(descuento_monto, subtotal))
        total = round(subtotal - descuento_monto, 2)

        return round(subtotal, 2), round(descuento_monto, 2), total

    # ========================================================
    # APLICAR DESCUENTO
    # ========================================================

    def abrir_descuento(self):

        if not self.carrito:
            messagebox.showwarning("Mr.Burger", "No hay productos en el pedido.")
            return

        ventana = tk.Toplevel(self)
        ventana.title("Aplicar Descuento")
        ventana.configure(bg=BLANCO)
        ventana.resizable(False, False)
        ventana.transient(self)
        ventana.grab_set()
        ventana.geometry("340x320")

        tk.Label(
            ventana, text="Aplicar Descuento", font=("Segoe UI", 14, "bold"),
            fg=TEXTO, bg=BLANCO
        ).pack(pady=(20, 15))

        tipo_var = tk.StringVar(value=self.descuento_tipo or "porcentaje")

        opciones = tk.Frame(ventana, bg=BLANCO)
        opciones.pack(pady=(0, 15))

        btn_porcentaje = tk.Button(
            opciones, text="% Porcentaje", font=("Segoe UI", 10, "bold"),
            relief="solid", bd=1, cursor="hand2",
            command=lambda: elegir_tipo("porcentaje")
        )
        btn_porcentaje.pack(side="left", padx=5, ipady=6, ipadx=8)

        btn_monto = tk.Button(
            opciones, text="Q Monto fijo", font=("Segoe UI", 10, "bold"),
            relief="solid", bd=1, cursor="hand2",
            command=lambda: elegir_tipo("monto")
        )
        btn_monto.pack(side="left", padx=5, ipady=6, ipadx=8)

        def refrescar_botones_tipo():
            btn_porcentaje.configure(
                bg=ROJO_CLARO if tipo_var.get() == "porcentaje" else BLANCO,
                fg="white" if tipo_var.get() == "porcentaje" else TEXTO
            )
            btn_monto.configure(
                bg=ROJO_CLARO if tipo_var.get() == "monto" else BLANCO,
                fg="white" if tipo_var.get() == "monto" else TEXTO
            )

        def elegir_tipo(valor):
            tipo_var.set(valor)
            refrescar_botones_tipo()

        tk.Label(
            ventana, text="Valor del descuento", font=("Segoe UI", 10),
            fg=TEXTO, bg=BLANCO
        ).pack(anchor="w", padx=30)

        entrada_valor = tk.Entry(ventana, font=("Segoe UI", 13), bd=1, relief="solid")
        entrada_valor.pack(fill="x", padx=30, pady=(3, 15), ipady=6)

        if self.descuento_tipo:
            entrada_valor.insert(0, f"{self.descuento_valor:g}")

        refrescar_botones_tipo()

        def aplicar():

            try:
                valor = float(entrada_valor.get())
            except ValueError:
                messagebox.showwarning("Mr.Burger", "Ingresa un valor válido.", parent=ventana)
                return

            if valor < 0:
                messagebox.showwarning("Mr.Burger", "El descuento no puede ser negativo.", parent=ventana)
                return

            if tipo_var.get() == "porcentaje" and valor > 100:
                messagebox.showwarning("Mr.Burger", "El porcentaje no puede ser mayor a 100.", parent=ventana)
                return

            self.descuento_tipo = tipo_var.get()
            self.descuento_valor = valor

            self.actualizar_resumen()
            ventana.destroy()

        def quitar():
            self.descuento_tipo = None
            self.descuento_valor = 0.0
            self.actualizar_resumen()
            ventana.destroy()

        botones = tk.Frame(ventana, bg=BLANCO)
        botones.pack(fill="x", padx=30, pady=(5, 20))

        tk.Button(
            botones, text="Quitar", font=("Segoe UI", 10), bg=BLANCO,
            relief="solid", bd=1, cursor="hand2", command=quitar
        ).pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=8)

        tk.Button(
            botones, text="Aplicar", font=("Segoe UI", 10, "bold"), bg=ROJO_CLARO,
            fg="white", activebackground=ROJO, activeforeground="white",
            relief="flat", cursor="hand2", command=aplicar
        ).pack(side="left", fill="x", expand=True, padx=(5, 0), ipady=8)

    # ========================================================
    # DIVIDIR CUENTA
    # ========================================================

    def dividir_cuenta(self):

        if not self.carrito:
            messagebox.showwarning("Mr.Burger", "No hay productos en el pedido.")
            return

        if sum(item["cantidad"] for item in self.carrito) < 2:
            messagebox.showwarning(
                "Mr.Burger",
                "Se necesita más de un producto (o más de una unidad) para poder dividir la cuenta."
            )
            return

        VentanaDividirCuenta(self, self.carrito, self._iniciar_cuentas_divididas)

    def _iniciar_cuentas_divididas(self, cuentas):

        self._en_division = True
        self._cuentas_pendientes = list(cuentas)
        self._cuenta_num_total = len(cuentas)
        self._cuenta_num_actual = 0

        self._procesar_siguiente_cuenta()

    def _procesar_siguiente_cuenta(self):

        if not self._cuentas_pendientes:

            self._en_division = False
            self._cuenta_num_actual = 0
            self._cuenta_num_total = 0

            messagebox.showinfo(
                "Dividir Cuenta", "Todas las cuentas fueron cobradas correctamente."
            )

            self._limpiar_pedido_actual()
            return

        self._cuenta_num_actual += 1
        self.carrito = self._cuentas_pendientes.pop(0)

        self.actualizar_resumen()

        messagebox.showinfo(
            "Dividir Cuenta",
            f"Cobrando la cuenta {self._cuenta_num_actual} de {self._cuenta_num_total}."
        )

        self.pagar()

    # ========================================================
    # GUARDAR PEDIDO (sin cobrar todavía)
    # ========================================================

    def guardar_pedido(self):

        if not self.carrito:
            messagebox.showwarning("Mr.Burger", "No hay productos en el pedido.")
            return

        notas_texto = self.entrada_notas.get("1.0", "end").strip()

        if notas_texto == "Notas":
            notas_texto = ""

        pedido = {
            "id_usuario": getattr(self.controlador, "id_usuario", None),
            "cajero": self.controlador.cajero_actual,
            "tipo_pedido": self.tipo_pedido,
            "mesa": self.numero_mesa if self.tipo_pedido == "mesa" else None,
            "notas": notas_texto or None,
            "items": [
                {
                    "id": item.get("id"),
                    "nombre": item["nombre"],
                    "precio": item["precio"],
                    "cantidad": item["cantidad"],
                }
                for item in self.carrito
            ],
        }

        try:
            id_pedido = datos_ventas.guardar_pedido_pendiente(pedido)
        except ErrorBaseDatos as error:
            messagebox.showerror("No se pudo guardar el pedido", str(error))
            return

        messagebox.showinfo(
            "Pedido guardado",
            f"El pedido #{id_pedido} quedó guardado sin cobrar todavía.\n"
            "Puedes atenderlo más tarde desde Pedidos, en el Panel de Administrador."
        )

        self._limpiar_pedido_actual()

    # ========================================================
    # PAGAR
    # ========================================================

    def pagar(self):

        if not self.carrito:
            messagebox.showwarning("Mr.Burger", "No hay productos en el pedido.")
            return

        _, _, total = self._calcular_totales()

        VentanaMetodoPago(self.controlador, total, self._finalizar_venta)

    # ========================================================
    # FINALIZAR VENTA (tras elegir método de pago)
    # ========================================================

    def _finalizar_venta(self, metodo, detalle):

        subtotal, descuento_monto, total = self._calcular_totales()

        notas_texto = self.entrada_notas.get("1.0", "end").strip()

        if notas_texto == "Notas":
            notas_texto = ""

        # ----------------------------------------------------
        # REGISTRAR LA VENTA EN LA BASE DE DATOS
        # ----------------------------------------------------
        # Esto crea el pedido, agrega cada producto, registra el
        # o los pagos y confirma el pedido (sp_confirmar_pedido),
        # que a su vez valida y descuenta el inventario real
        # dentro de MySQL, ya aplicando el descuento (requiere la
        # migración migraciones/004_descuento_y_pendientes.sql).
        # Si algo falla (por ejemplo, no hay inventario
        # suficiente) no se guarda nada y se avisa al cajero sin
        # perder el carrito.
        # ----------------------------------------------------

        venta = {
            "id_usuario": getattr(self.controlador, "id_usuario", None),
            "cajero": self.controlador.cajero_actual,
            "tipo_pedido": self.tipo_pedido,
            "mesa": self.numero_mesa if self.tipo_pedido == "mesa" else None,
            "notas": notas_texto or None,
            "metodo_pago": metodo,
            "detalle_pago": detalle,
            "descuento": descuento_monto,
            "items": [
                {
                    "id": item.get("id"),
                    "nombre": item["nombre"],
                    "precio": item["precio"],
                    "cantidad": item["cantidad"],
                }
                for item in self.carrito
            ],
            "total": total
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

        prefijo_mensaje = (
            f"Cuenta {self._cuenta_num_actual} de {self._cuenta_num_total} cobrada.\n\n"
            if self._en_division else ""
        )

        mensaje = (
            f"{prefijo_mensaje}"
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

        if self._en_division:
            # El descuento (si había) ya se aplicó a esta primera
            # cuenta cobrada; se limpia para no volver a aplicarlo
            # a las cuentas que faltan del mismo pedido.
            self.descuento_tipo = None
            self.descuento_valor = 0.0

            self._procesar_siguiente_cuenta()
            return

        self._limpiar_pedido_actual()

    # ========================================================
    # LIMPIAR EL PEDIDO ACTUAL (tras cobrar o guardar)
    # ========================================================

    def _limpiar_pedido_actual(self):

        self.carrito.clear()
        self.descuento_tipo = None
        self.descuento_valor = 0.0

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

            if self._en_division:
                self._en_division = False
                self._cuentas_pendientes = []
                self._cuenta_num_actual = 0
                self._cuenta_num_total = 0

            self._limpiar_pedido_actual()
