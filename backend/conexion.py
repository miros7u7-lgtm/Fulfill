import os
import psycopg
from pathlib import Path
from dotenv import load_dotenv

# Buscar el archivo .env en la carpeta principal Fulfill
ruta_env = Path(__file__).resolve().parent.parent / ".env"

# Cargar las variables de entorno
load_dotenv(ruta_env)

print("Conectando con PostgreSQL...")

try:
    with psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        connect_timeout=5
    ) as conexion:

        with conexion.cursor() as cursor:
            cursor.execute("SELECT current_database();")
            resultado = cursor.fetchone()

        print("¡Conexión exitosa con Fulfill!")
        print("Base de datos:", resultado[0])

except psycopg.Error as error:
    print("No se pudo conectar con PostgreSQL.")
    print("Tipo de error:", type(error).__name__)
