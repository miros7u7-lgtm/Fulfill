import re

from psycopg.errors import UniqueViolation
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database import conectar_bd

def validar_correo(correo):
    if not isinstance(correo, str):
        raise ValueError("El correo electrónico es obligatorio.")

    correo = correo.strip().lower()

    if len(correo) > 150:
        raise ValueError("El correo es demasiado largo.")

    patron = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"

    if not re.fullmatch(patron, correo):
        raise ValueError("Introduce un correo electrónico válido.")

    return correo


def validar_password(password):
    if not isinstance(password, str):
        raise ValueError("La contraseña es obligatoria.")

    if len(password) < 8:
        raise ValueError(
            "La contraseña debe tener al menos 8 caracteres."
        )

    if len(password) > 128:
        raise ValueError(
            "La contraseña no puede superar 128 caracteres."
        )

    return password

def registrar_usuario(nombre, correo, password):

    if not isinstance(nombre, str) or not nombre.strip():
        raise ValueError("El nombre es obligatorio.")

    nombre = nombre.strip()

    if len(nombre) > 100:
        raise ValueError(
            "El nombre no puede superar 100 caracteres."
        )

    correo = validar_correo(correo)
    password = validar_password(password)

    hash_seguro = generate_password_hash(
        password,
        method="scrypt"
    )

    with conectar_bd() as conexion:
        with conexion.cursor() as cursor:

            # Verificar correo existente sin importar mayúsculas.
            cursor.execute("""
                SELECT id_usuario
                FROM usuarios
                WHERE LOWER(correo) = %s;
            """, (correo,))

            if cursor.fetchone() is not None:
                raise ValueError(
                    "No se pudo registrar la cuenta con ese correo."
                )

            try:
                cursor.execute("""
                    INSERT INTO usuarios (
                        nombre,
                        correo,
                        password_hash,
                        rol
                    )
                    VALUES (%s, %s, %s, 'estudiante')
                    RETURNING
                        id_usuario,
                        nombre,
                        correo,
                        rol;
                """, (
                    nombre,
                    correo,
                    hash_seguro
                ))

                usuario = cursor.fetchone()

            except UniqueViolation:
                raise ValueError(
                    "No se pudo registrar la cuenta con ese correo."
                )

    return {
        "usuario": usuario,
        "mensaje": "Cuenta registrada correctamente."
    }

def autenticar_usuario(correo, password):

    correo = validar_correo(correo)

    if not isinstance(password, str) or not password:
        raise ValueError(
            "Correo o contraseña incorrectos."
        )

    with conectar_bd() as conexion:
        with conexion.cursor() as cursor:

            cursor.execute("""
                SELECT
                    id_usuario,
                    nombre,
                    correo,
                    password_hash,
                    rol
                FROM usuarios
                WHERE LOWER(correo) = %s;
            """, (correo,))

            usuario = cursor.fetchone()

    if usuario is None:
        raise ValueError(
            "Correo o contraseña incorrectos."
        )

    try:
        password_correcto = check_password_hash(
            usuario["password_hash"],
            password
        )
    except (ValueError, TypeError):
        password_correcto = False

    if not password_correcto:
        raise ValueError(
            "Correo o contraseña incorrectos."
        )

    return {
        "id_usuario": usuario["id_usuario"],
        "nombre": usuario["nombre"],
        "correo": usuario["correo"],
        "rol": usuario["rol"]
    }

def obtener_usuario(id_usuario):

    if (
        not isinstance(id_usuario, int)
        or isinstance(id_usuario, bool)
        or id_usuario <= 0
    ):
        raise ValueError("Identificador de usuario inválido.")

    with conectar_bd() as conexion:
        with conexion.cursor() as cursor:

            cursor.execute("""
                SELECT
                    id_usuario,
                    nombre,
                    correo,
                    rol
                FROM usuarios
                WHERE id_usuario = %s;
            """, (id_usuario,))

            return cursor.fetchone()
