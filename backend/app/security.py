from datetime import datetime, timedelta, timezone
from hashlib import pbkdf2_hmac
from hmac import compare_digest
from secrets import token_urlsafe
from jose import jwt, JWTError
from .config import settings

ALGORITHM = "HS256"
ACCESS_MINUTES = 30
REFRESH_DAYS = 14

def hash_password(password: str) -> str:
    salt = token_urlsafe(16)
    digest = pbkdf2_hmac("sha256", password.encode(), salt.encode(), 240_000).hex()
    return f"pbkdf2$240000${salt}${digest}"

def verify_password(password: str, stored: str) -> bool:
    try:
        _, rounds, salt, digest = stored.split("$")
        candidate = pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(rounds)).hex()
        return compare_digest(candidate, digest)
    except (ValueError, TypeError):
        return False

def create_token(subject: str, tenant_id: str, role: str, kind: str, expires: timedelta) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode({"sub": subject, "tenant_id": tenant_id, "role": role, "kind": kind, "iat": now, "exp": now + expires}, settings.jwt_secret, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise ValueError("invalid token") from exc

