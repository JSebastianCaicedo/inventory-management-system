from datetime import datetime, timedelta, timezone
from jose import jwt

JWT_SECRET = "randomkey"
JWT_ALG = "HS256"
JWT_EXPIRE_MIN = 480

def crear_token(usuario: str, rol: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": usuario,
        "rol": rol,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes = JWT_EXPIRE_MIN)).timestamp())
    }

    return jwt.encode(payload, JWT_SECRET, algorithm = JWT_ALG)

def verificar_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms = [JWT_ALG])