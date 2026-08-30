"""
datos_admin.py
------------------------------------------------------------
Capa de datos del Panel de Administrador (inventario y
categorías).

NOTA PARA EL EQUIPO DE DESARROLLO:
Estos datos viven únicamente en memoria mientras se usa el
programa; no se guardan en ningún archivo ni base de datos.
Cuando se conecte el backend real, esta clase (RepositorioProductos)
es el único lugar que debe cambiar: sus métodos deberán hacer
consultas/actualizaciones a la base de datos (tablas de
productos, categorías e inventario) en vez de leer y escribir
las listas en memoria. Las vistas (vista_inventario.py,
vista_categorias.py, etc.) seguirán funcionando igual porque
solo hablan con estos métodos.
------------------------------------------------------------
"""

PERIODOS = ["desayuno", "almuerzo"]
METODOS_PAGO = {"efectivo": "Efectivo", "tarjeta": "Tarjeta", "mixto": "Mixto"}

CATEGORIAS_INICIALES = ["comida", "bebidas", "postres", "combos"]

ICONOS_CATEGORIA = {
    "comida": "🍔",
    "bebidas": "🥤",
    "postres": "🍰",
    "combos": "🍟",
}

ICONO_CATEGORIA_DEFECTO = "🍽"


class RepositorioProductos:
    """Guarda y consulta el catálogo de productos/categorías del
    inventario que administra el Panel de Administrador."""

    def __init__(self):

        self.categorias = list(CATEGORIAS_INICIALES)
        self.productos = []
        self._siguiente_id_valor = 1

    # --------------------------------------------------------
    # IDS
    # --------------------------------------------------------

    def siguiente_id(self):

        id_nuevo = self._siguiente_id_valor
        self._siguiente_id_valor += 1
        return id_nuevo

    # --------------------------------------------------------
    # CONSULTAS
    # --------------------------------------------------------

    def icono_categoria(self, categoria):

        return ICONOS_CATEGORIA.get(categoria, ICONO_CATEGORIA_DEFECTO)

    def buscar_producto_por_id(self, id_producto):

        for producto in self.productos:
            if producto.get("id") == id_producto:
                return producto

        return None

    def listar_productos(self, categoria="todas", periodo="todos", busqueda=""):
        """Devuelve los productos que cumplen los filtros dados.
        Con base de datos esto sería un SELECT ... WHERE."""

        busqueda = (busqueda or "").strip().lower()
        resultado = []

        for producto in self.productos:

            if categoria != "todas" and producto["categoria"] != categoria:
                continue

            if periodo != "todos" and producto["periodo"] != periodo:
                continue

            nombre_plano = producto["nombre"].replace("\n", " ")

            if busqueda and busqueda not in nombre_plano.lower():
                continue

            resultado.append(producto)

        return resultado

    def cantidad_por_categoria(self, categoria):

        return sum(1 for p in self.productos if p["categoria"] == categoria)

    def productos_con_poco_stock(self, limite=5):

        return [
            p for p in self.productos
            if p.get("stock") is not None and p["stock"] <= limite
        ]

    # --------------------------------------------------------
    # PRODUCTOS: ALTA / BAJA
    # --------------------------------------------------------

    def agregar_producto(self, valores):

        valores["id"] = self.siguiente_id()
        self.productos.append(valores)
        return valores

    def eliminar_producto(self, id_producto):

        self.productos = [p for p in self.productos if p["id"] != id_producto]

    # --------------------------------------------------------
    # CATEGORÍAS: ALTA / BAJA
    # --------------------------------------------------------

    def agregar_categoria(self, nombre):
        """Devuelve (ok, mensaje_de_error)."""

        nombre = nombre.strip().lower()

        if not nombre:
            return False, "Ingresa un nombre."

        if nombre in self.categorias:
            return False, "Esa categoría ya existe."

        self.categorias.append(nombre)
        return True, None

    def eliminar_categoria(self, categoria):
        """Devuelve (ok, mensaje_de_error)."""

        en_uso = [p for p in self.productos if p["categoria"] == categoria]

        if en_uso:
            return False, (
                f"La categoría \"{categoria}\" tiene {len(en_uso)} producto(s) "
                "asociado(s). Elimina o reasigna esos productos primero."
            )

        self.categorias = [c for c in self.categorias if c != categoria]
        return True, None
