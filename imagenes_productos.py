"""
imagenes_productos.py
======================
Busca automáticamente la foto de un producto dentro de la carpeta
Recursos/productos/, comparando el NOMBRE del producto contra los
nombres de los archivos de imagen que haya en esa carpeta.

Idea de uso (flujo pensado para que sea simple de mantener):

  - Todas las imágenes de referencia se dejan sueltas en
    Recursos/productos/ (jpg, jpeg o png). No hace falta anotar en
    ningún lado "este producto usa este archivo".
  - Si creas un producto y todavía no existe una imagen con un
    nombre parecido, el producto se muestra igual, solo que sin foto
    (se usa su emoji como respaldo). No es un error.
  - Si después agregas a la carpeta un archivo cuyo nombre se parece
    al del producto (p. ej. "Hamburguesa Clásica" y
    "HamburguesaClasica.png"), la próxima vez que se abra el punto de
    venta esa foto aparece junto al producto automáticamente.
  - Si dejas una imagen en la carpeta pero ningún producto tiene un
    nombre parecido, esa imagen simplemente no se usa en ningún lado
    (no aparece nada por ella sola).

La comparación de nombres ignora mayúsculas/minúsculas, acentos,
espacios y signos de puntuación, y tolera pequeñas diferencias de
redacción (p. ej. paréntesis, "Mr." vs "Mr", etc.) usando similitud
de texto en vez de exigir una coincidencia exacta.
"""

import os
import re
import unicodedata
import difflib

# Carpeta raíz del proyecto (un nivel arriba de este archivo).
RAIZ_PROYECTO = os.path.dirname(os.path.abspath(__file__))
CARPETA_IMAGENES = os.path.join(RAIZ_PROYECTO, "Recursos", "productos")

EXTENSIONES_VALIDAS = (".jpg", ".jpeg", ".png")

# Qué tan parecidos deben ser el nombre del producto y el nombre del
# archivo para considerarlo "la misma imagen" (0 = nada parecido,
# 1 = idéntico). 0.70 tolera diferencias razonables sin generar
# coincidencias falsas entre productos distintos.
UMBRAL_SIMILITUD = 0.70


def _normalizar(texto):
    """Deja solo letras y números en minúscula, sin acentos ni
    espacios, para poder comparar 'Hamburguesa Clásica' contra
    'HamburguesaClasica.png' sin que estorben esos detalles."""

    texto = os.path.splitext(texto)[0]  # quita la extensión si la trae
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = texto.lower()
    return re.sub(r"[^a-z0-9]", "", texto)


def _listar_archivos_de_imagenes():
    """Devuelve la lista de archivos de imagen presentes en
    Recursos/productos/ (vacía si la carpeta no existe todavía)."""

    if not os.path.isdir(CARPETA_IMAGENES):
        return []

    return [
        f for f in os.listdir(CARPETA_IMAGENES)
        if f.lower().endswith(EXTENSIONES_VALIDAS)
    ]


def buscar_imagen_de_producto(nombre_producto):
    """Busca en Recursos/productos/ el archivo cuyo nombre se parezca
    más al nombre del producto. Devuelve la ruta relativa al proyecto
    (ej. "Recursos/productos/HamburguesaClasica.png") si encuentra
    una coincidencia razonable, o None si no hay ninguna imagen
    suficientemente parecida (el producto simplemente no tendrá
    foto)."""

    if not nombre_producto:
        return None

    objetivo = _normalizar(nombre_producto)
    mejor_archivo = None
    mejor_puntaje = 0.0

    for archivo in _listar_archivos_de_imagenes():
        puntaje = difflib.SequenceMatcher(None, objetivo, _normalizar(archivo)).ratio()
        if puntaje > mejor_puntaje:
            mejor_puntaje = puntaje
            mejor_archivo = archivo

    if mejor_archivo is None or mejor_puntaje < UMBRAL_SIMILITUD:
        return None

    return os.path.join("Recursos", "productos", mejor_archivo).replace("\\", "/")
