from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import models, schemas, session

router = APIRouter(prefix="/transfers", tags=["transfers"])

def get_db():
    db = session.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.TrasfertaRead)
def create_trasferta(trasferta: schemas.TrasfertaCreate, db: Session = Depends(get_db)):
    new_trasferta = models.Trasferta(**trasferta.dict())
    db.add(new_trasferta)
    db.commit()
    db.refresh(new_trasferta)
    return new_trasferta

@router.get("/", response_model=list[schemas.TrasfertaRead])
def read_trasferte(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Trasferta).offset(skip).limit(limit).all()
