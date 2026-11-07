document.addEventListener("DOMContentLoaded", async () => {

    const nombre = document.getElementById("admin-nombre");
    const botonSalir = document.getElementById("admin-logout");
    const botonActualizar = document.getElementById("admin-actualizar");
    const mensaje = document.getElementById("admin-mensaje");
    const errorPanel = document.getElementById("admin-error");

    function escribir(id, valor) {
        const elemento = document.getElementById(id);

        if (elemento) {
            elemento.textContent = valor;
        }
    }

    function mostrarError(texto) {
        errorPanel.textContent = texto;
        errorPanel.hidden = false;
        mensaje.hidden = true;
    }

    function actualizarBarra(id, cantidad, total) {
        const barra = document.getElementById(id);

        if (!barra) return;

        const porcentaje = total > 0
            ? Math.min(100, Math.max(0, (cantidad / total) * 100))
            : 0;

        barra.style.width = `${porcentaje}%`;
        barra.setAttribute("role", "progressbar");
        barra.setAttribute("aria-valuemin", "0");
        barra.setAttribute("aria-valuemax", "100");
        barra.setAttribute("aria-valuenow", String(porcentaje));
    }

    async function comprobarAdministrador() {
        const respuesta = await fetch("/api/auth/yo", {
            method: "GET",
            credentials: "same-origin",
            cache: "no-store"
        });

        if (respuesta.status === 401) {
            window.location.replace("/login.html");
            return false;
        }

        if (!respuesta.ok) {
            throw new Error("No se pudo verificar la sesión.");
        }

        const datos = await respuesta.json();
        const usuario = datos.usuario;

        if (!usuario || usuario.rol !== "administrador") {
            window.location.replace("/");
            return false;
        }

        nombre.textContent = usuario.nombre;
        return true;
    }

    async function cargarResumen() {
        botonActualizar.disabled = true;
        errorPanel.hidden = true;
        mensaje.hidden = false;
        mensaje.textContent = "Cargando estadísticas...";

        try {
            const respuesta = await fetch("/api/admin/resumen", {
                method: "GET",
                credentials: "same-origin",
                cache: "no-store"
            });

            if (respuesta.status === 401) {
                window.location.replace("/login.html");
                return;
            }

            if (respuesta.status === 403) {
                window.location.replace("/");
                return;
            }

            if (!respuesta.ok) {
                throw new Error(
                    "No fue posible consultar las estadísticas."
                );
            }

            const datos = await respuesta.json();
            const resumen = datos.resumen;

            if (!resumen || !resumen.usuarios ||
                !resumen.materias || !resumen.actividades) {
                throw new Error(
                    "El servidor devolvió información incompleta."
                );
            }

            escribir("total-usuarios", resumen.usuarios.total);
            escribir("total-materias", resumen.materias.activas);
            escribir("total-actividades", resumen.actividades.total);

            escribir(
                "total-estudiantes",
                resumen.usuarios.estudiantes
            );

            escribir(
                "total-administradores",
                resumen.usuarios.administradores
            );

            escribir(
                "total-pendientes",
                resumen.actividades.pendientes
            );

            escribir(
                "total-proceso",
                resumen.actividades.en_proceso
            );

            escribir(
                "total-completadas",
                resumen.actividades.completadas
            );

            const total = resumen.actividades.total;

            actualizarBarra(
                "barra-pendientes",
                resumen.actividades.pendientes,
                total
            );

            actualizarBarra(
                "barra-proceso",
                resumen.actividades.en_proceso,
                total
            );

            actualizarBarra(
                "barra-completadas",
                resumen.actividades.completadas,
                total
            );

            mensaje.textContent =
                "Estadísticas actualizadas correctamente.";

        } catch (error) {
            console.error(error);
            mostrarError(error.message);

        } finally {
            botonActualizar.disabled = false;
        }
    }

    botonActualizar.addEventListener("click", cargarResumen);

    botonSalir.addEventListener("click", async () => {
        botonSalir.disabled = true;

        try {
            const respuesta = await fetch("/api/auth/logout", {
                method: "POST",
                credentials: "same-origin"
            });

            if (!respuesta.ok) {
                throw new Error("No se pudo cerrar la sesión.");
            }

            window.location.replace("/login.html");

        } catch (error) {
            mostrarError(error.message);
            botonSalir.disabled = false;
        }
    });

    try {
        const autorizado = await comprobarAdministrador();

        if (autorizado) {
            await cargarResumen();
        }

    } catch (error) {
        console.error(error);
        mostrarError(error.message);
    }
});
