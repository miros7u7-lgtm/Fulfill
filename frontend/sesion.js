document.addEventListener("DOMContentLoaded", async () => {
    const contenedor = document.getElementById("usuario-sesion");

    if (!contenedor) return;

    try {
        const respuesta = await fetch("/api/auth/yo", {
            method: "GET",
            credentials: "same-origin",
            cache: "no-store"
        });

        if (respuesta.status === 401) {
            window.location.replace("/login.html");
            return;
        }

        if (!respuesta.ok) {
            throw new Error("No se pudo verificar la sesión.");
        }

        const datos = await respuesta.json();
        const usuario = datos.usuario;

        if (!usuario || !usuario.nombre) {
            throw new Error("No se encontraron los datos del usuario.");
        }

        const enlaceAdministracion = document.getElementById(
                "enlace-administracion"
            );

            if (enlaceAdministracion) {
                if (usuario.rol === "administrador") {
                    enlaceAdministracion.hidden = false;
                } else {
                    enlaceAdministracion.hidden = true;
                }
        }

        contenedor.replaceChildren();

        const nombre = document.createElement("span");
        nombre.className = "sesion-nombre";
        nombre.textContent = usuario.nombre;

        const boton = document.createElement("button");
        boton.type = "button";
        boton.className = "sesion-salir";
        boton.textContent = "Cerrar sesión";

        boton.addEventListener("click", async () => {
            boton.disabled = true;
            boton.textContent = "Saliendo...";

            try {
                const respuestaLogout = await fetch("/api/auth/logout", {
                    method: "POST",
                    credentials: "same-origin"
                });

                if (!respuestaLogout.ok) {
                    throw new Error("No se pudo cerrar la sesión.");
                }

                window.location.replace("/login.html");

            } catch (error) {
                alert(error.message);
                boton.disabled = false;
                boton.textContent = "Cerrar sesión";
            }
        });

        contenedor.append(nombre, boton);

    } catch (error) {
        contenedor.textContent = "No se pudo cargar la sesión.";
        console.error(error);
    }
});
