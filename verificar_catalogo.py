"""
verificar_catalogo.py
------------------------------------------------------------
Script de diagnóstico. No modifica nada, solo muestra en la
terminal cómo está el catálogo en este momento: qué productos
existen, si cada uno encontró su imagen, y qué se mostraría en
el Punto de Venta a distintas horas del día (sin tener que
cambiar el reloj de la computadora para probarlo).

Uso:

    python verificar_catalogo.py

Requiere que la base de datos esté accesible (mismas variables
de entorno / config.py que usa el resto del proyecto).
------------------------------------------------------------
"""

from basedatos import repositorio_productos as productos
from basedatos.conexion import ErrorBaseDatos
import imagenes_productos


def _linea(caracter="-", ancho=70):
    print(caracter * ancho)


def verificar_todos_los_productos():
    """Lista cada producto de la base de datos y si se le
    encontró o no una imagen en Recursos/productos/."""

    print("\n=== TODOS LOS PRODUCTOS (sin importar el horario) ===\n")

    todos = productos.listar_productos()

    if not todos:
        print("No hay productos registrados todavía. Corre sembrar_datos.py primero.")
        return

    sin_imagen = []

    for p in todos:
        ruta = imagenes_productos.buscar_imagen_de_producto(p["nombre"])
        estado = f"imagen: {ruta}" if ruta else "SIN IMAGEN (se muestra con emoji)"
        print(f"[{p['categoria']:<12}] [{p['periodo']:<9}] {p['nombre']:<32} -> {estado}")

        if not ruta:
            sin_imagen.append(p["nombre"])

    _linea()
    print(f"Total de productos: {len(todos)}")
    print(f"Sin imagen encontrada: {len(sin_imagen)}")
    if sin_imagen:
        for nombre in sin_imagen:
            print(f"   - {nombre}")


def verificar_horarios():
    """Muestra qué productos aparecerían en el Punto de Venta a
    distintas horas del día, simulando la hora (no usa el reloj
    real de la computadora)."""

    print("\n=== SIMULACIÓN DE HORARIOS ===\n")
    print("Recordatorio de cómo está configurado el horario ahora mismo:")
    print("  - Productos con periodo 'desayuno' -> visibles SOLO de 07:00 a 10:59")
    print("  - Productos con periodo 'almuerzo' -> visibles el resto del día")
    print("    (11:00 a 06:59), es decir, TODO EL DÍA excepto ese bloque de la mañana.")
    print("  - Ningún producto está configurado para mostrarse absolutamente")
    print("    siempre (ni siquiera durante el bloque de desayuno).\n")

    horas_de_prueba = [
        ("06:30:00", "madrugada, antes del desayuno"),
        ("08:00:00", "en horario de desayuno"),
        ("11:30:00", "mediodía"),
        ("19:00:00", "noche"),
        ("23:30:00", "antes de medianoche"),
    ]

    for hora, descripcion in horas_de_prueba:
        _linea("=")
        print(f"Hora simulada: {hora}  ({descripcion})")
        _linea()

        for periodo in ("desayuno", "almuerzo"):
            disponibles = productos.listar_disponibles(periodo, hora_prueba=hora)
            nombres = ", ".join(p["nombre"] for p in disponibles) or "(ninguno)"
            print(f"  {periodo:<9}: {len(disponibles)} producto(s) -> {nombres}")


if __name__ == "__main__":
    try:
        verificar_todos_los_productos()
        verificar_horarios()
    except ErrorBaseDatos as error:
        print(f"No se pudo conectar a la base de datos: {error}")
