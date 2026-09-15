"""
ingredientes.py
------------------------------------------------------------
Ingredientes que el cajero puede quitarle a un producto al
personalizarlo desde el carrito del Punto de Venta (por ejemplo,
quitarle el tomate o la cebolla a una hamburguesa).

*** IMPORTANTE PARA QUIEN CONECTE ESTO A LA BASE DE DATOS ***
Por ahora estos ingredientes NO viven en MySQL: son una lista de
respaldo/ejemplo para que la interfaz ya funcione mientras se
agrega una tabla real (algo como "producto_ingrediente", con sus
ingredientes por producto).

Cuando esa tabla exista, basta con reemplazar el cuerpo de
obtener_ingredientes_editables() de este archivo por una consulta
real (por ejemplo, una nueva función en
basedatos/repositorio_productos.py, algo como
listar_ingredientes(id_producto)). Ni panel_carrito.py ni
dialogo_personalizar.py necesitan cambiar, porque los dos solo
llaman a esta función.
------------------------------------------------------------
"""


# Ingredientes típicos que se pueden quitar, agrupados por tipo de
# producto. Se usan como respaldo cuando el producto todavía no
# tiene su propia lista definida en _INGREDIENTES_POR_PRODUCTO.
_INGREDIENTES_POR_TIPO = {
    "hamburguesas": [
        "Lechuga", "Tomate", "Cebolla", "Pepinillos",
        "Queso", "Tocino", "Mayonesa", "Mostaza", "Catsup",
    ],
    "combos": [
        "Lechuga", "Tomate", "Cebolla", "Pepinillos",
        "Queso", "Tocino", "Mayonesa", "Mostaza", "Catsup",
    ],
    "desayunos": [
        "Queso", "Tocino", "Jamón", "Cebolla", "Tomate", "Crema",
    ],
    "extras": [
        "Sal", "Queso extra", "Salsa de tocino",
    ],
    "bebidas": [
        "Hielo", "Azúcar",
    ],
}

# Si algún día se necesita afinar un producto en particular sin
# esperar a la base de datos, se puede agregar aquí su nombre
# exacto (tal como aparece en la tabla productos) con su propia
# lista de ingredientes. Tiene prioridad sobre _INGREDIENTES_POR_TIPO.
_INGREDIENTES_POR_PRODUCTO = {
    # "Hamburguesa Clásica": ["Carne", "Queso", "Lechuga", "Tomate", "Cebolla"],
}


def _tipo_de_categoria(categoria):
    """Agrupa las categorías reales de la base de datos (p. ej.
    'Combos Pareja', 'Extras y Acompañamientos') en los tipos
    genéricos usados arriba."""

    categoria = (categoria or "").strip().lower()

    if categoria.startswith("hamburguesa"):
        return "hamburguesas"
    if categoria.startswith("combo"):
        return "combos"
    if categoria.startswith("desayuno"):
        return "desayunos"
    if categoria.startswith("extra"):
        return "extras"
    if categoria.startswith("bebida"):
        return "bebidas"

    return categoria


def obtener_ingredientes_editables(producto):
    """Devuelve la lista de ingredientes que el cajero puede
    quitarle a este producto. Si no se conoce ninguno para ese
    producto (por ejemplo, una gaseosa embotellada), devuelve una
    lista vacía y el diálogo de personalización solo deja escribir
    instrucciones especiales."""

    nombre = (producto.get("nombre") or "").replace("\n", " ").strip()

    if nombre in _INGREDIENTES_POR_PRODUCTO:
        return list(_INGREDIENTES_POR_PRODUCTO[nombre])

    tipo = _tipo_de_categoria(producto.get("categoria"))

    return list(_INGREDIENTES_POR_TIPO.get(tipo, []))
