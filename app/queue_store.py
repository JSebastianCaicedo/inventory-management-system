import sqlite3
from datetime import datetime, timezone
from typing import List, Dict, Any

def init_queue(db_path: str):
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cola_movimientos (
                     id_movimiento TEXT PRIMARY KEY,
                     timestamp_utc TEXT NOT NULL,
                     sku TEXT NOT NULL,
                     delta INTEGER NOT NULL,
                     tipo TEXT NOT NULL,
                     usuario TEXT NOT NULL,
                     maquina_id TEXT NOT NULL,
                     estado TEXT NOT NULL DEFAULT 'PENDIENTE',
                     reintentos INTEGER NOT NULL DEFAULT 0,
                     ultimo_error TEXT,
                     creado_en TEXT NOT NULL
            );             
        """)
        conn.commit()

def enqueue(db_path: str, mov: Dict[str, Any]):
    now = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            INSERT OR REPLACE INTO cola_movimientos
            (id_movimiento, timestamp_utc, sku, delta, tipo, usuario, maquina_id, estado, reintentos, ultimo_error, creado_en)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'PENDIENTE', 0, NULL, ?)     
        """, (
            str(mov["id"]),
            mov["timestamp_utc"],
            mov["sku"],
            int(mov["delta"]),
            mov["tipo"],
            mov["usuario"],
            mov["maquina_id"],
            now
        ))
        conn.commit()

def fetch_pending(db_path: str, limit: int = 50) -> List[Dict[str, Any]]:
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
                    SELECT * FROM cola_movimientos
                    WHERE estado = 'PENDIENTE'
                    ORDER BY creado_en ASC
                    LIMIT ?
        """, (limit, )).fetchall()
        return [dict(r) for r in rows]
    
def mark_sent(db_path: str, id_movimiento: str):
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            UPDATE cola_movimientos SET estado='ENVIADO', ultimo_error=NULL
            WHERE id_movimiento=?             
        """, (id_movimiento, ))
        conn.commit()

def mark_error(db_path: str, id_movimiento: str, err: str):
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            UPDATE cola_movimientos
            SET reintentos = reintentos + 1,
                ultimo_error = ?,
                estado = 'PENDIENTE'
            WHERE id_movimiento=?             
        """, (err[:500], id_movimiento))
        conn.commit()