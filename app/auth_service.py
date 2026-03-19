import sqlite3
from datetime import datetime, timezone
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

def autenticar(db_path, nombre, clave_ingresada):
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT rowid, password_hash
            FROM usuarios
            WHERE nombre = ?               
        """, (nombre, ))
        row = cursor.fetchone()

        if not row:
            return False
        
        if row["password_hash"]:
            try:
                return ph.verify(row["password_hash"], clave_ingresada)
            
            except VerifyMismatchError:
                return False
             
        if row["clave"] and row["clave"] == clave_ingresada:
            new_hash = ph.hash(clave_ingresada)
            updated_at = datetime.now(timezone.utc).isoformat()

            cursor.execute("""
                UPDATE usuarios
                SET password_hash = ?, password_alg = 'argon2id', password_updated_aT = ?
                WHERE rowid = ?     
            """, (new_hash, updated_at, row["rowid"]))
            connection.commit()
            return True