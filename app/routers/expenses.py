# app/routers/expenses.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Header
from fastapi.responses import StreamingResponse
from typing import List, Optional
from sqlalchemy.orm import Session
import base64
import io

from app.database import schemas, crud, models
from app.dependencies import get_db  # non usiamo più get_current_user temporaneamente

router = APIRouter(prefix="/spese", tags=["spese"])

# ------------------------
# Dipendenza per ottenere l'ID dipendente dall'header x-user-id
# ------------------------
async def get_user_id(x_user_id: Optional[int] = Header(None)):
    if x_user_id is None:
        x_user_id = 1  # fallback a 1 se non specificato
    return x_user_id

# ------------------------
# Create spesa with files (multipart/form-data)
# ------------------------
@router.post("/", response_model=schemas.SpesaRead, status_code=status.HTTP_201_CREATED)
async def create_spesa_with_files(
    id_trasferta: int = Form(...),
    categoria: str = Form(...),
    importo: float = Form(...),
    valuta: str = Form("EUR"),
    tipo_scontrino: models.TipoScontrinoEnum = Form(...),
    data_spesa: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_user_id),  # <-- ID dinamico
):
    """
    Crea una spesa e allega eventuali file (immagini, pdf, ecc).
    """
    # Validazione base: la trasferta deve esistere e appartenere al dipendente
    trasferta = db.query(models.Trasferta).filter(
        models.Trasferta.id == id_trasferta,
        models.Trasferta.id_dipendente == current_user_id
    ).first()
    if not trasferta:
        raise HTTPException(status_code=404, detail="Trasferta non trovata o non appartiene al dipendente selezionato")

    spesa_in = schemas.SpesaCreate(
        id_trasferta=id_trasferta,
        categoria=categoria,
        importo=importo,
        valuta=valuta,
        tipo_scontrino=tipo_scontrino,
        data_spesa=data_spesa
    )

    files_data = []
    if files:
        for f in files:
            content = await f.read()
            b64 = base64.b64encode(content).decode("utf-8")
            files_data.append({"filename": f.filename, "mimetype": f.content_type, "data": b64})

    created = crud.create_spesa(db=db, spesa_in=spesa_in, creator_id=current_user_id, files_data=files_data)
    return created

# ------------------------
# Lista spese per dipendente specificato
# ------------------------
@router.get("/mine", response_model=List[schemas.SpesaRead])
def get_my_spese(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_user_id)
):
    spese = crud.list_spese_by_user(db, current_user_id)
    return spese

# ------------------------
# Lista tutte le spese (temporaneamente senza controlli ruolo)
# ------------------------
@router.get("/", response_model=List[schemas.SpesaRead])
def get_all_spese(db: Session = Depends(get_db)):
    return crud.list_all_spese(db)

# ------------------------
# Download / view specific file
# ------------------------
@router.get("/file/{file_id}")
def download_spesa_file(file_id: int, db: Session = Depends(get_db), current_user_id: int = Depends(get_user_id)):
    file_rec = crud.get_spesa_file(db, file_id)
    if not file_rec:
        raise HTTPException(status_code=404, detail="File non trovato")

    spesa = crud.get_spesa(db, file_rec.id_spesa)
    trasferta = db.query(models.Trasferta).filter(models.Trasferta.id == spesa.id_trasferta).first()
    if trasferta.id_dipendente != current_user_id:
        raise HTTPException(status_code=403, detail="Permesso negato")

    try:
        raw = base64.b64decode(file_rec.data)
    except Exception:
        raise HTTPException(status_code=500, detail="Errore nel decodificare il file")

    return StreamingResponse(
        io.BytesIO(raw),
        media_type=file_rec.mimetype or "application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{file_rec.filename}"'}
    )

# ------------------------
# Delete file
# ------------------------
@router.delete("/file/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(file_id: int, db: Session = Depends(get_db), current_user_id: int = Depends(get_user_id)):
    file_rec = crud.get_spesa_file(db, file_id)
    if not file_rec:
        raise HTTPException(status_code=404, detail="File non trovato")
    spesa = crud.get_spesa(db, file_rec.id_spesa)
    trasferta = db.query(models.Trasferta).filter(models.Trasferta.id == spesa.id_trasferta).first()

    if trasferta.id_dipendente != current_user_id:
        raise HTTPException(status_code=403, detail="Permesso negato")

    ok = crud.delete_spesa_file(db, file_id)
    if not ok:
        raise HTTPException(status_code=500, detail="Impossibile cancellare il file")
    return None
