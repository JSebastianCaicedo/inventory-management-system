from PySide6.QtCore import QTimer
from queue_store import fetch_pending, mark_sent, mark_error

class SyncManager:
    def __init__(self, api_client, queue_db_path):
        self.api = api_client
        self.queue_db_path = queue_db_path
        self.timer = QTimer()
        self.timer.setInterval(10_000) #Each 10 seconds
        self.timer.timeout.connect(self.sync_once)

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def sync_once(self):
        pending = fetch_pending(self.queue_db_path, limit = 20)
        for m in pending:
            payload = {
                "id": m["id_movimiento"],
                "timestamp_utc": m["timestamp_utc"],
                "sku": m["sku"],
                "delta": m["delta"],
                "tipo": m["tipo"],
                "usuario": m["usuario"],
                "maquina_id": m["maquina_id"]
            }
            try:
                r = self.api.post_movimiento(payload)
                if r.status_code == 200:
                    mark_sent(self.queue_db_path, m["id_movimiento"])
                else:
                    mark_error(self.queue_db_path, m["id_movimiento"], f"{r.status_code}: {r.text}")
            except Exception as e:
                mark_error(self.queue_db_path, m["id_movimiento"], str(e))
                break