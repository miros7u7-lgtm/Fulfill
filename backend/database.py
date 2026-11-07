import os
from pathlib import Path
from datetime import date

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

def validar_id(valor, nombre):
    if (
        not isinstance(valor, int)
        or isinstance(valor, bool)
        or valor <= 0
    ):
        raise ValueError(f"{nombre} no es válido.")

def obtener_materias(id_usuario):
    validar_id(id_usuario, "El identificador del estudiante")

    with conectar_bd() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT
                    id_materia,
                    nombre,
                    descripcion
                FROM materias
                WHERE id_usuario = %s
                  AND eliminado = FALSE
                ORDER BY nombre;
            """, (id_usuario,))

            return cursor.fetchall()

def crear_materia(id_usuario, nombre, descripcion=""):
    validar_id(id_usuario, "El identificador del estudiante")

    if not isinstance(nombre, str) or not nombre.strip():
        raise ValueError("El nombre de la materia es obligatorio.")

    nombre = nombre.strip()

    if len(nombre) > 100:
        raise ValueError("El nombre no puede superar 100 caracteres.")

    if not isinstance(descripcion, str):
        raise ValueError("La descripción debe ser texto.")

    with conectar_bd() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT id_usuario
                FROM usuarios
                WHERE id_usuario = %s;
            """, (id_usuario,))

            if cursor.fetchone() is None:
                raise ValueError("El estudiante no existe.")

            cursor.execute("""
                SELECT id_materia
                FROM materias
                WHERE id_usuario = %s
                  AND LOWER(nombre) = LOWER(%s)
                  AND eliminado = FALSE;
            """, (id_usuario, nombre))

            if cursor.fetchone() is not None:
                raise ValueError(
                    "Ya tienes una materia activa con ese nombre."
                )

            cursor.execute("""
                INSERT INTO materias (
                    id_usuario,
                    nombre,
                    descripcion,
                    eliminado
                )
                VALUES (%s, %s, %s, FALSE)
                RETURNING id_materia;
            """, (
                id_usuario,
                nombre,
                descripcion.strip()
            ))

            resultado = cursor.fetchone()

        conexion.commit()

    return {
        "id_materia": resultado["id_materia"],
        "mensaje": "Materia registrada correctamente."
    }

def obtener_actividades(id_usuario=1):
    validar_id(id_usuario, "El identificador del estudiante")

    with conectar_bd() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT
                    a.id_actividad,
                    a.id_materia,
                    a.titulo,
                    a.descripcion,
                    m.nombre AS materia,
                    u.nombre AS estudiante,
                    a.fecha_entrega,
                    a.estado
                FROM actividades a
                INNER JOIN materias m
                    ON a.id_materia = m.id_materia
                INNER JOIN usuarios u
                    ON m.id_usuario = u.id_usuario
                WHERE a.eliminado = FALSE
                  AND m.eliminado = FALSE
                  AND m.id_usuario = %s
                ORDER BY a.id_actividad;
            """, (id_usuario,))

            actividades = cursor.fetchall()

    return [
        {
            **actividad,
            "fecha_entrega":
                actividad["fecha_entrega"].isoformat()
        }
        for actividad in actividades
    ]

def crear_actividad(
    id_materia,
    titulo,
    descripcion,
    fecha_entrega,
    id_usuario=1
):
    validar_id(id_materia, "El identificador de la materia")
    validar_id(id_usuario, "El identificador del estudiante")

    if not isinstance(titulo, str) or not titulo.strip():
        raise ValueError("El título es obligatorio.")

    titulo = titulo.strip()

    if len(titulo) > 150:
        raise ValueError("El título no puede superar 150 caracteres.")

    if not isinstance(descripcion, str):
        raise ValueError("La descripción debe ser texto.")

    if not isinstance(fecha_entrega, str):
        raise ValueError("La fecha de entrega es obligatoria.")

    try:
        fecha = date.fromisoformat(fecha_entrega)
    except ValueError:
        raise ValueError(
            "La fecha debe tener formato YYYY-MM-DD."
        )

    with conectar_bd() as conexion:
        with conexion.cursor() as cursor:
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
                    "La materia no existe, está eliminada "
                    "o no pertenece al estudiante."
                )

            cursor.execute("""
                INSERT INTO actividades (
                    id_materia,
                    titulo,
                    descripcion,
                    fecha_entrega,
                    estado,
                    eliminado
                )
                VALUES (
                    %s, %s, %s, %s,
                    'pendiente', FALSE
                )
                RETURNING id_actividad;
            """, (
                id_materia,
                titulo,
                descripcion.strip(),
                fecha
            ))

            resultado = cursor.fetchone()

        conexion.commit()

    return {
        "id_actividad": resultado["id_actividad"],
        "mensaje": "Actividad registrada correctamente."
    }

def actualizar_actividad(
    id_actividad,
    id_usuario,
    titulo,
    descripcion,
    fecha_entrega,
    estado
):
    validar_id(id_actividad, "El identificador de actividad")
    validar_id(id_usuario, "El identificador del estudiante")

    if not isinstance(titulo, str) or not titulo.strip():
        raise ValueError("El título es obligatorio.")

    titulo = titulo.strip()

    if len(titulo) > 150:
        raise ValueError("El título no puede superar 150 caracteres.")

    if not isinstance(descripcion, str):
        raise ValueError("La descripción debe ser texto.")

    if not isinstance(fecha_entrega, str):
        raise ValueError("La fecha de entrega es obligatoria.")

    try:
        fecha = date.fromisoformat(fecha_entrega)
    except ValueError:
        raise ValueError(
            "La fecha debe tener formato YYYY-MM-DD."
        )

    estados_validos = {
        "pendiente",
        "en_proceso",
        "completada"
    }

    if not isinstance(estado, str) or estado not in estados_validos:
        raise ValueError("El estado seleccionado no es válido.")

    with conectar_bd() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT a.estado
                FROM actividades a
                INNER JOIN materias m
                    ON a.id_materia = m.id_materia
                WHERE a.id_actividad = %s
                  AND m.id_usuario = %s
                  AND a.eliminado = FALSE
                  AND m.eliminado = FALSE
                FOR UPDATE OF a;
            """, (id_actividad, id_usuario))

            actividad_actual = cursor.fetchone()

            if actividad_actual is None:
                raise ValueError(
                    "La actividad no está disponible "
                    "para este estudiante."
                )

            transiciones = {
                "pendiente": {
                    "pendiente",
                    "en_proceso"
                },
                "en_proceso": {
                    "en_proceso",
                    "completada"
                },
                "completada": {
                    "completada"
                }
            }

            estado_anterior = actividad_actual["estado"]

            if estado not in transiciones.get(
                estado_anterior, set()
            ):
                raise ValueError(
                    "Cambio de estado no permitido. "
                    "Debes avanzar de pendiente a en_proceso "
                    "y después a completada."
                )

            cursor.execute("""
                UPDATE actividades
                SET
                    titulo = %s,
                    descripcion = %s,
                    fecha_entrega = %s,
                    estado = %s,
                    fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id_actividad = %s
                  AND eliminado = FALSE
                RETURNING id_actividad, estado;
            """, (
                titulo,
                descripcion.strip(),
                fecha,
                estado,
                id_actividad
            ))

            resultado = cursor.fetchone()

        conexion.commit()

    return {
        "id_actividad": resultado["id_actividad"],
        "estado": resultado["estado"],
        "mensaje": "Actividad actualizada correctamente."
    }

def eliminar_actividad(id_actividad, id_usuario):
    validar_id(id_actividad, "El identificador de actividad")
    validar_id(id_usuario, "El identificador del estudiante")

    with conectar_bd() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("""
                UPDATE actividades AS a
                SET
                    eliminado = TRUE,
                    fecha_actualizacion = CURRENT_TIMESTAMP
                FROM materias AS m
                WHERE a.id_materia = m.id_materia
                  AND a.id_actividad = %s
                  AND m.id_usuario = %s
                  AND m.eliminado = FALSE
                  AND a.eliminado = FALSE
                RETURNING a.id_actividad;
            """, (id_actividad, id_usuario))

            resultado = cursor.fetchone()

            if resultado is None:
                raise ValueError(
                    "La actividad no existe, ya fue eliminada "
                    "o no pertenece al estudiante."
                )

        conexion.commit()

    return {
        "id_actividad": resultado["id_actividad"],
        "mensaje": "Actividad eliminada correctamente."
    }
