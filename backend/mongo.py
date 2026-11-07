from pymongo import MongoClient
from datetime import datetime, timezone

import os

cliente_mongo = MongoClient(
    os.getenv(
        "MONGO_URI",
        "mongodb://localhost:27017/"
    ),
    serverSelectionTimeoutMS=5000
)

base_mongo = cliente_mongo["fulfill_logs"]

historial = base_mongo["historial_modificaciones"]

def registrar_movimiento(
    usuario_id,
    accion,
    entidad,
    entidad_id,
    detalles=None
):
    documento = {
        "usuario_id": usuario_id,
        "accion": accion,
        "entidad": entidad,
        "entidad_id": entidad_id,
        "detalles": detalles or {},
        "fecha": datetime.now(timezone.utc)
    }

    resultado = historial.insert_one(documento)

    return str(resultado.inserted_id)
