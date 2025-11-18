from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import models, schemas, session
from app.dependencies import get_db, require_role
from app.routers.auth import get_password_hash

router = APIRouter(prefix="/admin", tags=["admin"])

# ==============================
# LISTA TUTTI GLI UTENTI
# ==============================
@router.get("/utenti", response_model=List[schemas.DipendenteRead])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: models.Dipendente = Depends(require_role(["admin"]))
):
    return db.query(models.Dipendente).all()

# ==============================
# RESET PASSWORD UTENTE
# ==============================
class PasswordResetRequest(schemas.BaseModel):
    new_password: str

@router.post("/utenti/{user_id}/reset-password", response_model=schemas.DipendenteRead)
def reset_user_password(
    user_id: int,
    req: PasswordResetRequest,
    db: Session = Depends(get_db),
    current_user: models.Dipendente = Depends(require_role(["admin"]))
):
    user = db.query(models.Dipendente).filter(models.Dipendente.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utente non trovato")

    hashed_password = get_password_hash(req.new_password)
    user.password = hashed_password
    db.commit()
    db.refresh(user)
    return user

# ==============================
# MODIFICA RUOLO UTENTE
# ==============================
class RoleUpdateRequest(schemas.BaseModel):
    ruolo: models.RuoloEnum

@router.patch("/utenti/{user_id}/ruolo", response_model=schemas.DipendenteRead)
def update_user_role(
    user_id: int,
    req: RoleUpdateRequest,
    db: Session = Depends(get_db),
    current_user: models.Dipendente = Depends(require_role(["admin"]))
):
    user = db.query(models.Dipendente).filter(models.Dipendente.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utente non trovato")

    user.ruolo = req.ruolo
    db.commit()
    db.refresh(user)
    return user
