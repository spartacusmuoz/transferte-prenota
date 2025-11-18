from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import models, schemas, session
from app.dependencies import get_db, require_role, get_current_user

router = APIRouter(prefix="/trasferte", tags=["trasferte"])

# ==============================
# DIPENDENTE: crea trasferta
# ==============================
@router.post("/", response_model=schemas.TrasfertaRead)
def create_trasferta(
    trasferta: schemas.TrasfertaCreate,
    db: Session = Depends(get_db),
    current_user: models.Dipendente = Depends(require_role(["dipendente", "manager", "admin"]))
):
    new_trasferta = models.Trasferta(
        id_dipendente=current_user.id,
        data_partenza=trasferta.data_partenza,
        data_rientro=trasferta.data_rientro,
        luogo_destinazione=trasferta.luogo_destinazione,
        luogo_extra=trasferta.luogo_extra,
        tipo_commessa=trasferta.tipo_commessa,
        stato=trasferta.stato,
        note_dipendente=trasferta.note_dipendente
    )
    db.add(new_trasferta)
    db.commit()
    db.refresh(new_trasferta)
    return new_trasferta

# ==============================
# DIPENDENTE: lista trasferte proprie
# ==============================
@router.get("/miei", response_model=List[schemas.TrasfertaRead])
def get_my_trasferte(
    db: Session = Depends(get_db),
    current_user: models.Dipendente = Depends(require_role(["dipendente", "manager", "admin"]))
):
    return db.query(models.Trasferta).filter(models.Trasferta.id_dipendente == current_user.id).all()

# ==============================
# SEGRETERIA/MANAGER/ADMIN: lista tutte trasferte
# ==============================
@router.get("/", response_model=List[schemas.TrasfertaRead])
def get_all_trasferte(
    db: Session = Depends(get_db),
    current_user: models.Dipendente = Depends(require_role(["manager", "admin"]))
):
    return db.query(models.Trasferta).all()

# ==============================
# SEGRETERIA/MANAGER: approva/rifiuta trasferta
# ==============================
@router.patch("/{trasferta_id}/stato", response_model=schemas.TrasfertaRead)
def update_stato_trasferta(
    trasferta_id: int,
    stato: schemas.TrasfertaUpdate,
    db: Session = Depends(get_db),
    current_user: models.Dipendente = Depends(require_role(["manager", "admin"]))
):
    trasferta = db.query(models.Trasferta).filter(models.Trasferta.id == trasferta_id).first()
    if not trasferta:
        raise HTTPException(status_code=404, detail="Trasferta non trovata")
    
    if stato.stato:
        trasferta.stato = stato.stato
    if stato.note_segreteria:
        trasferta.note_segreteria = stato.note_segreteria

    db.commit()
    db.refresh(trasferta)
    return trasferta
