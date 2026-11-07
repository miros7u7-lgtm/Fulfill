import os

from pathlib import Path
from datetime import timedelta
from functools import wraps

from dotenv import load_dotenv

from flask import (
    Flask,
    jsonify,
    request,
    send_from_directory,
    g,
    session,
    redirect
)

from psycopg import Error as PostgreSQLError
from psycopg.errors import UniqueViolation
from pymongo.errors import PyMongoError

from mongo import registrar_movimiento
from auth_routes import auth_bp, login_requerido
from usuarios import obtener_usuario
from admin import obtener_resumen_admin

from database import (
    obtener_actividades,
    crear_actividad,
    actualizar_actividad,
    eliminar_actividad,
    obtener_materias,
    crear_materia
)

from materias_crud import (
    actualizar_materia,
    eliminar_materia
)

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND = BASE_DIR / "frontend"

load_dotenv(BASE_DIR / ".env")

app = Flask(
    __name__,
    static_folder=str(FRONTEND),
    static_url_path=""
)

secret_key = os.getenv("SECRET_KEY")

if not secret_key:
    raise RuntimeError(
        "Falta configurar SECRET_KEY en el archivo .env"
    )

app.config.update(
    SECRET_KEY=secret_key,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,
    PERMANENT_SESSION_LIFETIME=timedelta(hours=2)
)

app.register_blueprint(auth_bp)

@app.after_request
def configurar_cabeceras_seguridad(respuesta):

    ruta = request.path

    paginas_privadas = {
        "/",
        "/index.html",
        "/materias.html",
        "/admin.html"
    }

    if (
        ruta in paginas_privadas
        or ruta.startswith("/api/")
    ):
        respuesta.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, max-age=0"
        )

        respuesta.headers["Pragma"] = "no-cache"
        respuesta.headers["Expires"] = "0"

    respuesta.headers["X-Content-Type-Options"] = "nosniff"

    respuesta.headers["X-Frame-Options"] = "DENY"

    respuesta.headers["Referrer-Policy"] = (
        "strict-origin-when-cross-origin"
    )

    return respuesta

PAGINAS_PROTEGIDAS = {
    "/",
    "/index.html",
    "/materias.html",
    "/admin.html"
}


@app.before_request
def verificar_acceso_paginas():

    ruta = request.path

    if ruta not in PAGINAS_PROTEGIDAS:
        return None

    id_usuario = session.get("id_usuario")

    if not id_usuario:
        return redirect("/login.html")

    try:
        usuario = obtener_usuario(id_usuario)

    except (PostgreSQLError, ValueError, TypeError):

        app.logger.exception(
            "No se pudo verificar la sesión."
        )

        return jsonify({
            "error": "No se pudo verificar la sesión."
        }), 503

    if usuario is None:
        session.clear()
        return redirect("/login.html")

    if ruta == "/admin.html":

        if usuario.get("rol") != "administrador":

            return jsonify({
                "error": (
                    "Acceso denegado. Se requieren "
                    "permisos de administrador."
                )
            }), 403

    return None

def administrador_requerido(funcion):

    @wraps(funcion)
    @login_requerido
    def verificar_administrador(*args, **kwargs):

        usuario = g.usuario

        if usuario.get("rol") != "administrador":

            return jsonify({
                "error": (
                    "Acceso denegado. Se requieren "
                    "permisos de administrador."
                )
            }), 403

        return funcion(*args, **kwargs)

    return verificar_administrador


def usuario_actual():
    """
    Obtiene el ID del usuario autenticado.
    """
    return g.usuario["id_usuario"]

# HISTORIAL DE MONGODB
def registrar_historial_seguro(
    accion,
    entidad,
    entidad_id=None,
    detalles=None
):
    """
    Registra los movimientos realizados en Fulfill.

    PostgreSQL conserva los datos principales.
    MongoDB almacena el historial.

    Si MongoDB falla, no se cancela una operación
    que PostgreSQL ya completó.
    """

    try:

        registrar_movimiento(
            usuario_id=usuario_actual(),
            accion=accion,
            entidad=entidad,
            entidad_id=entidad_id,
            detalles=detalles or {}
        )

    except (PyMongoError, ValueError, TypeError, OSError):

        app.logger.exception(
            "No fue posible guardar el movimiento %s en MongoDB.",
            accion
        )


def id_resultado(resultado, clave):
    """
    Obtiene el identificador de una materia o actividad
    desde la respuesta de PostgreSQL.
    """

    if not isinstance(resultado, dict):
        return None

    if clave in resultado:
        return resultado[clave]

    for campo in ("materia", "actividad"):

        objeto = resultado.get(campo)

        if isinstance(objeto, dict) and clave in objeto:
            return objeto[clave]

    return None

def error_validacion(error):

    return jsonify({
        "error": str(error)
    }), 400


def error_base_datos(mensaje):

    return jsonify({
        "error": mensaje
    }), 503

@app.route("/")
def inicio():

    return send_from_directory(
        FRONTEND,
        "index.html"
    )

@app.route("/api/salud", methods=["GET"])
def salud():

    return jsonify({
        "aplicacion": "Fulfill",
        "estado": "funcionando",
        "version": "0.1.0"
    }), 200

@app.route("/api/materias", methods=["GET"])
@login_requerido
def listar_materias():

    try:

        materias = obtener_materias(
            usuario_actual()
        )

        return jsonify({
            "total": len(materias),
            "materias": materias
        }), 200

    except PostgreSQLError:

        app.logger.exception(
            "Error consultando materias"
        )

        return error_base_datos(
            "No se pudieron consultar las materias."
        )

@app.route("/api/materias", methods=["POST"])
@login_requerido
def registrar_materia():

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):

        return jsonify({
            "error": "Debes enviar un objeto JSON válido."
        }), 400

    try:

        resultado = crear_materia(
            id_usuario=usuario_actual(),
            nombre=datos.get("nombre"),
            descripcion=datos.get("descripcion", "")
        )

        registrar_historial_seguro(
            accion="crear_materia",
            entidad="materia",
            entidad_id=id_resultado(
                resultado,
                "id_materia"
            ),
            detalles={
                "nombre": datos.get("nombre")
            }
        )

        return jsonify(resultado), 201

    except ValueError as error:

        return error_validacion(error)

    except UniqueViolation:

        return jsonify({
            "error": "La materia ya está registrada."
        }), 409

    except PostgreSQLError:

        app.logger.exception(
            "Error registrando materia"
        )

        return error_base_datos(
            "No se pudo registrar la materia."
        )

@app.route(
    "/api/materias/<int:id_materia>",
    methods=["PUT"]
)
@login_requerido
def editar_materia(id_materia):

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):

        return jsonify({
            "error": "Debes enviar un objeto JSON válido."
        }), 400

    try:

        resultado = actualizar_materia(
            id_materia=id_materia,
            id_usuario=usuario_actual(),
            nombre=datos.get("nombre"),
            descripcion=datos.get("descripcion", "")
        )

        registrar_historial_seguro(
            accion="actualizar_materia",
            entidad="materia",
            entidad_id=id_materia,
            detalles={
                "nombre": datos.get("nombre")
            }
        )

        return jsonify(resultado), 200

    except ValueError as error:

        return error_validacion(error)

    except UniqueViolation:

        return jsonify({
            "error": "Ya existe otra materia con ese nombre."
        }), 409

    except PostgreSQLError:

        app.logger.exception(
            "Error actualizando materia"
        )

        return error_base_datos(
            "No se pudo actualizar la materia."
        )

@app.route(
    "/api/materias/<int:id_materia>",
    methods=["DELETE"]
)
@login_requerido
def borrar_materia(id_materia):

    try:

        resultado = eliminar_materia(
            id_materia=id_materia,
            id_usuario=usuario_actual()
        )

        registrar_historial_seguro(
            accion="eliminar_materia",
            entidad="materia",
            entidad_id=id_materia
        )

        return jsonify(resultado), 200

    except ValueError:

        return jsonify({
            "error": "Materia no encontrada o no disponible."
        }), 404

    except PostgreSQLError:

        app.logger.exception(
            "Error eliminando materia"
        )

        return error_base_datos(
            "No se pudo eliminar la materia."
        )

@app.route("/api/actividades", methods=["GET"])
@login_requerido
def listar_actividades():

    try:

        actividades = obtener_actividades(
            id_usuario=usuario_actual()
        )

        return jsonify({
            "total": len(actividades),
            "actividades": actividades
        }), 200

    except PostgreSQLError:

        app.logger.exception(
            "Error consultando actividades"
        )

        return error_base_datos(
            "No se pudieron consultar las actividades."
        )

@app.route("/api/actividades", methods=["POST"])
@login_requerido
def registrar_actividad():

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):

        return jsonify({
            "error": "Debes enviar un objeto JSON válido."
        }), 400

    try:

        resultado = crear_actividad(
            id_materia=datos.get("id_materia"),
            titulo=datos.get("titulo"),
            descripcion=datos.get("descripcion", ""),
            fecha_entrega=datos.get("fecha_entrega"),
            id_usuario=usuario_actual()
        )

        registrar_historial_seguro(
            accion="crear_actividad",
            entidad="actividad",
            entidad_id=id_resultado(
                resultado,
                "id_actividad"
            ),
            detalles={
                "titulo": datos.get("titulo"),
                "id_materia": datos.get("id_materia")
            }
        )

        return jsonify(resultado), 201

    except ValueError as error:

        return error_validacion(error)

    except PostgreSQLError:

        app.logger.exception(
            "Error registrando actividad"
        )

        return error_base_datos(
            "No se pudo registrar la actividad."
        )

@app.route(
    "/api/actividades/<int:id_actividad>",
    methods=["PUT"]
)
@login_requerido
def editar_actividad(id_actividad):

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):

        return jsonify({
            "error": "Debes enviar un objeto JSON válido."
        }), 400

    try:

        resultado = actualizar_actividad(
            id_actividad=id_actividad,
            id_usuario=usuario_actual(),
            titulo=datos.get("titulo"),
            descripcion=datos.get("descripcion", ""),
            fecha_entrega=datos.get("fecha_entrega"),
            estado=datos.get("estado")
        )

        registrar_historial_seguro(
            accion="actualizar_actividad",
            entidad="actividad",
            entidad_id=id_actividad,
            detalles={
                "titulo": datos.get("titulo"),
                "estado_solicitado": datos.get("estado")
            }
        )

        return jsonify(resultado), 200

    except ValueError as error:

        return error_validacion(error)

    except PostgreSQLError:

        app.logger.exception(
            "Error actualizando actividad"
        )

        return error_base_datos(
            "No se pudo actualizar la actividad."
        )

@app.route(
    "/api/actividades/<int:id_actividad>",
    methods=["DELETE"]
)
@login_requerido
def borrar_actividad(id_actividad):

    try:

        resultado = eliminar_actividad(
            id_actividad=id_actividad,
            id_usuario=usuario_actual()
        )

        registrar_historial_seguro(
            accion="eliminar_actividad",
            entidad="actividad",
            entidad_id=id_actividad
        )

        return jsonify(resultado), 200

    except ValueError:

        return jsonify({
            "error": "Actividad no encontrada o no disponible."
        }), 404

    except PostgreSQLError:

        app.logger.exception(
            "Error eliminando actividad"
        )

        return error_base_datos(
            "No se pudo eliminar la actividad."
        )

@app.route("/api/admin/panel", methods=["GET"])
@administrador_requerido
def panel_administrador():

    return jsonify({
        "mensaje": "Acceso administrativo autorizado.",
        "administrador": {
            "id_usuario": g.usuario["id_usuario"],
            "nombre": g.usuario["nombre"],
            "rol": g.usuario["rol"]
        },
        "estado": "activo"
    }), 200

@app.route("/api/admin/resumen", methods=["GET"])
@administrador_requerido
def resumen_administrador():

    try:

        resumen = obtener_resumen_admin()

        return jsonify({
            "mensaje": (
                "Resumen administrativo "
                "obtenido correctamente."
            ),
            "resumen": resumen
        }), 200

    except PostgreSQLError:

        app.logger.exception(
            "Error consultando resumen administrativo"
        )

        return jsonify({
            "error": (
                "No se pudo obtener el "
                "resumen administrativo."
            )
        }), 503

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
