const API_ACTIVIDADES = "/api/actividades";
const API_MATERIAS = "/api/materias";

let actividadesGuardadas = [];

const botonVerificar = document.getElementById("verificar");

if (botonVerificar) {
    botonVerificar.addEventListener("click", async () => {
        const resultado = document.getElementById("resultado");

        resultado.className = "connection-result is-loading";
        resultado.textContent = "Comprobando conexión...";

        try {
            const respuesta = await fetch("/api/salud");

            if (!respuesta.ok) {
                throw new Error("Error de conexión");
            }

            const datos = await respuesta.json();

            resultado.className = "connection-result is-success";
            resultado.textContent =
                `Conexión exitosa: ${datos.aplicacion} está ${datos.estado}`;

        } catch (error) {
            resultado.className = "connection-result is-error";
            resultado.textContent =
                "No se pudo conectar con el servidor.";
        }
    });
}

async function cargarMaterias() {
    const selector = document.getElementById("materia-actividad");

    if (!selector) return;

    selector.replaceChildren();

    const opcionInicial = document.createElement("option");
    opcionInicial.value = "";
    opcionInicial.textContent = "Selecciona una materia";
    selector.appendChild(opcionInicial);

    try {
        const respuesta = await fetch(API_MATERIAS);

        if (!respuesta.ok) {
            throw new Error("No se pudieron cargar las materias.");
        }

        const datos = await respuesta.json();

        datos.materias.forEach((materia) => {
            const opcion = document.createElement("option");

            opcion.value = String(materia.id_materia);
            opcion.textContent = materia.nombre;

            selector.appendChild(opcion);
        });

        if (datos.materias.length === 0) {
            opcionInicial.textContent = "Primero registra una materia";
        }

    } catch (error) {
        opcionInicial.textContent = "Error al cargar materias";
        console.error(error);
    }
}

function formatearFecha(fechaTexto) {
    const [anio, mes, dia] = fechaTexto.split("-").map(Number);

    const fecha = new Date(anio, mes - 1, dia);

    return fecha.toLocaleDateString("es-MX", {
        day: "2-digit",
        month: "short",
        year: "numeric"
    });
}

async function cargarActividades() {
    const tabla = document.getElementById("tabla-actividades");
    const total = document.getElementById("total-actividades");

    if (!tabla || !total) return;

    try {
        const respuesta = await fetch(API_ACTIVIDADES);

        if (!respuesta.ok) {
            throw new Error("No se pudieron consultar las actividades.");
        }

        const datos = await respuesta.json();

        actividadesGuardadas = datos.actividades;

        tabla.replaceChildren();

        if (actividadesGuardadas.length === 0) {
            const fila = tabla.insertRow();
            const celda = fila.insertCell();

            celda.colSpan = 5;
            celda.textContent =
                "Todavía no tienes actividades registradas.";

            total.textContent = "0 actividades registradas";
            return;
        }

        actividadesGuardadas.forEach((actividad) => {
            const fila = tabla.insertRow();

            const celdaTitulo = fila.insertCell();
            celdaTitulo.textContent = actividad.titulo;

            const celdaMateria = fila.insertCell();
            celdaMateria.textContent = actividad.materia;

            const celdaFecha = fila.insertCell();
            celdaFecha.textContent =
                formatearFecha(actividad.fecha_entrega);

            const celdaEstado = fila.insertCell();

            const etiqueta = document.createElement("span");

            const nombresEstados = {
                pendiente: "Pendiente",
                en_proceso: "En proceso",
                completada: "Completada"
            };

            etiqueta.className =
                "activity-status " + actividad.estado;

            etiqueta.textContent =
                nombresEstados[actividad.estado] || actividad.estado;

            celdaEstado.appendChild(etiqueta);

            const celdaAcciones = fila.insertCell();
            celdaAcciones.className = "activity-actions-cell";

            const contenedor = document.createElement("div");
            contenedor.className = "activity-actions";

            const botonEditar = document.createElement("button");
            botonEditar.type = "button";
            botonEditar.className = "activity-edit-button";
            botonEditar.textContent = "Editar";

            botonEditar.addEventListener("click", () => {
                abrirEdicion(actividad.id_actividad);
            });

            const botonEliminar = document.createElement("button");
            botonEliminar.type = "button";
            botonEliminar.className = "activity-delete-button";
            botonEliminar.textContent = "Eliminar";

            botonEliminar.addEventListener("click", () => {
                eliminarActividad(
                    actividad.id_actividad,
                    actividad.titulo,
                    botonEliminar
                );
            });

            contenedor.appendChild(botonEditar);
            contenedor.appendChild(botonEliminar);
            celdaAcciones.appendChild(contenedor);
        });

        total.textContent =
            `${actividadesGuardadas.length} actividad(es) registrada(s)`;

    } catch (error) {
        tabla.replaceChildren();

        const fila = tabla.insertRow();
        const celda = fila.insertCell();

        celda.colSpan = 5;
        celda.textContent =
            "No se pudieron cargar las actividades.";

        total.textContent = "Error al consultar actividades";

        console.error(error);
    }
}

const formularioActividad =
    document.getElementById("form-actividad");

if (formularioActividad) {
    formularioActividad.addEventListener("submit", async (evento) => {
        evento.preventDefault();

        const boton = document.getElementById("guardar-actividad");
        const mensaje = document.getElementById("mensaje-actividad");

        const titulo =
            document.getElementById("titulo-actividad").value.trim();

        const descripcion =
            document.getElementById("descripcion-actividad").value.trim();

        const idMateria =
            Number(document.getElementById("materia-actividad").value);

        const fechaEntrega =
            document.getElementById("fecha-actividad").value;

        if (!titulo || !fechaEntrega ||
            !Number.isInteger(idMateria) || idMateria <= 0) {

            mensaje.style.color = "#a64c46";
            mensaje.textContent = "Completa los campos obligatorios.";
            return;
        }

        boton.disabled = true;
        boton.textContent = "Guardando...";
        mensaje.textContent = "";

        try {
            const respuesta = await fetch(API_ACTIVIDADES, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    id_materia: idMateria,
                    titulo,
                    descripcion,
                    fecha_entrega: fechaEntrega
                })
            });

            const resultado = await respuesta.json();

            if (!respuesta.ok) {
                throw new Error(
                    resultado.error || "No se pudo registrar la actividad."
                );
            }

            mensaje.style.color = "#376d57";
            mensaje.textContent =
                "¡Actividad registrada correctamente!";

            formularioActividad.reset();

            await cargarActividades();

        } catch (error) {
            mensaje.style.color = "#a64c46";
            mensaje.textContent = error.message;

        } finally {
            boton.disabled = false;
            boton.textContent = "Guardar actividad";
        }
    });
}

function abrirEdicion(idActividad) {
    const actividad = actividadesGuardadas.find(
        (item) => item.id_actividad === idActividad
    );

    if (!actividad) {
        alert("No se encontró la actividad.");
        return;
    }

    document.getElementById("editar-id").value =
        actividad.id_actividad;

    document.getElementById("editar-titulo").value =
        actividad.titulo;

    document.getElementById("editar-descripcion").value =
        actividad.descripcion || "";

    document.getElementById("editar-fecha").value =
        actividad.fecha_entrega;

    const selector = document.getElementById("editar-estado");

    const transiciones = {
        pendiente: ["pendiente", "en_proceso"],
        en_proceso: ["en_proceso", "completada"],
        completada: ["completada"]
    };

    const nombres = {
        pendiente: "Pendiente",
        en_proceso: "En proceso",
        completada: "Completada"
    };

    selector.replaceChildren();

    const permitidos =
        transiciones[actividad.estado] || [actividad.estado];

    permitidos.forEach((estado) => {
        const opcion = document.createElement("option");

        opcion.value = estado;
        opcion.textContent = nombres[estado] || estado;

        selector.appendChild(opcion);
    });

    selector.value = actividad.estado;

    const seccion = document.getElementById("seccion-editar");

    document.getElementById("mensaje-edicion").textContent = "";

    seccion.hidden = false;

    seccion.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}

function cerrarEdicion() {
    const seccion = document.getElementById("seccion-editar");

    if (seccion) {
        seccion.hidden = true;
    }

    const formulario = document.getElementById("form-editar-actividad");

    if (formulario) {
        formulario.reset();
    }
}

const botonCancelar =
    document.getElementById("cancelar-edicion");

if (botonCancelar) {
    botonCancelar.addEventListener("click", cerrarEdicion);
}

const formularioEdicion =
    document.getElementById("form-editar-actividad");

if (formularioEdicion) {
    formularioEdicion.addEventListener("submit", async (evento) => {
        evento.preventDefault();

        const idActividad =
            Number(document.getElementById("editar-id").value);

        const titulo =
            document.getElementById("editar-titulo").value.trim();

        const descripcion =
            document.getElementById("editar-descripcion").value.trim();

        const fechaEntrega =
            document.getElementById("editar-fecha").value;

        const estado =
            document.getElementById("editar-estado").value;

        const mensaje =
            document.getElementById("mensaje-edicion");

        const boton =
            document.getElementById("guardar-edicion");

        if (!idActividad || !titulo || !fechaEntrega || !estado) {
            mensaje.style.color = "#a64c46";
            mensaje.textContent = "Completa los campos obligatorios.";
            return;
        }

        boton.disabled = true;
        boton.textContent = "Guardando cambios...";
        mensaje.textContent = "";

        try {
            const respuesta = await fetch(
                `${API_ACTIVIDADES}/${idActividad}`,
                {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        titulo,
                        descripcion,
                        fecha_entrega: fechaEntrega,
                        estado
                    })
                }
            );

            const resultado = await respuesta.json();

            if (!respuesta.ok) {
                throw new Error(
                    resultado.error ||
                    "No se pudo actualizar la actividad."
                );
            }

            await cargarActividades();

            cerrarEdicion();

            document.getElementById("actividades").scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        } catch (error) {
            mensaje.style.color = "#a64c46";
            mensaje.textContent = error.message;

        } finally {
            boton.disabled = false;
            boton.textContent = "Guardar cambios";
        }
    });
}

async function eliminarActividad(idActividad, titulo, boton) {

    const confirmar = window.confirm(
        `¿Deseas eliminar la actividad "${titulo}"?\n\n` +
        "La actividad dejará de aparecer en tu lista, " +
        "pero permanecerá guardada en la base de datos."
    );

    if (!confirmar) {
        return;
    }

    boton.disabled = true;
    boton.textContent = "Eliminando...";

    try {
        const respuesta = await fetch(
            `${API_ACTIVIDADES}/${idActividad}`,
            {
                method: "DELETE"
            }
        );

        const resultado = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(
                resultado.error ||
                "No se pudo eliminar la actividad."
            );
        }

        const idEnEdicion = Number(
            document.getElementById("editar-id").value
        );

        if (idEnEdicion === idActividad) {
            cerrarEdicion();
        }

        await cargarActividades();

    } catch (error) {
        alert(error.message);
        console.error("Error al eliminar:", error);

    } finally {
        boton.disabled = false;
        boton.textContent = "Eliminar";
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    await Promise.all([
        cargarMaterias(),
        cargarActividades()
    ]);
});
