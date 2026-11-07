
# Fulfill — Sistema de Gestión Académica

Fulfill es una aplicación web diseñada para administrar materias y actividades académicas de manera organizada, mediante una interfaz intuitiva y operaciones CRUD.

## Tecnologías utilizadas

- **Frontend:** HTML, CSS y JavaScript.
- **Backend:** Python y Flask.
- **Base de datos relacional:** PostgreSQL.
- **Base de datos NoSQL:** MongoDB.
- **Contenedores:** Docker y Docker Compose.
- **Orquestación:** Kubernetes con K3s.
- **Entrada HTTPS:** Traefik.
- **Monitoreo:** Prometheus.

## Funcionalidades

- Registro e inicio de sesión de usuarios.
- Administración de materias.
- Creación, consulta, actualización y eliminación de actividades.
- Administración de usuarios.
- Registro de modificaciones mediante MongoDB.

## Arquitectura

El frontend se comunica con una API REST desarrollada en Flask.

PostgreSQL almacena la información estructurada de usuarios, materias y actividades.

MongoDB se utiliza para registrar el historial de modificaciones.

La aplicación se ejecuta mediante contenedores Docker y cuenta con manifiestos para su despliegue en Kubernetes.

## Estructura del proyecto

- `backend/`: API y lógica de negocio.
- `frontend/`: interfaz web.
- `database/`: scripts de base de datos.
- `kubernetes/`: manifiestos y configuración de Kubernetes.
- `backups/`: Dockerfiles para herramientas de respaldo.
- `docs/`: evidencias técnicas.
- `Dockerfile`: construcción de la aplicación.
- `compose.yaml`: configuración de Docker Compose.
- `requirements.txt`: dependencias de Python.

## Infraestructura Kubernetes

El proyecto incorpora:

- Deployments y Services.
- Almacenamiento persistente para las bases de datos.
- Ingress con HTTPS.
- NetworkPolicies para controlar las comunicaciones.
- ServiceAccount con permisos restringidos.
- Horizontal Pod Autoscaler (HPA).
- Monitoreo y alertas mediante Prometheus.
- Respaldos automatizados y pruebas de restauración.

## Ejecución

El proyecto requiere Docker, Docker Compose y las configuraciones de entorno correspondientes.

Para construir e iniciar los servicios de Docker Compose:

```bash
docker compose up -d --build
```

Para consultar su estado:

```bash
docker compose ps
```

Para detener los servicios:

```bash
docker compose down
```

El despliegue en Kubernetes utiliza los manifiestos de `kubernetes/` y requiere configurar previamente los Secrets, certificados y servicios correspondientes.

## Seguridad

Las credenciales, claves privadas y respaldos sensibles no se incluyen en el repositorio. Se utiliza `.gitignore` para excluir archivos locales y privados.

## Estado del proyecto

Versión académica de laboratorio. Se han implementado funcionalidades de gestión académica, despliegue en K3s, políticas de red, escalado horizontal, monitoreo y procedimientos de respaldo y recuperación.

La separación completa entre desarrollo y producción y otras pruebas avanzadas forman parte de las mejoras pendientes.

## Autoría

Proyecto académico desarrollado por Shelvy Miroslava Bucio Hurtado - 22120635.

## Versión

1.0.0 — Versión inicial.
