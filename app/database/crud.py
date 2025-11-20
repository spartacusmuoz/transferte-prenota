from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import base64

from app.database import models, schemas

# ------------------------
# Spesa + SpesaFile CRUD
# ------------------------
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
    # ritorna tutte le spese appartenenti alle trasferte del dipendente
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

# Utility helper: convert UploadFile bytes -> base64 dict
def file_to_base64_dict(uploaded_file) -> dict:
    """
    uploaded_file is a starlette UploadFile
    returns dict: { filename, mimetype, data }
    """
    content = uploaded_file.file.read()
    if isinstance(content, str):
        # ensure bytes
        content = content.encode("utf-8")
    b64 = base64.b64encode(content).decode("utf-8")
    return {"filename": uploaded_file.filename, "mimetype": uploaded_file.content_type, "data": b64}
