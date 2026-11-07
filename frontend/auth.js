document.addEventListener("DOMContentLoaded", () => {

    const formulario = document.getElementById("form-auth");
    const titulo = document.getElementById("titulo-formulario");
    const subtitulo = document.getElementById("subtitulo-formulario");

    const campoNombre = document.getElementById("campo-nombre");
    const nombre = document.getElementById("nombre");
    const correo = document.getElementById("correo");
    const password = document.getElementById("password");

    const botonEnviar = document.getElementById("boton-enviar");
    const cambiarModo = document.getElementById("cambiar-modo");
    const textoAlternativa = document.getElementById("texto-alternativa");

    const mostrarPassword = document.getElementById("mostrar-password");
    const mensaje = document.getElementById("mensaje-estado");

    let modoRegistro = false;

    function mostrarMensaje(texto, tipo = "error") {
        mensaje.textContent = texto;
        mensaje.className = "mensaje-estado " + tipo;
    }

    function actualizarModo() {

        mensaje.textContent = "";
        mensaje.className = "mensaje-estado";

        formulario.reset();

        password.type = "password";
        mostrarPassword.textContent = "Mostrar";

        campoNombre.classList.toggle(
            "oculto",
            !modoRegistro
        );

        nombre.required = modoRegistro;

        if (modoRegistro) {

            titulo.textContent = "Tu camino comienza aquí.";

            subtitulo.textContent =
                "Crea tu cuenta y empieza a organizar tus materias.";

            botonEnviar.textContent = "Crear mi cuenta";

            textoAlternativa.textContent =
                "¿Ya tienes una cuenta?";

            cambiarModo.textContent = "Iniciar sesión";

            password.autocomplete = "new-password";

            password.minLength = 8;
            password.maxLength = 128;

        } else {

            titulo.textContent =
                "¡Qué bueno tenerte de vuelta!";

            subtitulo.textContent =
                "Inicia sesión para continuar organizando tu vida académica.";

            botonEnviar.textContent = "Iniciar sesión";

            textoAlternativa.textContent =
                "¿Todavía no tienes cuenta?";

            cambiarModo.textContent = "Regístrate";

            password.autocomplete = "current-password";

            password.removeAttribute("minlength");
            password.removeAttribute("maxlength");
        }
    }

    cambiarModo.addEventListener("click", () => {

        modoRegistro = !modoRegistro;

        actualizarModo();
    });

    mostrarPassword.addEventListener("click", () => {

        const visible = password.type === "text";

        password.type = visible ? "password" : "text";

        mostrarPassword.textContent =
            visible ? "Mostrar" : "Ocultar";
    });

    function redirigirUsuario(usuario) {

        if (!usuario || !usuario.rol) {
            throw new Error(
                "No fue posible identificar el rol del usuario."
            );
        }

        if (usuario.rol === "administrador") {

            window.location.replace("/admin.html");

        } else if (usuario.rol === "estudiante") {

            window.location.replace("/");

        } else {

            throw new Error(
                "El usuario tiene un rol no reconocido."
            );
        }
    }

    formulario.addEventListener("submit", async (evento) => {

        evento.preventDefault();

        const esRegistro = modoRegistro;

        const url = esRegistro
            ? "/api/auth/registro"
            : "/api/auth/login";

        const datos = {
            correo: correo.value.trim(),
            password: password.value
        };

        if (esRegistro) {
            datos.nombre = nombre.value.trim();
        }

        botonEnviar.disabled = true;

        botonEnviar.textContent = esRegistro
            ? "Creando cuenta..."
            : "Iniciando sesión...";

        mostrarMensaje(
            "Conectando con Fulfill...",
            "exito"
        );

        try {

            const respuesta = await fetch(url, {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                credentials: "same-origin",

                body: JSON.stringify(datos)
            });

            const resultado = await respuesta.json();

            if (!respuesta.ok) {
                throw new Error(
                    resultado.error ||
                    "No se pudo completar la solicitud."
                );
            }

            if (esRegistro) {

                modoRegistro = false;

                actualizarModo();

                mostrarMensaje(
                    "¡Cuenta creada correctamente! Ahora inicia sesión.",
                    "exito"
                );

                return;
            }

            const usuario = resultado.usuario;

            if (!usuario || !usuario.rol) {
                throw new Error(
                    "El servidor no devolvió el rol del usuario."
                );
            }

            mostrarMensaje(
                "¡Bienvenido a Fulfill! Redirigiendo...",
                "exito"
            );

            redirigirUsuario(usuario);

        } catch (error) {

            mostrarMensaje(
                error.message ||
                "No se pudo conectar con el servidor."
            );

        } finally {

            botonEnviar.disabled = false;

            botonEnviar.textContent = modoRegistro
                ? "Crear mi cuenta"
                : "Iniciar sesión";
        }
    });

});
