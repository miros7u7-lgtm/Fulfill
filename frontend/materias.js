const API_MATERIAS = "/api/materias";

let materiasRegistradas = [];

const formularioMateria = document.getElementById("form-materia");
const listaMaterias = document.getElementById("lista-materias");
const mensajeMateria = document.getElementById("mensaje-materia");

async function cargarMaterias() {
    if (!listaMaterias) return;

    listaMaterias.textContent = "Cargando materias...";

    try {
        const respuesta = await fetch(API_MATERIAS);

        if (!respuesta.ok) {
            throw new Error("No se pudieron consultar las materias.");
        }

        const datos = await respuesta.json();

        materiasRegistradas = datos.materias || [];

        mostrarMaterias();

    } catch (error) {
        listaMaterias.textContent = error.message;
        console.error(error);
    }
}


function mostrarMaterias() {
    listaMaterias.replaceChildren();

    if (materiasRegistradas.length === 0) {
        const mensaje = document.createElement("p");
        mensaje.textContent = "Todavía no tienes materias registradas.";
        listaMaterias.appendChild(mensaje);
        return;
    }

    materiasRegistradas.forEach((materia) => {
        const tarjeta = document.createElement("article");
        tarjeta.className = "materia-item";

        // INFORMACIÓN DE LA MATERIA
        const informacion = document.createElement("div");
        informacion.className = "materia-info";

        const titulo = document.createElement("h3");
        titulo.textContent = materia.nombre;

        const descripcion = document.createElement("p");
        descripcion.textContent =
            materia.descripcion || "Sin descripción.";

        informacion.appendChild(titulo);
        informacion.appendChild(descripcion);

        // CONTENEDOR DE ACCIONES
        const acciones = document.createElement("div");
        acciones.className = "materia-actions";

        // BOTÓN EDITAR
        const botonEditar = document.createElement("button");
        botonEditar.type = "button";
        botonEditar.className =
            "icon-action-button action-edit";

        botonEditar.setAttribute("aria-label", "Editar materia");
        botonEditar.setAttribute("data-tooltip", "Editar");

        botonEditar.innerHTML = `
            <svg
                xmlns="http://www.w3.org/2000/svg"
                width="19"
                height="19"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.8"
                stroke-linecap="round"
                stroke-linejoin="round"
                aria-hidden="true"
            >
                <path d="M12 20h9"/>
                <path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L9 17l-4 1 1-4Z"/>
            </svg>
        `;

        botonEditar.addEventListener("click", () => {
            abrirFormularioEdicion(tarjeta, materia);
        });

        // BOTÓN ELIMINAR
        const botonEliminar = document.createElement("button");
        botonEliminar.type = "button";
        botonEliminar.className =
            "icon-action-button action-delete";

        botonEliminar.setAttribute("aria-label", "Eliminar materia");
        botonEliminar.setAttribute("data-tooltip", "Eliminar");

        botonEliminar.innerHTML = `
            <svg
                xmlns="http://www.w3.org/2000/svg"
                width="19"
                height="19"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.8"
                stroke-linecap="round"
                stroke-linejoin="round"
                aria-hidden="true"
            >
                <path d="M3 6h18"/>
                <path d="M8 6V4h8v2"/>
                <path d="M19 6l-1 14H6L5 6"/>
                <path d="M10 11v5"/>
                <path d="M14 11v5"/>
            </svg>
        `;

        botonEliminar.addEventListener("click", () => {
            eliminarMateria(materia, botonEliminar);
        });

        acciones.appendChild(botonEditar);
        acciones.appendChild(botonEliminar);

        tarjeta.appendChild(informacion);
        tarjeta.appendChild(acciones);

        listaMaterias.appendChild(tarjeta);
    });
}

function abrirFormularioEdicion(tarjeta, materia) {
    mostrarMaterias();

    const tarjetaActual = Array.from(
        listaMaterias.querySelectorAll(".materia-item")
    ).find((elemento) =>
        elemento.querySelector("h3")?.textContent === materia.nombre
    );

    if (!tarjetaActual) return;

    const formulario = document.createElement("form");
    formulario.className = "materia-edit-form";

    const etiquetaNombre = document.createElement("label");
    etiquetaNombre.textContent = "Nombre de la materia";

    const campoNombre = document.createElement("input");
    campoNombre.type = "text";
    campoNombre.value = materia.nombre;
    campoNombre.maxLength = 100;
    campoNombre.required = true;

    const etiquetaDescripcion = document.createElement("label");
    etiquetaDescripcion.textContent = "Descripción";

    const campoDescripcion = document.createElement("textarea");
    campoDescripcion.value = materia.descripcion || "";
    campoDescripcion.rows = 3;

    const acciones = document.createElement("div");
    acciones.className = "materia-edit-actions";

    const botonGuardar = document.createElement("button");
    botonGuardar.type = "submit";
    botonGuardar.className = "activity-submit-button";
    botonGuardar.textContent = "Guardar cambios";

    const botonCancelar = document.createElement("button");
    botonCancelar.type = "button";
    botonCancelar.className = "edit-cancel-button";
    botonCancelar.textContent = "Cancelar";

    botonCancelar.addEventListener("click", mostrarMaterias);

    acciones.appendChild(botonCancelar);
    acciones.appendChild(botonGuardar);

    formulario.appendChild(etiquetaNombre);
    formulario.appendChild(campoNombre);
    formulario.appendChild(etiquetaDescripcion);
    formulario.appendChild(campoDescripcion);
    formulario.appendChild(acciones);

    formulario.addEventListener("submit", async (evento) => {
        evento.preventDefault();

        botonGuardar.disabled = true;
        botonGuardar.textContent = "Guardando...";

        try {
            const respuesta = await fetch(
                `${API_MATERIAS}/${materia.id_materia}`,
                {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        nombre: campoNombre.value.trim(),
                        descripcion: campoDescripcion.value.trim()
                    })
                }
            );

            const resultado = await respuesta.json();

            if (!respuesta.ok) {
                throw new Error(
                    resultado.error || "No se pudo actualizar la materia."
                );
            }

            await cargarMaterias();

        } catch (error) {
            alert(error.message);
            botonGuardar.disabled = false;
            botonGuardar.textContent = "Guardar cambios";
        }
    });

    tarjetaActual.replaceChildren(formulario);
    campoNombre.focus();
}

async function eliminarMateria(materia, boton) {

    const confirmar = window.confirm(
        `¿Deseas eliminar la materia "${materia.nombre}"?\n\n` +
        "La materia y sus actividades dejarán de aparecer " +
        "en tu lista, pero permanecerán guardadas " +
        "en PostgreSQL."
    );

    if (!confirmar) return;

    boton.disabled = true;
    boton.textContent = "Eliminando...";

    try {
        const respuesta = await fetch(
            `${API_MATERIAS}/${materia.id_materia}`,
            {
                method: "DELETE"
            }
        );

        const resultado = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(
                resultado.error || "No se pudo eliminar la materia."
            );
        }

        await cargarMaterias();

    } catch (error) {
        alert(error.message);
        boton.disabled = false;
        boton.textContent = "Eliminar";
    }
}

if (formularioMateria) {
    formularioMateria.addEventListener("submit", async (evento) => {
        evento.preventDefault();

        const nombre = document.getElementById("nombre-materia");
        const descripcion =
            document.getElementById("descripcion-materia");

        if (!nombre || !descripcion) return;

        const boton = formularioMateria.querySelector(
            'button[type="submit"]'
        );

        boton.disabled = true;
        boton.textContent = "Guardando...";

        try {
            const respuesta = await fetch(API_MATERIAS, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    nombre: nombre.value.trim(),
                    descripcion: descripcion.value.trim()
                })
            });

            const resultado = await respuesta.json();

            if (!respuesta.ok) {
                throw new Error(
                    resultado.error || "No se pudo registrar la materia."
                );
            }

            formularioMateria.reset();

            if (mensajeMateria) {
                mensajeMateria.style.color = "#376d57";
                mensajeMateria.textContent =
                    "¡Materia registrada correctamente!";
            }

            await cargarMaterias();

        } catch (error) {
            if (mensajeMateria) {
                mensajeMateria.style.color = "#a64c46";
                mensajeMateria.textContent = error.message;
            }

        } finally {
            boton.disabled = false;
            boton.textContent = "Guardar materia";
        }
    });
}

document.addEventListener("DOMContentLoaded", cargarMaterias);
