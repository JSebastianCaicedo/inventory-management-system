from uuid import uuid4
from datetime import datetime, timezone
from queue_store import enqueue
from api_client import ApiClient

def procesar_movimiento(api: ApiClient, queue_db: str,
                        sku: str, delta: int,
                        tipo: str, usuario: str,
                        maquina_id: str):
    payload = {
        "id": str(uuid4()),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "sku": sku,
        "delta": int(delta),
        "tipo": tipo,
        "usuario": usuario,
        "maquina_id": maquina_id
    }

    try:
        r = api.post_movimiento(payload)

        #Éxito
        if r.status_code == 200:
            return True, None
        
        #Error lógico (ej: inventario insuficiente)
        if r.status_code == 400:
            detail = r.json().get("detail", "Error de negocio")
            return False, detail
        
        #Error de autenticación
        if r.status_code in (401, 403):
            return False, "No autorizado o sesión expirada"
        
        #Error servidor -> encolar
        enqueue(queue_db, payload)
        return False, "Servidor no disponible. Guardado para sincronizar."
    
    except Exception:
        enqueue(queue_db, payload)
        return False, "Error de conexión. Guardado para sincronizar."