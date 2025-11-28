from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Header
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import models, schemas
from app.dependencies import get_db, require_role
import shutil
import os
import json
import io

router = APIRouter(prefix="/prenotazioni", tags=["prenotazioni"])

UPLOAD_DIR = "uploads/biglietti"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ------------------------
# Fallback temporaneo per l'ID utente
# ------------------------
async def get_user_id(x_user_id: Optional[int] = Header(None)):
    return x_user_id or 1

# ==============================
# CREA PRENOTAZIONE
# ==============================
@router.post("/crea", response_model=schemas.PrenotazioneRead)
def create_prenotazione(
    prenotazione: str = Form(...),
    file_biglietto: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: models.Dipendente = Depends(require_role(["dipendente", "manager", "admin"]))
):
    prenotazione_data = schemas.PrenotazioneCreate(**json.loads(prenotazione))

    trasferta = db.query(models.Trasferta).filter(models.Trasferta.id == prenotazione_data.id_trasferta).first()
    if not trasferta or trasferta.id_dipendente != current_user.id:
        raise HTTPException(status_code=403, detail="Non puoi aggiungere prenotazioni a questa trasferta")

    # Salvataggio file
    filename = None
    if file_biglietto:
        filename = f"{UPLOAD_DIR}/{file_biglietto.filename}"
        with open(filename, "wb") as buffer:
            shutil.copyfileobj(file_biglietto.file, buffer)

    # Crea prenotazione con campi trasporto e alloggio
    new_prenotazione = models.Prenotazione(
        id_trasferta=prenotazione_data.id_trasferta,
        tipo_mezzo=prenotazione_data.tipo_mezzo,
        fornitore=prenotazione_data.fornitore,
        costo=prenotazione_data.costo,
        dettagli=prenotazione_data.dettagli,
        file_biglietto=filename,
        tipo_alloggio=getattr(prenotazione_data, "tipo_alloggio", None),
        nome_struttura=getattr(prenotazione_data, "nome_struttura", None),
        costo_alloggio=getattr(prenotazione_data, "costo_alloggio", None)
    )

    db.add(new_prenotazione)
    db.commit()
    db.refresh(new_prenotazione)
    return new_prenotazione


# ==============================
# LISTA PRENOTAZIONI UTENTE
# ==============================
@router.get("/mie", response_model=List[schemas.PrenotazioneRead])
def get_my_prenotazioni(
    db: Session = Depends(get_db),
    current_user: models.Dipendente = Depends(require_role(["dipendente", "manager", "admin"]))
):
    return db.query(models.Prenotazione)\
             .join(models.Trasferta)\
             .filter(models.Trasferta.id_dipendente == current_user.id)\
             .all()


# ==============================
# LISTA TUTTE LE PRENOTAZIONI
# ==============================
@router.get("/", response_model=List[schemas.PrenotazioneRead])
def get_all_prenotazioni(
    db: Session = Depends(get_db),
    current_user: models.Dipendente = Depends(require_role(["manager", "admin"]))
):
    return db.query(models.Prenotazione).all()


# ==============================
# SCARICA FILE DI UNA PRENOTAZIONE
# ==============================
@router.get("/file/{file_id}")
def download_prenotazione_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_user_id)
):
    file_rec = db.query(models.Prenotazione).filter(models.Prenotazione.id == file_id).first()
    if not file_rec or not file_rec.file_biglietto:
        raise HTTPException(status_code=404, detail="File non trovato")

    trasferta = db.query(models.Trasferta).filter(models.Trasferta.id == file_rec.id_trasferta).first()
    if trasferta.id_dipendente != current_user_id:
        raise HTTPException(status_code=403, detail="Permesso negato")

    try:
        with open(file_rec.file_biglietto, "rb") as f:
            file_data = f.read()
    except Exception:
        raise HTTPException(status_code=500, detail="Impossibile leggere il file")

    mime = "application/pdf" if file_rec.file_biglietto.endswith(".pdf") else "image/jpeg"
    return StreamingResponse(
        io.BytesIO(file_data),
        media_type=mime,
        headers={"Content-Disposition": f'inline; filename="{os.path.basename(file_rec.file_biglietto)}"'}
    )
