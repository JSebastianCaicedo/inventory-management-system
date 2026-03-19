from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from db import get_conn

ph = PasswordHasher()

def verificar_usuario(nombre: str, clave: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT password_hash, activo, rol
        FROM usuarios
        WHERE nombre = %s        
    """, (nombre, ))
    row = cur.fetchone()
    conn.close()

    if not row:
        return {"ok": False}
    
    hash_guardado, activo, rol = row

    if not activo:
        return {"ok": False}
    
    try:
        ph.verify(hash_guardado, clave)
        return {"ok": True, "rol": rol}
    except VerifyMismatchError:
        return {"ok": False}