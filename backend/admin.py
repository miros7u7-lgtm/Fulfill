from database import conectar_bd


def obtener_resumen_admin():
    """
    Consulta las estadísticas generales de Fulfill.

    Compatible con conexiones PostgreSQL
    que utilizan dict_row.
    """

    with conectar_bd() as conexion:

        with conexion.cursor() as cursor:

            cursor.execute("""
                SELECT
                    (SELECT COUNT(*)
                     FROM usuarios) AS total_usuarios,

                    (SELECT COUNT(*)
                     FROM usuarios
                     WHERE rol = 'estudiante')
                     AS total_estudiantes,

                    (SELECT COUNT(*)
                     FROM usuarios
                     WHERE rol = 'administrador')
                     AS total_administradores,

                    (SELECT COUNT(*)
                     FROM materias
                     WHERE eliminado = FALSE)
                     AS total_materias,

                    (SELECT COUNT(*)
                     FROM actividades
                     WHERE eliminado = FALSE)
                     AS total_actividades,

                    (SELECT COUNT(*)
                     FROM actividades
                     WHERE eliminado = FALSE
                     AND estado = 'pendiente')
                     AS actividades_pendientes,

                    (SELECT COUNT(*)
                     FROM actividades
                     WHERE eliminado = FALSE
                     AND estado = 'en_proceso')
                     AS actividades_en_proceso,

                    (SELECT COUNT(*)
                     FROM actividades
                     WHERE eliminado = FALSE
                     AND estado = 'completada')
                     AS actividades_completadas
            """)

            resultado = cursor.fetchone()

    return {
        "usuarios": {
            "total": resultado["total_usuarios"],
            "estudiantes": resultado["total_estudiantes"],
            "administradores": resultado["total_administradores"]
        },
        "materias": {
            "activas": resultado["total_materias"]
        },
        "actividades": {
            "total": resultado["total_actividades"],
            "pendientes": resultado["actividades_pendientes"],
            "en_proceso": resultado["actividades_en_proceso"],
            "completadas": resultado["actividades_completadas"]
        }
    }
