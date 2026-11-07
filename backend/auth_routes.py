from functools import wraps

from flask import (
    Blueprint,
    jsonify,
    request,
    session,
    g,
    current_app
)

from psycopg import Error as PostgreSQLError
from psycopg.errors import UniqueViolation

from usuarios import (
    registrar_usuario,
    autenticar_usuario,
    obtener_usuario
)


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)

def login_requerido(funcion):

    @wraps(funcion)
    def protegida(*args, **kwargs):

        id_usuario = session.get("id_usuario")

        if not id_usuario:
            return jsonify({
                "error": "Debes iniciar sesión."
            }), 401

        try:
            usuario = obtener_usuario(id_usuario)

        except (PostgreSQLError, ValueError, TypeError):
            current_app.logger.exception(
                "Error verificando usuario autenticado."
            )

            return jsonify({
                "error": "No se pudo verificar la sesión."
            }), 503

        if usuario is None:
            session.clear()

            return jsonify({
                "error": "Sesión no válida."
            }), 401

        g.usuario = usuario

        return funcion(*args, **kwargs)

    return protegida

@auth_bp.route("/registro", methods=["POST"])
def registro():

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "error": "Debes enviar un JSON válido."
        }), 400

    try:
        resultado = registrar_usuario(
            nombre=datos.get("nombre"),
            correo=datos.get("correo"),
            password=datos.get("password")
        )

        return jsonify(resultado), 201

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except UniqueViolation:
        return jsonify({
            "error": "No se pudo registrar la cuenta."
        }), 409

    except PostgreSQLError:
        current_app.logger.exception(
            "Error registrando usuario."
        )

        return jsonify({
            "error": "No se pudo registrar el usuario."
        }), 503

@auth_bp.route("/login", methods=["POST"])
def login():

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "error": "Debes enviar un JSON válido."
        }), 400

    try:
        usuario = autenticar_usuario(
            correo=datos.get("correo"),
            password=datos.get("password")
        )

        # Limpiar cualquier sesión anterior.
        session.clear()

        # Registrar los datos mínimos de la sesión.
        session["id_usuario"] = usuario["id_usuario"]
        session["rol"] = usuario["rol"]

        # Aplica PERMANENT_SESSION_LIFETIME de app.py.
        session.permanent = True

        return jsonify({
            "mensaje": "Inicio de sesión correcto.",
            "usuario": usuario
        }), 200

    except ValueError:
        return jsonify({
            "error": "Correo o contraseña incorrectos."
        }), 401

    except PostgreSQLError:
        current_app.logger.exception(
            "Error iniciando sesión."
        )

        return jsonify({
            "error": "No se pudo iniciar sesión."
        }), 503

@auth_bp.route("/yo", methods=["GET"])
@login_requerido
def mi_perfil():

    return jsonify({
        "usuario": g.usuario
    }), 200

@auth_bp.route("/logout", methods=["POST"])
def logout():

    session.clear()

    return jsonify({
        "mensaje": "Sesión cerrada correctamente."
    }), 200
