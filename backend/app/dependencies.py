from dataclasses import dataclass
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from .db import get_db
from .models import User
from .security import decode_token

bearer = HTTPBearer(auto_error=False)

@dataclass
class CurrentUser:
    user: User
    claims: dict

def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> CurrentUser:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try:
        claims = decode_token(credentials.credentials)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if claims.get("kind") != "access":
        raise HTTPException(status_code=401, detail="Access token required")
    user = db.get(User, claims.get("sub"))
    if not user or not user.is_active or user.tenant_id != claims.get("tenant_id"):
        raise HTTPException(status_code=401, detail="User is inactive or invalid")
    return CurrentUser(user=user, claims=claims)

def require_roles(*roles: str):
    def dependency(identity: CurrentUser = Depends(current_user)) -> CurrentUser:
        if identity.user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return identity
    return dependency

