from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import models, schemas, session

router = APIRouter(prefix="/bookings", tags=["bookings"])

def get_db():
    db = session.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.PrenotazioneRead)
def create_prenotazione(prenotazione: schemas.PrenotazioneCreate, db: Session = Depends(get_db)):
    new_booking = models.Prenotazione(**prenotazione.dict())
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking

@router.get("/", response_model=list[schemas.PrenotazioneRead])
def read_prenotazioni(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Prenotazione).offset(skip).limit(limit).all()
