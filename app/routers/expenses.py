# app/routers/expenses.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Header
from fastapi.responses import StreamingResponse
from typing import List, Optional, Union
from sqlalchemy.orm import Session
import base64
import io

from app.database import schemas, crud, models
from app.dependencies import get_db

router = APIRouter(prefix="/spese", tags=["spese"])

# ------------------------
# Fallback temporaneo per l'ID utente
# ------------------------
async def get_user_id(x_user_id: Optional[int] = Header(None)):
    return x_user_id or 1

# ------------------------
# CREA SPESA + UPLOAD FILES
# ------------------------
@router.post("/", response_model=schemas.SpesaRead, status_code=status.HTTP_201_CREATED)
async def create_spesa_with_files(
    id_trasferta: int = Form(...),
    categoria: str = Form(...),
    importo: float = Form(...),
    valuta: str = Form("EUR"),
    tipo_scontrino: str = Form("altro"),  # aggiornato a stringa
    data_spesa: str = Form(...),
    files: Optional[Union[UploadFile, List[UploadFile]]] = File(None),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_user_id)
):
    """
    Crea una spesa collegata a una trasferta e gestisce sia singolo file sia più file.
    """

    # Normalizza a lista
    files_list = []
    if files:
        if isinstance(files, list):
            files_list = files
        else:
            files_list = [files]

    # --- Validazione: trasferta esiste e appartiene al dipendente ---
    trasferta = db.query(models.Trasferta).filter(
        models.Trasferta.id == id_trasferta,
        models.Trasferta.id_dipendente == current_user_id
    ).first()

    if not trasferta:
        raise HTTPException(
            status_code=404,
            detail="Trasferta non trovata o non appartiene al dipendente"
        )

    # --- Costruzione oggetto spesa ---
    spesa_in = schemas.SpesaCreate(
        id_trasferta=id_trasferta,
        categoria=categoria,
        importo=importo,
        valuta=valuta,
        tipo_scontrino=tipo_scontrino,  # stringa
        data_spesa=data_spesa
    )

    # --- Preparazione file ---
    files_data = []
    for f in files_list:
        if f.content_type not in ["image/jpeg", "image/png", "application/pdf"]:
            raise HTTPException(
                status_code=400,
                detail=f"Formato non valido per il file {f.filename}"
            )
        data = await f.read()
        files_data.append({
            "filename": f.filename,
            "mimetype": f.content_type,
            "data": base64.b64encode(data).decode("utf-8")
        })

    # --- Salvataggio nel DB ---
    created = crud.create_spesa(
        db=db,
        spesa_in=spesa_in,
        creator_id=current_user_id,
        files_data=files_data
    )

    return created

# ------------------------
# GET - Spese mie
# ------------------------
@router.get("/mine", response_model=List[schemas.SpesaRead])
def get_my_spese(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_user_id),
):
    return crud.list_spese_by_user(db, current_user_id)

# ------------------------
# GET - Tutte le spese
# ------------------------
@router.get("/", response_model=List[schemas.SpesaRead])
def get_all_spese(db: Session = Depends(get_db)):
    return crud.list_all_spese(db)

# ------------------------
# DOWNLOAD FILE
# ------------------------
@router.get("/file/{file_id}")
def download_spesa_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_user_id)
):
    file_rec = crud.get_spesa_file(db, file_id)
    if not file_rec:
        raise HTTPException(status_code=404, detail="File non trovato")

    spesa = crud.get_spesa(db, file_rec.id_spesa)
    trasferta = db.query(models.Trasferta).filter(
        models.Trasferta.id == spesa.id_trasferta
    ).first()

    if trasferta.id_dipendente != current_user_id:
        raise HTTPException(status_code=403, detail="Permesso negato")

    return StreamingResponse(
        io.BytesIO(base64.b64decode(file_rec.data)),
        media_type=file_rec.mimetype or "application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{file_rec.filename}"'}
    )

# ------------------------
# DELETE FILE
# ------------------------
@router.delete("/file/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_user_id)
):
    file_rec = crud.get_spesa_file(db, file_id)
    if not file_rec:
        raise HTTPException(status_code=404, detail="File non trovato")

    spesa = crud.get_spesa(db, file_rec.id_spesa)
    trasferta = db.query(models.Trasferta).filter(
        models.Trasferta.id == spesa.id_trasferta
    ).first()

    if trasferta.id_dipendente != current_user_id:
        raise HTTPException(status_code=403, detail="Permesso negato")

    crud.delete_spesa_file(db, file_id)
    return None
