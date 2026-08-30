"""
seguridad de contraseñas a sabiendas que no se puede usar correos
esta cosa va a parte por lo que investigué

3.14159265358979323846264338327950

"""

import hashlib
import hmac
import os

ITERACIONES = 200_000


def generar_hash(password):
    """Genera hash nuevo al crear o cambiar contraseña"""

    sal = os.urandom(16)
    derivado = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), sal, ITERACIONES
    )

    return f"{sal.hex()}${derivado.hex()}"


def verificar_password(password, hash_guardado):
    """Compara hash hecho texto plano"""

    if not password or not hash_guardado or "$" not in hash_guardado:
        return False

    try:
        sal_hex, derivado_hex = hash_guardado.split("$", 1)
        sal = bytes.fromhex(sal_hex)
        derivado_esperado = bytes.fromhex(derivado_hex)
    except (ValueError, AttributeError):
        return False

    derivado_actual = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), sal, ITERACIONES
    )

    return hmac.compare_digest(derivado_actual, derivado_esperado)
