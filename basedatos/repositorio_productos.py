"""
el crud del proyecto
"""

import mysql.connector

from .conexion import obtener_conexion, ErrorBaseDatos


ICONOS_CATEGORIA = {
    "comida": "🍔",
    "bebidas": "🥤",
    "postres": "🍰",
    "combos": "🍟",
}
ICONO_CATEGORIA_DEFECTO = "🍽"

PERIODOS = ["desayuno", "almuerzo"]
METODOS_PAGO = {"efectivo": "Efectivo", "tarjeta": "Tarjeta", "mixto": "Mixto"}


_HORA_INICIO_DESAYUNO = "07:00:00"


def _horario_de_periodo(periodo):
    if periodo == "desayuno":
        return True, "07:00:00", "11:00:00"
    return True, "11:00:00", "07:00:00"


def _periodo_de_hora_inicio(hora_inicio):
    if hora_inicio is not None and str(hora_inicio).startswith("07:"):
        return "desayuno"
    return "almuerzo"


_SELECT_BASE = """
    SELECT p.id_producto, p.nombre_producto, p.descripcion, p.emoji, p.precio,
           p.hora_inicio, c.nombre_categoria,
           (SELECT MIN(FLOOR(inv.cantidad_actual / pi.cantidad_requerida))
              FROM producto_insumo pi
              JOIN inventario inv ON inv.id_insumo = pi.id_insumo
             WHERE pi.id_producto = p.id_producto) AS stock
      FROM productos p
      JOIN categorias c ON c.id_categoria = p.id_categoria
"""


def _fila_a_producto(fila):

    stock = fila["stock"]

    return {
        "id": fila["id_producto"],
        "nombre": fila["nombre_producto"],
        "descripcion": fila["descripcion"] or "",
        "emoji": fila["emoji"] or ICONO_CATEGORIA_DEFECTO,
        "precio": float(fila["precio"]),
        "stock": int(stock) if stock is not None else 0,
        "categoria": fila["nombre_categoria"],
        "periodo": _periodo_de_hora_inicio(fila["hora_inicio"]),
    }


# CATEGORÍAS


def listar_categorias():

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("SELECT nombre_categoria FROM categorias ORDER BY nombre_categoria")
        return [fila[0] for fila in cursor.fetchall()]

    finally:
        cursor.close()
        conexion.close()


def agregar_categoria(nombre):

    nombre = (nombre or "").strip().lower()

    if not nombre:
        return False, "Ingresa un nombre."

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("SELECT 1 FROM categorias WHERE nombre_categoria = %s", (nombre,))

        if cursor.fetchone():
            return False, "Esa categoría ya existe."

        cursor.execute("INSERT INTO categorias (nombre_categoria) VALUES (%s)", (nombre,))
        conexion.commit()
        return True, None

    except mysql.connector.Error as error:
        conexion.rollback()
        return False, f"No se pudo guardar la categoría: {error}"

    finally:
        cursor.close()
        conexion.close()


def eliminar_categoria(categoria):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute(
            """SELECT COUNT(*) FROM productos p
                 JOIN categorias c ON c.id_categoria = p.id_categoria
                WHERE c.nombre_categoria = %s""",
            (categoria,)
        )
        en_uso = cursor.fetchone()[0]

        if en_uso:
            return False, (
                f"La categoría \"{categoria}\" tiene {en_uso} producto(s) "
                "asociado(s). Elimina o reasigna esos productos primero."
            )

        cursor.execute("DELETE FROM categorias WHERE nombre_categoria = %s", (categoria,))
        conexion.commit()
        return True, None

    except mysql.connector.Error as error:
        conexion.rollback()
        return False, f"No se pudo eliminar la categoría: {error}"

    finally:
        cursor.close()
        conexion.close()


def _id_categoria(cursor, nombre_categoria):

    cursor.execute("SELECT id_categoria FROM categorias WHERE nombre_categoria = %s", (nombre_categoria,))
    fila = cursor.fetchone()

    if fila is None:
        raise ErrorBaseDatos(f"La categoría \"{nombre_categoria}\" no existe.")

    return fila[0]



# PRODUCTOS

def listar_productos(categoria="todas", periodo="todos", busqueda=""):


    condiciones = []
    parametros = []

    if categoria not in (None, "todas"):
        condiciones.append("c.nombre_categoria = %s")
        parametros.append(categoria)

    if periodo not in (None, "todos"):
        if periodo == "desayuno":
            condiciones.append("p.hora_inicio = %s")
            parametros.append(_HORA_INICIO_DESAYUNO)
        else:
            condiciones.append("(p.hora_inicio IS NULL OR p.hora_inicio <> %s)")
            parametros.append(_HORA_INICIO_DESAYUNO)

    busqueda = (busqueda or "").strip()

    if busqueda:
        condiciones.append("p.nombre_producto LIKE %s")
        parametros.append(f"%{busqueda}%")

    consulta = _SELECT_BASE

    if condiciones:
        consulta += " WHERE " + " AND ".join(condiciones)

    consulta += " ORDER BY p.nombre_producto"

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute(consulta, parametros)
        return [_fila_a_producto(fila) for fila in cursor.fetchall()]

    finally:
        cursor.close()
        conexion.close()


def listar_disponibles(periodo):


    consulta = _SELECT_BASE + """
        WHERE p.habilitado = TRUE
          AND (
                p.restringido_horario = FALSE
                OR (p.hora_inicio <= p.hora_fin AND CURTIME() BETWEEN p.hora_inicio AND p.hora_fin)
                OR (p.hora_inicio > p.hora_fin AND (CURTIME() >= p.hora_inicio OR CURTIME() <= p.hora_fin))
          )
    """

    parametros = []

    if periodo == "desayuno":
        consulta += " AND p.hora_inicio = %s"
        parametros.append(_HORA_INICIO_DESAYUNO)
    elif periodo == "almuerzo":
        consulta += " AND (p.hora_inicio IS NULL OR p.hora_inicio <> %s)"
        parametros.append(_HORA_INICIO_DESAYUNO)

    consulta += " ORDER BY p.nombre_producto"

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute(consulta, parametros)
        return [_fila_a_producto(fila) for fila in cursor.fetchall()]

    finally:
        cursor.close()
        conexion.close()


def buscar_producto_por_id(id_producto):

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute(_SELECT_BASE + " WHERE p.id_producto = %s", (id_producto,))
        fila = cursor.fetchone()
        return _fila_a_producto(fila) if fila else None

    finally:
        cursor.close()
        conexion.close()


def _sincronizar_stock(cursor, id_producto, nombre_producto, stock):


    cursor.execute(
        "SELECT pi.id_insumo FROM producto_insumo pi WHERE pi.id_producto = %s LIMIT 1",
        (id_producto,)
    )
    fila = cursor.fetchone()

    if fila:
        cursor.execute(
            "UPDATE inventario SET cantidad_actual = %s WHERE id_insumo = %s",
            (stock, fila[0])
        )
    else:
        cursor.execute(
            """INSERT INTO inventario (nombre_insumo, unidad_medida, cantidad_actual, cantidad_minima)
               VALUES (%s, 'unidad', %s, 5)""",
            (f"Stock de {nombre_producto}", stock)
        )
        id_insumo = cursor.lastrowid

        cursor.execute(
            "INSERT INTO producto_insumo (id_producto, id_insumo, cantidad_requerida) VALUES (%s, %s, 1)",
            (id_producto, id_insumo)
        )


def agregar_producto(valores):


    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        id_categoria = _id_categoria(cursor, valores["categoria"])
        restringido, hora_inicio, hora_fin = _horario_de_periodo(valores.get("periodo", "almuerzo"))
        nombre = valores["nombre"].replace("\n", " ").strip()

        cursor.execute(
            """INSERT INTO productos
                 (nombre_producto, descripcion, emoji, precio, id_categoria,
                  tipo_producto, habilitado, restringido_horario, hora_inicio, hora_fin)
               VALUES (%s, %s, %s, %s, %s, 'platillo', TRUE, %s, %s, %s)""",
            (
                nombre, valores.get("descripcion", ""), valores.get("emoji") or ICONO_CATEGORIA_DEFECTO,
                valores["precio"], id_categoria, restringido, hora_inicio, hora_fin
            )
        )

        id_producto = cursor.lastrowid

        _sincronizar_stock(cursor, id_producto, nombre, valores.get("stock", 0))

        conexion.commit()

    except mysql.connector.Error as error:
        conexion.rollback()
        raise ErrorBaseDatos(f"No se pudo guardar el producto: {error}") from error

    finally:
        cursor.close()
        conexion.close()

    return buscar_producto_por_id(id_producto)


def actualizar_producto(id_producto, valores):


    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        id_categoria = _id_categoria(cursor, valores["categoria"])
        restringido, hora_inicio, hora_fin = _horario_de_periodo(valores.get("periodo", "almuerzo"))
        nombre = valores["nombre"].replace("\n", " ").strip()

        cursor.execute(
            """UPDATE productos
                  SET nombre_producto = %s, descripcion = %s, emoji = %s, precio = %s,
                      id_categoria = %s, restringido_horario = %s, hora_inicio = %s, hora_fin = %s
                WHERE id_producto = %s""",
            (
                nombre, valores.get("descripcion", ""), valores.get("emoji") or ICONO_CATEGORIA_DEFECTO,
                valores["precio"], id_categoria, restringido, hora_inicio, hora_fin, id_producto
            )
        )

        _sincronizar_stock(cursor, id_producto, nombre, valores.get("stock", 0))

        conexion.commit()

    except mysql.connector.Error as error:
        conexion.rollback()
        raise ErrorBaseDatos(f"No se pudo actualizar el producto: {error}") from error

    finally:
        cursor.close()
        conexion.close()

    return buscar_producto_por_id(id_producto)


def eliminar_producto(id_producto):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id_producto,))
        conexion.commit()

    except mysql.connector.Error as error:
        conexion.rollback()

        if error.errno == 1451:
            raise ErrorBaseDatos(
                "No se puede eliminar: este producto ya tiene pedidos registrados "
                "en el historial de ventas.\nPuedes editarlo y poner su stock en 0 "
                "en su lugar."
            ) from error

        raise ErrorBaseDatos(f"No se pudo eliminar el producto: {error}") from error

    finally:
        cursor.close()
        conexion.close()


# la granja de zenón

class RepositorioProductos:

    @property
    def categorias(self):
        return listar_categorias()

    @property
    def productos(self):
        return listar_productos()

    def icono_categoria(self, categoria):
        return ICONOS_CATEGORIA.get(categoria, ICONO_CATEGORIA_DEFECTO)

    def buscar_producto_por_id(self, id_producto):
        return buscar_producto_por_id(id_producto)

    def listar_productos(self, categoria="todas", periodo="todos", busqueda=""):
        return listar_productos(categoria, periodo, busqueda)

    def cantidad_por_categoria(self, categoria):
        return sum(1 for p in self.productos if p["categoria"] == categoria)

    def productos_con_poco_stock(self, limite=5):
        return [
            p for p in self.productos
            if p.get("stock") is not None and p["stock"] <= limite
        ]

    def agregar_producto(self, valores):
        return agregar_producto(valores)

    def actualizar_producto(self, id_producto, valores):
        return actualizar_producto(id_producto, valores)

    def eliminar_producto(self, id_producto):
        eliminar_producto(id_producto)

    def agregar_categoria(self, nombre):
        return agregar_categoria(nombre)

    def eliminar_categoria(self, categoria):
        return eliminar_categoria(categoria)
