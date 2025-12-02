from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.database.models import Trasferta, HotelSuggerito, Prenotazione
from app.services.hotel_import_service import import_hotels_osm

router = APIRouter(prefix="/suggerimenti-hotel", tags=["Hotel Suggeriti"])


@router.post("/genera/{id_trasferta}")
def genera_hotels(id_trasferta: int, db: Session = Depends(get_db)):
    # Recupera la trasferta
    trasferta = db.query(Trasferta).filter(Trasferta.id == id_trasferta).first()
    if not trasferta:
        raise HTTPException(status_code=404, detail="Trasferta non trovata")

    city = trasferta.luogo_destinazione
    if not city:
        raise HTTPException(status_code=400, detail="Trasferta senza città di destinazione")

    # Chiama direttamente la funzione OSM
    hotels_raw = import_hotels_osm(city)
    if hotels_raw is None:
        raise HTTPException(status_code=500, detail="Errore nella ricerca hotel OSM")
    if not hotels_raw:
        raise HTTPException(status_code=404, detail="Nessun hotel trovato per la città selezionata")

    # Cancella vecchi suggerimenti
    db.query(HotelSuggerito).filter(HotelSuggerito.id_trasferta == id_trasferta).delete()

    hotels_to_add = []
    results = []

    for h in hotels_raw:
        hotel = HotelSuggerito(
            id_trasferta=id_trasferta,
            nome=h["name"],
            lat=h["lat"],
            lon=h["lon"],
            indirizzo=None,  # da compilare su richiesta
            citta=city
        )
        hotels_to_add.append(hotel)
        results.append({
            "nome": h["name"],
            "lat": h["lat"],
            "lon": h["lon"],
            "indirizzo": None
        })

    db.bulk_save_objects(hotels_to_add)
    db.commit()

    return {
        "message": f"{len(results)} hotel suggeriti generati per {city}",
        "results": results
    }


@router.get("/lista/{id_trasferta}")
def lista_hotels(id_trasferta: int, db: Session = Depends(get_db)):
    hotels = (
        db.query(HotelSuggerito)
        .filter(HotelSuggerito.id_trasferta == id_trasferta)
        .all()
    )
    return hotels


@router.post("/seleziona/{id_trasferta}/{id_hotel}")
def seleziona_hotel(
    id_trasferta: int,
    id_hotel: int,
    prenotazione_id: int | None = None,  # opzionale
    db: Session = Depends(get_db)
):
    trasferta = db.query(Trasferta).filter(Trasferta.id == id_trasferta).first()
    if not trasferta:
        raise HTTPException(status_code=404, detail="Trasferta non trovata")

    hotel = (
        db.query(HotelSuggerito)
        .filter(
            HotelSuggerito.id == id_hotel,
            HotelSuggerito.id_trasferta == id_trasferta
        )
        .first()
    )
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel selezionato non trovato")

    # Usa prenotazione esistente se fornita, altrimenti crea nuova
    if prenotazione_id:
        pren = db.query(Prenotazione).filter(Prenotazione.id == prenotazione_id).first()
        if not pren:
            raise HTTPException(status_code=404, detail="Prenotazione non trovata")
    else:
        pren = Prenotazione(id_trasferta=id_trasferta)
        db.add(pren)

    pren.tipo_alloggio = "Hotel"
    pren.nome_struttura = hotel.nome
    pren.indirizzo = hotel.indirizzo
    pren.citta = hotel.citta

    db.commit()

    return {
        "message": "Hotel selezionato e salvato nella prenotazione",
        "hotel": {
            "id": hotel.id,
            "nome": hotel.nome,
            "indirizzo": hotel.indirizzo,
            "citta": hotel.citta
        },
        "prenotazione_id": pren.id
    }


@router.delete("/clear/{id_trasferta}")
def cancella_suggerimenti(id_trasferta: int, db: Session = Depends(get_db)):
    db.query(HotelSuggerito).filter(HotelSuggerito.id_trasferta == id_trasferta).delete()
    db.commit()
    return {"message": "Suggerimenti cancellati"}
