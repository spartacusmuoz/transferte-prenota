from sqlalchemy.orm import Session
from typing import List, Optional
import base64
import shutil
import os

from app.database import models, schemas

# =========================
# Spese CRUD
# =========================

def create_spesa(db: Session, spesa_in: schemas.SpesaCreate, creator_id: int, files_data: Optional[List[dict]] = None) -> models.Spesa:
    """
    files_data: list of dict { filename, mimetype, data_base64 }
    """
    spesa = models.Spesa(
        id_trasferta=spesa_in.id_trasferta,
        categoria=spesa_in.categoria,
        importo=spesa_in.importo,
        valuta=spesa_in.valuta,
        tipo_scontrino=spesa_in.tipo_scontrino,
        file_scontrino=None,
        data_spesa=spesa_in.data_spesa
    )
    db.add(spesa)
    db.commit()
    db.refresh(spesa)

    # create SpesaFile records if present
    if files_data:
        for f in files_data:
            file_rec = models.SpesaFile(
                id_spesa=spesa.id,
                filename=f["filename"],
                mimetype=f.get("mimetype"),
                data=f["data"]  # already base64 string
            )
            db.add(file_rec)
        db.commit()
    db.refresh(spesa)
    return spesa

def get_spesa(db: Session, spesa_id: int) -> Optional[models.Spesa]:
    return db.query(models.Spesa).filter(models.Spesa.id == spesa_id).first()

def list_spese_by_user(db: Session, user_id: int) -> List[models.Spesa]:
    return db.query(models.Spesa).join(models.Trasferta).filter(models.Trasferta.id_dipendente == user_id).all()

def list_all_spese(db: Session) -> List[models.Spesa]:
    return db.query(models.Spesa).all()

def get_spesa_file(db: Session, file_id: int) -> Optional[models.SpesaFile]:
    return db.query(models.SpesaFile).filter(models.SpesaFile.id == file_id).first()

def delete_spesa_file(db: Session, file_id: int) -> bool:
    file_rec = db.query(models.SpesaFile).filter(models.SpesaFile.id == file_id).first()
    if not file_rec:
        return False
    db.delete(file_rec)
    db.commit()
    return True

def file_to_base64_dict(uploaded_file) -> dict:
    """
    uploaded_file: starlette UploadFile
    returns dict: { filename, mimetype, data }
    """
    content = uploaded_file.file.read()
    if isinstance(content, str):
        content = content.encode("utf-8")
    b64 = base64.b64encode(content).decode("utf-8")
    return {"filename": uploaded_file.filename, "mimetype": uploaded_file.content_type, "data": b64}

# =========================
# Prenotazioni CRUD
# =========================

UPLOAD_DIR = "uploads/biglietti"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_prenotazione_file(uploaded_file) -> str:
    """
    Salva il file sul filesystem e ritorna il percorso completo
    """
    filepath = os.path.join(UPLOAD_DIR, uploaded_file.filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)
    return filepath

def create_prenotazione(db: Session, prenotazione_in: schemas.PrenotazioneCreate, file_biglietto: Optional = None) -> models.Prenotazione:
    """
    Crea una prenotazione e salva eventuale file
    """
    filepath = None
    if file_biglietto:
        filepath = save_prenotazione_file(file_biglietto)

    prenotazione = models.Prenotazione(
        id_trasferta=prenotazione_in.id_trasferta,
        tipo_mezzo=prenotazione_in.tipo_mezzo,
        fornitore=prenotazione_in.fornitore,
        costo=prenotazione_in.costo,
        dettagli=prenotazione_in.dettagli,
        file_biglietto=filepath
    )
    db.add(prenotazione)
    db.commit()
    db.refresh(prenotazione)
    return prenotazione

def get_prenotazione(db: Session, prenotazione_id: int) -> Optional[models.Prenotazione]:
    return db.query(models.Prenotazione).filter(models.Prenotazione.id == prenotazione_id).first()

def list_prenotazioni_by_user(db: Session, user_id: int) -> List[models.Prenotazione]:
    return db.query(models.Prenotazione).join(models.Trasferta).filter(models.Trasferta.id_dipendente == user_id).all()

def list_all_prenotazioni(db: Session) -> List[models.Prenotazione]:
    return db.query(models.Prenotazione).all()
