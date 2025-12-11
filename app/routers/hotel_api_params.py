from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import HotelApiParams, HotelSuggerito
from app.database.schemas import (
    HotelApiParamsCreate,
    HotelApiParamsRead,
    HotelApiParamsUpdate
)
import requests
from datetime import datetime
from sqlalchemy import text


router = APIRouter(
    prefix="/hotel-api-params",
    tags=["Hotel API Params"]
)


from sqlalchemy.exc import SQLAlchemyError
# ============================================================
# 1️⃣ GET: LISTA CON NOMI (DEVE ESSERE PRIMA DI TUTTE!)
# ============================================================

@router.get("/list-with-names")
def list_with_names(db: Session = Depends(get_db)):

    # Query con join tra hotel_api_params e hotel_suggeriti
    rows = (
        db.query(
            HotelApiParams.id_hotel,
            HotelSuggerito.nome.label("hotel_nome"),
            HotelApiParams.hotel_key,
            HotelApiParams.chk_in,
            HotelApiParams.chk_out,
            HotelApiParams.rooms,
            HotelApiParams.adults,
            HotelApiParams.currency,
            HotelApiParams.id.label("param_id"),
            HotelApiParams.created_at
        )
        .join(HotelSuggerito, HotelApiParams.id_hotel == HotelSuggerito.id, isouter=True)
        .order_by(HotelSuggerito.nome)
        .all()
    )

    # Convertiamo i risultati in lista di dizionari
    result = []
    for r in rows:
        result.append({
            "id_hotel": r.id_hotel,
            "hotel_nome": r.hotel_nome,
            "hotel_key": r.hotel_key,
            "chk_in": r.chk_in,
            "chk_out": r.chk_out,
            "rooms": r.rooms,
            "adults": r.adults,
            "currency": r.currency,
            "param_id": r.param_id,
            "created_at": r.created_at
        })

    return result
   
# ============================================================
# POST: CREA PARAMETRI PER HOTEL
# ============================================================
@router.post("/", response_model=HotelApiParamsRead)
def create_hotel_api_params(params: HotelApiParamsCreate, db: Session = Depends(get_db)):

    # verifica che l'hotel esista
    hotel = db.query(HotelSuggerito).filter(HotelSuggerito.id == params.id_hotel).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel non trovato")

    new_params = HotelApiParams(
        id_hotel=params.id_hotel,
        hotel_key=params.hotel_key,
        chk_in=params.chk_in,
        chk_out=params.chk_out,
        rooms=params.rooms,
        adults=params.adults,
        currency=params.currency,
        alloggio=params.alloggio,
        exists_in_db=params.exists_in_db
    )

    try:
        db.add(new_params)
        db.commit()
        db.refresh(new_params)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore DB: {e}")

    return new_params


# ============================================================
# GET: OTTIENI PARAMETRI PER ID RECORD
# ============================================================
@router.get("/{id}", response_model=HotelApiParamsRead)
def get_params_by_id(id: int, db: Session = Depends(get_db)):

    params = db.query(HotelApiParams).filter(HotelApiParams.id == id).first()
    if not params:
        raise HTTPException(status_code=404, detail="Parametri non trovati")

    return params


# ============================================================
# GET: OTTIENI TUTTI I PARAMETRI DI UN HOTEL
# ============================================================
@router.get("/hotel/{id_hotel}", response_model=list[HotelApiParamsRead])
def get_params_by_hotel(id_hotel: int, db: Session = Depends(get_db)):

    params = db.query(HotelApiParams).filter(HotelApiParams.id_hotel == id_hotel).all()
    return params

print(">>> FILE hotel_api_params.py CARICATO")



# ============================================================
# GET: OTTIENI PARAMETRI PER NOME HOTEL
# ============================================================
@router.get("/by-name/{hotel_name}", response_model=HotelApiParamsRead)
def get_params_by_name(hotel_name: str, db: Session = Depends(get_db)):
    """
    Restituisce i parametri API di un hotel cercandolo tramite il nome.
    """
    params = (
        db.query(HotelApiParams)
        .join(HotelSuggerito)
        .filter(HotelSuggerito.nome.ilike(hotel_name))  # ricerca case-insensitive
        .first()
    )
    if not params:
        raise HTTPException(status_code=404, detail="Parametri hotel non trovati")
    return params


# ============================================================
# GET: CHIAMATA DIRETTA A XOTELO USANDO PARAMETRI SALVATI
# ============================================================
@router.get("/xotelo/{hotel_id}", response_model=dict)
def call_xotelo_rates(hotel_id: int, db: Session = Depends(get_db)):
    params = db.query(HotelApiParams).filter(HotelApiParams.id_hotel == hotel_id).first()
    if not params:
        raise HTTPException(status_code=404, detail="Parametri hotel non trovati")
    ...


    # CHIAMATA ALLA TUA API LOCALE XOTELO
    url = "http://127.0.0.1:8000/xotelo/rates"
    query = {
        "hotel_key": params.hotel_key,
        "chk_in": params.chk_in,
        "chk_out": params.chk_out,
        "rooms": params.rooms,
        "adults": params.adults,
        "currency": params.currency
    }

    try:
        response = requests.get(url, params=query)
        return response.json()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore chiamando Xotelo: {e}")


@router.patch("/{hotel_id}", response_model=dict)
def update_hotel_api_params(
    hotel_id: int,
    params_update: HotelApiParamsUpdate,
    db: Session = Depends(get_db)
):

    db_params = db.query(HotelApiParams).filter(HotelApiParams.id_hotel == hotel_id).first()

    if not db_params:
        raise HTTPException(status_code=404, detail="Parametri hotel non trovati")

    update_data = params_update.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_params, key, value)

    db.commit()
    db.refresh(db_params)

    return {
        "message": "Parametri aggiornati",
        "data": HotelApiParamsRead.model_validate(db_params)
    }






@router.post("/sync-from-existing-api-simple")
def sync_from_existing_api_simple(trasferta_id: int, db: Session = Depends(get_db)):
    """
    Sincronizza HotelApiParams usando direttamente gli hotel che hanno già hotel_key.
    """
    # 1️⃣ Prendo tutti gli hotel della trasferta che hanno hotel_key
    hotels = db.query(HotelSuggerito).filter(
        HotelSuggerito.id_trasferta == trasferta_id,
        HotelSuggerito.hotel_key != None  # solo quelli che hanno hotel_key
    ).all()

    if not hotels:
        raise HTTPException(status_code=404, detail="Nessun hotel trovato con hotel_key")

    results = []

    # 2️⃣ Per ogni hotel creo HotelApiParams usando direttamente il modello
    for hotel in hotels:
        payload = HotelApiParamsCreate(
            id_hotel=hotel.id,
            hotel_key=hotel.hotel_key,
            chk_in="2025-12-10",   # default se vuoi
            chk_out="2025-12-12",
            rooms=1,
            adults=1,
            currency="USD"
        )

        # Controllo se già esiste per evitare duplicati
        existing = db.query(HotelApiParams).filter(HotelApiParams.id_hotel == hotel.id).first()
        if existing:
            results.append({
                "hotel": hotel.nome,
                "status": "ESISTENTE",
                "param_id": existing.id
            })
            continue

        # Creo nuovo record
        try:
            new_param = HotelApiParams(
                id_hotel=payload.id_hotel,
                hotel_key=payload.hotel_key,
                chk_in=payload.chk_in,
                chk_out=payload.chk_out,
                rooms=payload.rooms,
                adults=payload.adults,
                currency=payload.currency
            )
            db.add(new_param)
            db.commit()
            db.refresh(new_param)

            results.append({
                "hotel": hotel.nome,
                "status": "CREATO",
                "param_id": new_param.id
            })

        except SQLAlchemyError as e:
            db.rollback()
            results.append({
                "hotel": hotel.nome,
                "status": f"ERRORE: {str(e)}"
            })

    return {
        "message": "Sincronizzazione completata",
        "count": len(results),
        "hotels": results
    }

@router.post("/sync-from-existing-api-simple2")
def sync_from_existing_api_simple(
    trasferta_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """
    Crea automaticamente record HotelApiParams per gli hotel della trasferta
    che hanno già un hotel_key.
    """
    hotels = db.query(HotelSuggerito).filter(
        HotelSuggerito.id_trasferta == trasferta_id,
        HotelSuggerito.hotel_key.isnot(None)  # solo quelli con hotel_key
    ).all()

    if not hotels:
        raise HTTPException(status_code=404, detail="Nessun hotel trovato con hotel_key")

    results = []

    for hotel in hotels:
        # Controllo se esiste già in HotelApiParams
        existing = db.query(HotelApiParams).filter(HotelApiParams.id_hotel == hotel.id).first()
        if existing:
            results.append({"hotel": hotel.nome, "status": "GIÀ_PRESENTE"})
            continue

        # Creazione nuovo record
        new_params = HotelApiParams(
            id_hotel=hotel.id,
            hotel_key=hotel.hotel_key,
            chk_in="2025-12-20",  # valore di default o personalizzabile
            chk_out="2025-12-25",
            rooms=1,
            adults=1,
            currency="USD"
        )

        try:
            db.add(new_params)
            db.commit()
            db.refresh(new_params)
            results.append({"hotel": hotel.nome, "status": "CREATO", "param_id": new_params.id})
        except SQLAlchemyError as e:
            db.rollback()
            results.append({"hotel": hotel.nome, "status": f"ERRORE: {str(e)}"})

    return {"message": "Sincronizzazione completata", "count": len(results), "hotels": results}