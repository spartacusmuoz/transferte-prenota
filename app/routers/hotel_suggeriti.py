from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.dependencies import get_db
from app.database.models import Trasferta, HotelSuggerito, Prenotazione
from app.services.hotel_import_service import import_hotels_osm

router = APIRouter(prefix="/suggerimenti-hotel", tags=["Hotel Suggeriti"])


# -------------------------------
# MODELLO PER DATI IN ENTRATA DAL FRONTEND
# -------------------------------
class HotelSelectionPayload(BaseModel):
    nome: Optional[str] = None
    indirizzo: Optional[str] = None
    address: Optional[str] = None
    stars: Optional[int] = None
    providers: Optional[str] = None


# ================================
# 2️⃣ GENERA HOTEL SUGGERITI SOLO SE NON ESISTONO
# ================================
@router.post("/genera-suggeriti/{id_trasferta}")
def genera_suggeriti(id_trasferta: int, db: Session = Depends(get_db)):
    # Verifica che la trasferta esista
    trasferta = db.query(Trasferta).filter(Trasferta.id == id_trasferta).first()
    if not trasferta:
        raise HTTPException(status_code=404, detail="Trasferta non trovata")

    city = trasferta.luogo_destinazione
    if not city:
        raise HTTPException(status_code=400, detail="Trasferta senza città di destinazione")

    # 🔍 1️⃣ CONTROLLO SE ESISTONO GIÀ HOTEL SUGGERITI
    existing = db.query(HotelSuggerito).filter(
        HotelSuggerito.id_trasferta == id_trasferta
    ).first()

    if existing:
        return {
            "message": "Gli hotel suggeriti esistono già. Nessuna rigenerazione fatta.",
            "status": "skipped"
        }

    # 🔄 2️⃣ GENERAZIONE HOTEL OSM
    hotels_raw = import_hotels_osm(city)
    if hotels_raw is None:
        raise HTTPException(status_code=500, detail="Errore nella ricerca hotel OSM")
    if not hotels_raw:
        raise HTTPException(status_code=404, detail="Nessun hotel trovato per la città selezionata")

    hotels_to_add = []
    results = []

    for h in hotels_raw:
        hotel = HotelSuggerito(
            id_trasferta=id_trasferta,
            nome=h["name"],
            lat=h["lat"],
            lon=h["lon"],
            indirizzo=None,
            citta=city,
            hotel_key=h.get("hotel_key")
        )

        hotels_to_add.append(hotel)
        results.append({
            "nome": h["name"],
            "lat": h["lat"],
            "lon": h["lon"],
            "indirizzo": None,
            "hotel_key": h.get("hotel_key")
        })

    db.bulk_save_objects(hotels_to_add)
    db.commit()

    return {
        "message": f"{len(results)} hotel suggeriti generati per {city}",
        "status": "created",
        "results": results
    }


# -------------------------------
# LISTA HOTEL SUGGERITI
# -------------------------------
@router.get("/lista/{id_trasferta}")
def lista_hotels(id_trasferta: int, db: Session = Depends(get_db)):
    hotels = db.query(HotelSuggerito).filter(HotelSuggerito.id_trasferta == id_trasferta).all()
    return hotels


# -------------------------------
# SELEZIONA HOTEL E CREA/AGGIORNA PRENOTAZIONE
# -------------------------------
@router.post("/seleziona/{id_trasferta}/{id_hotel}")
def seleziona_hotel(
    id_trasferta: int,
    id_hotel: int,
    payload: HotelSelectionPayload,
    prenotazione_id: int | None = None,
    db: Session = Depends(get_db)
):

    trasferta = db.query(Trasferta).filter(Trasferta.id == id_trasferta).first()
    if not trasferta:
        raise HTTPException(status_code=404, detail="Trasferta non trovata")

    hotel = db.query(HotelSuggerito).filter(
        HotelSuggerito.id == id_hotel,
        HotelSuggerito.id_trasferta == id_trasferta
    ).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel selezionato non trovato")

    if payload.indirizzo:
        hotel.indirizzo = payload.indirizzo
    elif payload.address:
        hotel.indirizzo = payload.address

    db.commit()

    # Gestione prenotazione
    if prenotazione_id:
        pren = db.query(Prenotazione).filter(Prenotazione.id == prenotazione_id).first()
        if not pren:
            raise HTTPException(status_code=404, detail="Prenotazione non trovata")
    else:
        pren = Prenotazione(id_trasferta=id_trasferta)
        db.add(pren)

    pren.tipo_alloggio = "Hotel"
    pren.nome_struttura = payload.nome or hotel.nome
    pren.indirizzo = hotel.indirizzo
    pren.citta = hotel.citta
    pren.hotel_key = hotel.hotel_key

    db.commit()
    db.refresh(pren)

    return {
        "message": "Hotel selezionato e salvato nella prenotazione",
        "hotel": {
            "id": hotel.id,
            "nome": hotel.nome,
            "indirizzo": hotel.indirizzo,
            "citta": hotel.citta,
            "hotel_key": hotel.hotel_key
        },
        "prenotazione_id": pren.id
    }

print(">>> FILE hotel_suggeriti.py CARICATO")

# -------------------------------
# NUOVA API: OTTIENI IL PRIMO ID HOTEL PER NOME + TRASFERTA
# -------------------------------
@router.get("/get-hotel-id/{id_trasferta}/{hotel_name}", response_model=int)
def get_first_hotel_id_by_name(id_trasferta: int, hotel_name: str, db: Session = Depends(get_db)):
    """
    Restituisce il PRIMO id dell'hotel trovato nella tabella hotel_suggeriti,
    filtrando per:
    - id_trasferta
    - nome hotel (case insensitive)
    """

    hotel = (
        db.query(HotelSuggerito)
        .filter(
            HotelSuggerito.id_trasferta == id_trasferta,
            HotelSuggerito.nome.ilike(hotel_name)
        )
        .order_by(HotelSuggerito.id.asc())
        .first()
    )

    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel non trovato nella trasferta")

    return hotel.id


# -------------------------------
# CANCELLA TUTTI I SUGGERIMENTI
# -------------------------------
@router.delete("/clear/{id_trasferta}")
def cancella_suggerimenti(id_trasferta: int, db: Session = Depends(get_db)):
    db.query(HotelSuggerito).filter(HotelSuggerito.id_trasferta == id_trasferta).delete()
    db.commit()
    return {"message": "Suggerimenti cancellati"}
