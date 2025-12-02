from fastapi import APIRouter, HTTPException
from app.services.hotel_import_service import import_hotels_osm

router = APIRouter(
    prefix="/hotels",
    tags=["hotels"]
)

@router.get("/{city_name}")
def get_hotels(city_name: str):
    """
    Recupera gli hotel per la città specificata usando OSM (solo JSON, senza DB)
    """
    hotels = import_hotels_osm(city_name)
    if hotels is None:
        raise HTTPException(status_code=500, detail="Errore nella ricerca degli hotel")
    if not hotels:
        raise HTTPException(status_code=404, detail="Nessun hotel trovato")
    return {"city": city_name, "hotels": hotels}
