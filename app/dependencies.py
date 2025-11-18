from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import models, session
from jose import jwt, JWTError
from app.routers.auth import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# =========================
# Dipendenza DB
# =========================
def get_db():
    db = session.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# Dipendenza per ottenere l'utente corrente dal token
# =========================
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossibile autenticare l'utente",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.Dipendente).filter(models.Dipendente.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user

# =========================
# Dipendenza generica per controllare il ruolo
# =========================
def require_role(required_roles: list):
    def role_checker(current_user: models.Dipendente = Depends(get_current_user)):
        if current_user.ruolo not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permesso negato"
            )
        return current_user
    return role_checker

# =========================
# Dipendenze specifiche per i ruoli
# =========================
get_current_dipendente = require_role(["dipendente"])
get_current_manager = require_role(["manager"])
get_current_admin = require_role(["admin"])
get_current_manager_or_admin = require_role(["manager", "admin"])
