from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from uuid import UUID
from db import get_conn
from auth import verificar_usuario
from datetime import datetime
from zoneinfo import ZoneInfo
from token_service import crear_token, verificar_token
import pandas as pd
import os

app = FastAPI()

REPORTES_DIR = r'C:\Users\JohnDoe'
tz_bog = ZoneInfo("America/Miami")
ahora_local = datetime.now(tz_bog)

class LoginRequest(BaseModel):
    nombre: str
    clave: str

class MovimientoRequest(BaseModel):
    id: UUID
    timestamp_utc: datetime
    sku: str
    delta: int
    tipo: str
    usuario: str
    maquina_id: str

@app.post("/login")
def login(req: LoginRequest):
    r = verificar_usuario(req.nombre, req.clave)
    if r and r.get("ok"):
        token = crear_token(req.nombre, r["rol"])
        return {"ok": True, "token": token, "rol": r["rol"]}
    raise HTTPException(status_code = 401, detail = "Credenciales inválidas")

@app.post("/movimientos")
def crear_movimiento(req: MovimientoRequest, authorization: str | None = Header(default = None)):
    claims = exigir_token(authorization)

    usuario_token = claims["sub"]
    rol = claims.get("rol", "")

    if rol not in ("OPERADOR", "ADMIN"):
        raise HTTPException(status_code = 403, detail = "Rol inválido")
    
    usuario_final = usuario_token

    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO movimientos (id, timestamp_utc, sku, delta, tipo, usuario, maquina_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)            
        """, (str(req.id), req.timestamp_utc, req.sku, req.delta, req.tipo, usuario_final, req.maquina_id))

        conn.commit()
        return {"status": "OK"}
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code = 400, detail = str(e))
    
    finally:
        conn.close()

def exigir_token(authorization: str | None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code = 401, detail = "Falta token Bearer")
    token = authorization.split(" ", 1)[1].strip()
    try:
        claims = verificar_token(token)
        return claims #usuario y rol
    except Exception:
        raise HTTPException(status_code = 401, detail = "Token inválido o expirado")
    
@app.get("/productos/{sku}")
def obtener_producto(sku: str, authorization: str | None = Header(default = None)):
    claims = exigir_token(authorization)

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, sku, nombre
        FROM productos
        WHERE sku = %s AND activo = TRUE         
    """, (sku, ))

    row = cur.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code = 404, detail = "Producto no encontrado")
    
    return {
        "id": row[0],
        "sku": row[1],
        "nombre": row[2]
    }

@app.post("/reportes/lote/")
def generar_reporte_lote(authorization: str | None = Header(default = None)):
    claims = exigir_token(authorization)
    usuario = claims["sub"]

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT sku, delta, tipo, usuario, maquina_id, timestamp_utc
        FROM movimientos
        ORDER BY timestamp_utc DESC            
    """)

    rows = cur.fetchall()
    conn.close()

    df = pd.DataFrame(rows, columns = [
        "Código", "Cantidad", "Tipo", "Usuario", "Máquina", "Fecha UTC"
    ])

    timestamp = ahora_local.strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"reporte_{timestamp}_{usuario}.xlsx"

    year_folder = os.path.join(REPORTES_DIR, datetime.utcnow().strftime("%Y"))
    os.makedirs(year_folder, exist_ok = True)

    path = os.path.join(year_folder, filename)

    df.to_excel(path, index = False)

    return {"ok": True, "archivo": filename}