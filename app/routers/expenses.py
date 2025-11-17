from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import models, schemas, session

router = APIRouter(prefix="/expenses", tags=["expenses"])

def get_db():
    db = session.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.SpesaRead)
def create_spesa(spesa: schemas.SpesaCreate, db: Session = Depends(get_db)):
    new_spesa = models.Spesa(**spesa.dict())
    db.add(new_spesa)
    db.commit()
    db.refresh(new_spesa)
    return new_spesa

@router.get("/", response_model=list[schemas.SpesaRead])
def read_spese(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Spesa).offset(skip).limit(limit).all()
