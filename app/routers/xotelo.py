from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
import requests
import httpx
import traceback

from app.dependencies import get_db
from app.database.models import HotelSuggerito, HotelApiParams, Location

router = APIRouter(
    prefix="/xotelo",
    tags=["xotelo"]
)

BASE_XOTELO_URL = "https://data.xotelo.com/api"


# ==========================
#      Helper per Location
# ==========================
def get_location_key(db: Session, city_name: str) -> str:
    location = db.query(Location).filter(Location.city_name.ilike(city_name)).first()
    if not location:
        raise HTTPException(status_code=404, detail=f"Location key per {city_name} non trovata")
    return location.location_key


# ==========================
#         RATES
# ==========================
@router.get("/rates")
def get_xotelo_rates(
    hotel_key: str = Query(...),
    chk_in: str = Query(...),
    chk_out: str = Query(...),
    rooms: int = Query(1),
    adults: int = Query(1),
    currency: str = Query("USD")
):
    params = {
        "hotel_key": hotel_key,
        "chk_in": chk_in,
        "chk_out": chk_out,
        "rooms": rooms,
        "adults": adults,
        "currency": currency
    }
    try:
        response = requests.get(f"{BASE_XOTELO_URL}/rates", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================
#         HEATMAP
# ==========================
@router.get("/heatmap")
def get_xotelo_heatmap(
    hotel_key: str = Query(...),
    chk_out: str = Query(...)
):
    params = {"hotel_key": hotel_key, "chk_out": chk_out}
    try:
        response = requests.get(f"{BASE_XOTELO_URL}/heatmap", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================
#         LIST
# ==========================
@router.get("/list")
def get_xotelo_list(
    city: str = Query(...),
    offset: int = Query(0),
    limit: int = Query(30),
    db: Session = Depends(get_db)
):
    location_key = get_location_key(db, city)
    params = {"location_key": location_key, "offset": offset, "limit": limit}
    try:
        response = requests.get(f"{BASE_XOTELO_URL}/list", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================
#         SEARCH
# ==========================
@router.get("/search")
def search_xotelo_hotels(
    query: str = Query(...),
    location_type: str = Query("accommodation")
):
    params = {"query": query, "location_type": location_type}
    try:
        response = requests.get(f"{BASE_XOTELO_URL}/search", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================
#   LIST HOTELS PER CITTA'
# ==========================
@router.get("/city-hotels")
async def get_city_hotels(
    city: str = Query(...),
    offset: int = 0,
    limit: int = 100,
    sort: str = "best_value",
    db: Session = Depends(get_db)
):
    location_key = get_location_key(db, city)
    params = {
        "location_key": location_key,
        "offset": offset,
        "limit": min(limit, 100),
        "sort": sort
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_XOTELO_URL}/list", params=params)
            response.raise_for_status()
            data = response.json()
            if data.get("error"):
                raise HTTPException(status_code=400, detail=data["error"])
            return data.get("result", {}).get("list", [])
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


# ==========================
#   SYNC HOTELS TO DB
# ==========================
@router.post("/sync-hotels-to-db")
def sync_hotels_to_db(
    city: str = Query(...),
    trasferta_id: int = Query(...),
    db: Session = Depends(get_db)
):
    location_key = get_location_key(db, city)
    params = {
        "location_key": location_key,
        "offset": 0,
        "limit": 100,
        "sort": "best_value"
    }

    try:
        response = httpx.get(f"{BASE_XOTELO_URL}/list", params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore Xotelo: {str(e)}")

    hotel_list = data.get("result", {}).get("list", [])
    if not hotel_list:
        raise HTTPException(status_code=404, detail="Nessun hotel ricevuto da Xotelo")

    db.query(HotelSuggerito).filter(
        HotelSuggerito.id_trasferta == trasferta_id
    ).update({"esiste": False})
    db.commit()

    updated_count = 0
    for hotel in hotel_list:
        name = hotel.get("name", "").strip()
        if not name:
            continue

        hotel_suggerito = (
            db.query(HotelSuggerito)
            .filter(
                HotelSuggerito.nome.ilike(name),
                HotelSuggerito.id_trasferta == trasferta_id
            )
            .first()
        )

        if hotel_suggerito:
            hotel_suggerito.esiste = True
            updated_count += 1

    db.commit()

    return {
        "message": "Sincronizzazione completata",
        "updated_count": updated_count
    }


# ==========================
#   SYNC HOTEL KEYS TO DB
# ==========================
@router.post("/sync-hotel-keys-to-db")
def sync_hotel_keys_to_db(
    city: str = Query(...),
    trasferta_id: int = Query(...),
    db: Session = Depends(get_db)
):
    location_key = get_location_key(db, city)
    params = {"location_key": location_key, "offset": 0, "limit": 100, "sort": "best_value"}

    try:
        response = httpx.get(f"{BASE_XOTELO_URL}/list", params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore Xotelo: {str(e)}")

    hotel_list = data.get("result", {}).get("list", [])
    if not hotel_list:
        raise HTTPException(status_code=404, detail="Nessun hotel ricevuto da Xotelo")

    hotel_suggeriti = db.query(HotelSuggerito).filter(
        HotelSuggerito.id_trasferta == trasferta_id
    ).all()

    updated_count = 0
    for hotel in hotel_suggeriti:
        for xotelo_hotel in hotel_list:
            if xotelo_hotel.get("name", "").strip().lower() == hotel.nome.strip().lower():
                hotel.hotel_key = xotelo_hotel.get("key")
                hotel.esiste = 1
                updated_count += 1
                break

    if updated_count > 0:
        db.commit()

    return {
        "message": "Sincronizzazione delle chiavi completata",
        "updated_count": updated_count
    }


# ==========================
#   SYNC HOTEL KEYS TO API PARAMS
# ==========================
@router.post("/sync-hotel-keys-to-api-params")
def sync_hotel_keys_to_api_params(
    trasferta_id: int = Query(...),
    db: Session = Depends(get_db)
):
    try:
        hotel_suggeriti = db.query(HotelSuggerito).filter(
            HotelSuggerito.id_trasferta == trasferta_id
        ).all()

        if not hotel_suggeriti:
            raise HTTPException(status_code=404, detail="Nessun hotel trovato per questa trasferta")

        hotel_data = [(hotel.id, hotel.hotel_key) for hotel in hotel_suggeriti if hotel.hotel_key]

        if not hotel_data:
            raise HTTPException(status_code=404, detail="Nessun hotel con hotel_key trovato")

        updated_count = 0
        for id_hotel, hotel_key in hotel_data:
            existing_entry = db.query(HotelApiParams).filter(
                HotelApiParams.id_hotel == id_hotel
            ).first()

            if existing_entry:
                existing_entry.hotel_key = hotel_key
            else:
                new_entry = HotelApiParams(
                    id_hotel=id_hotel,
                    hotel_key=hotel_key,
                    chk_in="2025-12-12",
                    chk_out="2025-12-17",
                    rooms=1,
                    adults=1,
                    currency="USD",
                    alloggio="Hotel",
                    exists_in_db=True,
                )
                db.add(new_entry)

            updated_count += 1

        db.commit()

        return {
            "message": f"{updated_count} hotel sincronizzati nella tabella hotel_api_params.",
            "updated_count": updated_count
        }

    except Exception as e:
        error_message = f"Errore durante la sincronizzazione: {str(e)}"
        traceback_str = traceback.format_exc()
        print("Errore completo:", error_message, traceback_str)
        raise HTTPException(status_code=500, detail=f"Errore interno: {error_message}")

@router.post("/suggerimenti-hotel/genera/{trasferta_id}")
def genera_suggerimenti_hotel(trasferta_id: int, db: Session = Depends(get_db)):
    # 1️⃣ Chiamata all'API Xotelo per ottenere la lista hotel
    location_keys = db.query(Location).join(HotelSuggerito, HotelSuggerito.id_trasferta == trasferta_id)\
                     .with_entities(Location.location_key).distinct().all()

    hotel_list = []
    for lk in location_keys:
        try:
            response = requests.get(f"{BASE_XOTELO_URL}/list", params={"location_key": lk[0], "offset": 0, "limit": 100})
            response.raise_for_status()
            data = response.json()
            hotel_list.extend(data.get("result", {}).get("list", []))
        except Exception as e:
            print(f"Errore Xotelo per location_key {lk[0]}: {e}")

    if not hotel_list:
        raise HTTPException(status_code=404, detail="Nessun hotel ricevuto da Xotelo")

    # 2️⃣ Inserimento o aggiornamento hotel senza cancellare quelli già presenti
    added_count = 0
    for hotel in hotel_list:
        nome = hotel.get("name", "").strip()
        if not nome or lat is None or lon is None:
            continue

        hotel_key = hotel.get("key")
        lat = hotel.get("lat")
        lon = hotel.get("lon")
        city_name = hotel.get("city", "").strip()

        # Verifica se l'hotel esiste già per la trasferta
        existing_hotel = db.query(HotelSuggerito).filter(
            HotelSuggerito.nome.ilike(nome),
            HotelSuggerito.id_trasferta == trasferta_id
        ).first()

        if existing_hotel:
            # Aggiorna solo se vuoi modificare campi come hotel_key, lat/lon
            existing_hotel.hotel_key = hotel_key or existing_hotel.hotel_key
            existing_hotel.lat = lat or existing_hotel.lat
            existing_hotel.lon = lon or existing_hotel.lon
            existing_hotel.citta = city_name or existing_hotel.citta
        else:
            # Cerca la location nel DB
            location = db.query(Location).filter(Location.city_name.ilike(city_name)).first()

            # Inserisce nuovo hotel con location_id
            new_hotel = HotelSuggerito(
                id_trasferta=trasferta_id,
                nome=nome,
                hotel_key=hotel_key,
                lat=lat,
                lon=lon,
                citta=city_name,
                location_id=location.id if location else None,
                esiste=True  # segna come presente
            )
            db.add(new_hotel)
            added_count += 1

    db.commit()

    return {
        "message": f"Sincronizzazione completata. Nuovi hotel aggiunti: {added_count}",
        "total_hotels": len(hotel_list)
    }
