# routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.database import models, schemas, session
from app.dependencies import get_current_user, get_current_admin
from datetime import date

router = APIRouter(prefix="/users", tags=["users"])

# Dipendenza DB
def get_db():
    db = session.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# DIPENDENTE
# =========================

@router.post("/trasferte/", response_model=schemas.TrasfertaRead)
def create_trasferta(trasferta: schemas.TrasfertaCreate,
                     db: Session = Depends(get_db),
                     current_user: models.Dipendente = Depends(get_current_user)):
    new_trasferta = models.Trasferta(
        id_dipendente=current_user.id,
        data_partenza=trasferta.data_partenza,
        data_rientro=trasferta.data_rientro,
        luogo_destinazione=trasferta.luogo_destinazione,
        luogo_extra=trasferta.luogo_extra,
        tipo_commessa=trasferta.tipo_commessa,
        note_dipendente=trasferta.note_dipendente
    )
    db.add(new_trasferta)
    db.commit()
    db.refresh(new_trasferta)
    return new_trasferta


@router.get("/trasferte/", response_model=List[schemas.TrasfertaRead])
def get_mie_trasferte(db: Session = Depends(get_db),
                       current_user: models.Dipendente = Depends(get_current_user)):
    return db.query(models.Trasferta).filter(models.Trasferta.id_dipendente == current_user.id).all()


@router.post("/trasferte/{trasferta_id}/spese/", response_model=schemas.SpesaRead)
def carica_spesa(trasferta_id: int,
                 categoria: str,
                 importo: float,
                 data_spesa: date,
                 file_scontrino: UploadFile = File(None),
                 db: Session = Depends(get_db),
                 current_user: models.Dipendente = Depends(get_current_user)):
    trasferta = db.query(models.Trasferta).filter(models.Trasferta.id == trasferta_id,
                                                 models.Trasferta.id_dipendente == current_user.id).first()
    if not trasferta:
        raise HTTPException(status_code=404, detail="Trasferta non trovata")
    
    file_path = None
    if file_scontrino:
        file_path = f"uploads/{file_scontrino.filename}"
        with open(file_path, "wb") as f:
            f.write(file_scontrino.file.read())

    spesa = models.Spesa(
        id_trasferta=trasferta_id,
        categoria=categoria,
        importo=importo,
        data_spesa=data_spesa,
        file_scontrino=file_path
    )
    db.add(spesa)
    db.commit()
    db.refresh(spesa)
    return spesa


@router.post("/trasferte/{trasferta_id}/prenotazioni/", response_model=schemas.PrenotazioneRead)
def proporre_prenotazione(trasferta_id: int,
                          tipo_mezzo: models.TipoMezzoEnum,
                          fornitore: str = None,
                          costo: float = None,
                          dettagli: str = None,
                          file_biglietto: UploadFile = File(None),
                          db: Session = Depends(get_db),
                          current_user: models.Dipendente = Depends(get_current_user)):
    trasferta = db.query(models.Trasferta).filter(models.Trasferta.id == trasferta_id,
                                                 models.Trasferta.id_dipendente == current_user.id).first()
    if not trasferta:
        raise HTTPException(status_code=404, detail="Trasferta non trovata")
    
    file_path = None
    if file_biglietto:
        file_path = f"uploads/{file_biglietto.filename}"
        with open(file_path, "wb") as f:
            f.write(file_biglietto.file.read())
    
    prenotazione = models.Prenotazione(
        id_trasferta=trasferta_id,
        tipo_mezzo=tipo_mezzo,
        fornitore=fornitore,
        costo=costo,
        dettagli=dettagli,
        file_biglietto=file_path
    )
    db.add(prenotazione)
    db.commit()
    db.refresh(prenotazione)
    return prenotazione


# =========================
# SEGRETERIA / MANAGER / ADMIN
# =========================

@router.get("/trasferte/all", response_model=List[schemas.TrasfertaRead])
def get_tutte_trasferte(db: Session = Depends(get_db),
                         current_user: models.Dipendente = Depends(get_current_admin)):
    return db.query(models.Trasferta).all()


@router.patch("/trasferte/{trasferta_id}/approva", response_model=schemas.TrasfertaRead)
def approva_trasferta(trasferta_id: int,
                      note_segreteria: str = None,
                      db: Session = Depends(get_db),
                      current_user: models.Dipendente = Depends(get_current_admin)):
    trasferta = db.query(models.Trasferta).filter(models.Trasferta.id == trasferta_id).first()
    if not trasferta:
        raise HTTPException(status_code=404, detail="Trasferta non trovata")
    
    trasferta.stato = models.StatoTrasfertaEnum.approvata
    if note_segreteria:
        trasferta.note_segreteria = note_segreteria
    db.commit()
    db.refresh(trasferta)
    return trasferta


@router.patch("/trasferte/{trasferta_id}/rifiuta", response_model=schemas.TrasfertaRead)
def rifiuta_trasferta(trasferta_id: int,
                       note_segreteria: str = None,
                       db: Session = Depends(get_db),
                       current_user: models.Dipendente = Depends(get_current_admin)):
    trasferta = db.query(models.Trasferta).filter(models.Trasferta.id == trasferta_id).first()
    if not trasferta:
        raise HTTPException(status_code=404, detail="Trasferta non trovata")
    
    trasferta.stato = models.StatoTrasfertaEnum.rifiutata
    if note_segreteria:
        trasferta.note_segreteria = note_segreteria
    db.commit()
    db.refresh(trasferta)
    return trasferta


@router.get("/trasferte/{trasferta_id}/rimborsi")
def calcola_rimborso(trasferta_id: int,
                     db: Session = Depends(get_db),
                     current_user: models.Dipendente = Depends(get_current_admin)):
    trasferta = db.query(models.Trasferta).filter(models.Trasferta.id == trasferta_id).first()
    if not trasferta:
        raise HTTPException(status_code=404, detail="Trasferta non trovata")
    
    totale_spese = sum([s.importo for s in trasferta.spese])
    totale_prenotazioni = sum([p.costo or 0 for p in trasferta.prenotazioni])
    totale = totale_spese + totale_prenotazioni
    return {"totale_rimborso": totale}


@router.patch("/trasferte/{trasferta_id}/completa", response_model=schemas.TrasfertaRead)
def completa_trasferta(trasferta_id: int,
                        db: Session = Depends(get_db),
                        current_user: models.Dipendente = Depends(get_current_admin)):
    trasferta = db.query(models.Trasferta).filter(models.Trasferta.id == trasferta_id).first()
    if not trasferta:
        raise HTTPException(status_code=404, detail="Trasferta non trovata")
    
    trasferta.stato = models.StatoTrasfertaEnum.completata
    db.commit()
    db.refresh(trasferta)
    return trasferta
