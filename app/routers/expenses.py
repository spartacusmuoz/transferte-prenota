from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.database import models, schemas, session
from app.dependencies import get_db, require_role, get_current_user
import shutil
import os

router = APIRouter(prefix="/spese", tags=["spese"])

UPLOAD_DIR = "uploads/scontrini"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ==============================
# DIPENDENTE: aggiungi spesa
# ==============================
@router.post("/", response_model=schemas.SpesaRead)
def create_spesa(
    spesa: schemas.SpesaCreate,
    file_scontrino: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: models.Dipendente = Depends(require_role(["dipendente", "manager", "admin"]))
):
    trasferta = db.query(models.Trasferta).filter(models.Trasferta.id == spesa.id_trasferta).first()
    if not trasferta or trasferta.id_dipendente != current_user.id:
        raise HTTPException(status_code=403, detail="Non puoi aggiungere spese a questa trasferta")

    filename = None
    if file_scontrino:
        filename = f"{UPLOAD_DIR}/{file_scontrino.filename}"
        with open(filename, "wb") as buffer:
            shutil.copyfileobj(file_scontrino.file, buffer)

    new_spesa = models.Spesa(
        id_trasferta=spesa.id_trasferta,
        categoria=spesa.categoria,
        importo=spesa.importo,
        valuta=spesa.valuta,
        file_scontrino=filename,
        data_spesa=spesa.data_spesa
    )
    db.add(new_spesa)
    db.commit()
    db.refresh(new_spesa)
    return new_spesa

# ==============================
# DIPENDENTE: lista spese proprie
# ==============================
@router.get("/mie", response_model=List[schemas.SpesaRead])
def get_my_spese(
    db: Session = Depends(get_db),
    current_user: models.Dipendente = Depends(require_role(["dipendente", "manager", "admin"]))
):
    return db.query(models.Spesa).join(models.Trasferta).filter(models.Trasferta.id_dipendente == current_user.id).all()

# ==============================
# SEGRETERIA/MANAGER: lista tutte spese
# ==============================
@router.get("/", response_model=List[schemas.SpesaRead])
def get_all_spese(
    db: Session = Depends(get_db),
    current_user: models.Dipendente = Depends(require_role(["manager", "admin"]))
):
    return db.query(models.Spesa).all()
