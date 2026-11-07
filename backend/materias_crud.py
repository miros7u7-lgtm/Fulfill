import os
from pathlib import Path

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

RUTA_ENV = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(RUTA_ENV)


def conectar_bd():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        connect_timeout=5,
        row_factory=dict_row
    )

def actualizar_materia(
    id_materia,
    id_usuario,
    nombre,
    descripcion
):
    if not isinstance(id_materia, int) or isinstance(id_materia, bool) or id_materia <= 0:
        raise ValueError("El identificador de materia no es válido.")

    if not isinstance(id_usuario, int) or isinstance(id_usuario, bool) or id_usuario <= 0:
        raise ValueError("El identificador de estudiante no es válido.")

    if not isinstance(nombre, str) or not nombre.strip():
        raise ValueError("El nombre de la materia es obligatorio.")

    nombre = nombre.strip()

    if len(nombre) > 100:
        raise ValueError("El nombre no puede superar 100 caracteres.")

    if not isinstance(descripcion, str):
        raise ValueError("La descripción debe ser texto.")

    with conectar_bd() as conexion:
        with conexion.cursor() as cursor:

            # Comprobar que la materia exista y pertenezca al estudiante
            cursor.execute("""
                SELECT id_materia
                FROM materias
                WHERE id_materia = %s
                  AND id_usuario = %s
                  AND eliminado = FALSE
                FOR UPDATE;
            """, (id_materia, id_usuario))

            if cursor.fetchone() is None:
                raise ValueError(
                    "La materia no existe o no pertenece al estudiante."
                )

            # que no haya estudiantes duplicados con el mismo nombre 
            cursor.execute("""
                SELECT id_materia
                FROM materias
                WHERE id_usuario = %s
                  AND LOWER(nombre) = LOWER(%s)
                  AND id_materia <> %s
                  AND eliminado = FALSE;
            """, (id_usuario, nombre, id_materia))

            if cursor.fetchone() is not None:
                raise ValueError(
                    "Ya tienes otra materia activa con ese nombre."
                )

            cursor.execute("""
                UPDATE materias
                SET
                    nombre = %s,
                    descripcion = %s
                WHERE id_materia = %s
                  AND id_usuario = %s
                  AND eliminado = FALSE
                RETURNING id_materia, nombre, descripcion;
            """, (
                nombre,
                descripcion.strip(),
                id_materia,
                id_usuario
            ))

            resultado = cursor.fetchone()

        conexion.commit()

    return {
        **resultado,
        "mensaje": "Materia actualizada correctamente."
    }

def eliminar_materia(id_materia, id_usuario):

    if not isinstance(id_materia, int) or isinstance(id_materia, bool) or id_materia <= 0:
        raise ValueError("El identificador de materia no es válido.")

    if not isinstance(id_usuario, int) or isinstance(id_usuario, bool) or id_usuario <= 0:
        raise ValueError("El identificador de estudiante no es válido.")

    with conectar_bd() as conexion:
        with conexion.cursor() as cursor:

            cursor.execute("""
                UPDATE materias
                SET eliminado = TRUE
                WHERE id_materia = %s
                  AND id_usuario = %s
                  AND eliminado = FALSE
                RETURNING id_materia, nombre;
            """, (id_materia, id_usuario))

            resultado = cursor.fetchone()

            if resultado is None:
                raise ValueError(
                    "La materia no existe, ya fue eliminada "
                    "o no pertenece al estudiante."
                )

        conexion.commit()

    return {
        "id_materia": resultado["id_materia"],
        "nombre": resultado["nombre"],
        "mensaje": "Materia eliminada correctamente."
    }
