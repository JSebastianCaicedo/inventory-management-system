import requests
from typing import Optional, Dict, Any

class ApiClient:
    def __init__(self, base_url: str, timeout_s: float = 5.0):
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s
        self.token: Optional[str] = None
        self.usuario: Optional[str] = None
        self.rol: Optional[str] = None

    def login(self, nombre: str, clave: str) -> bool:
        url = f"{self.base_url}/login"
        r = requests.post(url, json = {"nombre": nombre, "clave": clave}, timeout = self.timeout_s)
        if r.status_code != 200:
            return False
        data = r.json()
        if not data.get("ok"):
            return False
        self.token = data["token"]
        self.usuario = nombre
        self.rol = data.get("rol")
        return True
    
    def post_movimiento(self, payload: Dict[str, Any]) -> requests.Response:
        if not self.token:
            raise RuntimeError("No hay token. Debes iniciar sesión primero.")
        url = f"{self.base_url}/movimientos"
        headers = {"Authorization": f"Bearer {self.token}"}
        return requests.post(url, json = payload, headers = headers, timeout = self.timeout_s)
    
    def get_producto(self, sku):
        headers = {"Authorization": f"Bearer {self.token}"}
        r = requests.get(
            f"{self.base_url}/productos/{sku}", 
            headers = headers,
            timeout = self.timeout_s
            )
        
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 404:
            return None
        else:
            raise Exception(f"Error {r.status_code}: {r.text}")
        
    def generar_reporte(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        r = requests.post(
            f"{self.base_url}/reportes/lote",
            headers = headers,
            timeout = self.timeout_s
        )
        return r