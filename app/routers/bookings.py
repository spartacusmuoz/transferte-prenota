from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from app.database import models, schemas
from app.dependencies import get_db, require_role
import shutil
import os
import json

router = APIRouter(prefix="/prenotazioni", tags=["prenotazioni"])

UPLOAD_DIR = "uploads/biglietti"
os.makedirs(UPLOAD_DIR, exist_ok=True)



# ==============================
# DIPENDENTE: aggiungi prenotazione
# ==============================
@router.post("/crea", response_model=schemas.PrenotazioneRead)
def create_prenotazione(
    prenotazione: str = Form(...),             # riceve il JSON come stringa
    file_biglietto: UploadFile = File(None),  # riceve il file
    db: Session = Depends(get_db),
    current_user: models.Dipendente = Depends(require_role(["dipendente", "manager", "admin"]))
):
    # Converti la stringa JSON in Pydantic
    prenotazione_data = schemas.PrenotazioneCreate(**json.loads(prenotazione))

    trasferta = db.query(models.Trasferta).filter(models.Trasferta.id == prenotazione_data.id_trasferta).first()
    if not trasferta or trasferta.id_dipendente != current_user.id:
        raise HTTPException(status_code=403, detail="Non puoi aggiungere prenotazioni a questa trasferta")

    filename = None
    if file_biglietto:
        filename = f"{UPLOAD_DIR}/{file_biglietto.filename}"
        with open(filename, "wb") as buffer:
            shutil.copyfileobj(file_biglietto.file, buffer)

    new_prenotazione = models.Prenotazione(
        id_trasferta=prenotazione_data.id_trasferta,
        tipo_mezzo=prenotazione_data.tipo_mezzo,
        fornitore=prenotazione_data.fornitore,
        costo=prenotazione_data.costo,
        dettagli=prenotazione_data.dettagli,
        file_biglietto=filename
    )
    db.add(new_prenotazione)
    db.commit()
    db.refresh(new_prenotazione)
    return new_prenotazione


# ==============================
# DIPENDENTE: lista prenotazioni proprie
# ==============================
@router.get("/mie", response_model=List[schemas.PrenotazioneRead])
def get_my_prenotazioni(
    db: Session = Depends(get_db),
    current_user: models.Dipendente = Depends(require_role(["dipendente", "manager", "admin"]))
):
    return db.query(models.Prenotazione).join(models.Trasferta).filter(models.Trasferta.id_dipendente == current_user.id).all()

# ==============================
# SEGRETERIA/MANAGER: lista tutte prenotazioni
# ==============================
@router.get("/", response_model=List[schemas.PrenotazioneRead])
def get_all_prenotazioni(
    db: Session = Depends(get_db),
    current_user: models.Dipendente = Depends(require_role(["manager", "admin"]))
):
    return db.query(models.Prenotazione).all()
