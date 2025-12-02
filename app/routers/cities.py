from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.database.models import Trasferta

router = APIRouter(prefix="/cities", tags=["cities"])

@router.get("/{city_name}")
def check_city(city_name: str, db: Session = Depends(get_db)):
    trasferta = db.query(Trasferta).filter(
        (Trasferta.luogo_destinazione == city_name) |
        (Trasferta.luogo_extra == city_name)
    ).first()

    if not trasferta:
        raise HTTPException(status_code=404, detail="Città non trovata nel database")

    return {
        "city": city_name,
        "trasferta_id": trasferta.id
    }
