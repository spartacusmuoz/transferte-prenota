from pydantic import BaseModel, field_validator, EmailStr
from datetime import date, datetime
from typing import Optional, List
from app.database.models import (
    RuoloEnum,
    StatoTrasfertaEnum,
    TipoMezzoEnum,
    TipoAlloggioEnum,
)

# ============================
# DIPENDENTE
# ============================
class DipendenteBase(BaseModel):
    nome: Optional[str] = None
    cognome: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    area_lavoro: Optional[str] = None
    ruolo: Optional[RuoloEnum] = None

class DipendenteCreate(DipendenteBase):
    password: Optional[str] = None

class DipendenteRead(DipendenteBase):
    id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        orm_mode = True

class DipendenteUpdate(DipendenteBase):
    password: Optional[str] = None


# ============================
# TRASFERTA
# ============================
class TrasfertaBase(BaseModel):
    id_dipendente: Optional[int] = None
    data_partenza: Optional[date] = None
    data_rientro: Optional[date] = None
    luogo_destinazione: Optional[str] = None
    luogo_extra: Optional[str] = None
    tipo_commessa: Optional[str] = None
    stato: Optional[StatoTrasfertaEnum] = None
    note_dipendente: Optional[str] = None
    note_segreteria: Optional[str] = None

class TrasfertaCreate(TrasfertaBase):
    pass

class TrasfertaRead(TrasfertaBase):
    id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        orm_mode = True

class TrasfertaUpdate(TrasfertaBase):
    pass


# ============================
# SPESA FILE
# ============================
class SpesaFileBase(BaseModel):
    filename: Optional[str] = None
    mimetype: Optional[str] = None
    data: Optional[str] = None

class SpesaFileResponse(SpesaFileBase):
    id: int
    class Config:
        orm_mode = True


# ============================
# SPESA
# ============================
class SpesaBase(BaseModel):
    id_trasferta: Optional[int] = None
    categoria: Optional[str] = None
    importo: Optional[float] = None
    valuta: Optional[str] = None
    tipo_scontrino: Optional[str] = None
    data_spesa: Optional[date] = None

class SpesaCreate(SpesaBase):
    pass

class SpesaRead(SpesaBase):
    id: int
    created_at: datetime
    updated_at: datetime
    files: List[SpesaFileResponse] = []
    class Config:
        orm_mode = True

class SpesaUpdate(SpesaBase):
    pass


# ============================
# PRENOTAZIONE
# ============================
class PrenotazioneBase(BaseModel):
    id_trasferta: int

    # Trasporto
    tipo_mezzo: Optional[TipoMezzoEnum] = None
    fornitore: Optional[str] = None
    costo: Optional[float] = None
    dettagli: Optional[str] = None
    file_biglietto: Optional[str] = None

    # Alloggio
    tipo_alloggio: Optional[TipoAlloggioEnum] = None
    nome_struttura: Optional[str] = None
    citta: Optional[str] = None
    costo_alloggio: Optional[float] = None
    indirizzo: Optional[str] = None
    valutazione: Optional[float] = None
    numero_recensioni: Optional[int] = None
    link_hotel: Optional[str] = None
    hotel_key: Optional[str] = None
    id_hotel: Optional[int]= None
    chk_in: Optional[date] = None
    chk_out: Optional[date] = None
    @field_validator("tipo_alloggio", "tipo_mezzo", mode="before")
    def empty_string_to_none(cls, v):
        if v == "":
            return None
        return v

    class Config:
        orm_mode = True


class PrenotazioneCreate(PrenotazioneBase):
    pass

class PrenotazioneRead(PrenotazioneBase):
    id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        orm_mode = True

class PrenotazioneUpdate(BaseModel):
    tipo_mezzo: Optional[TipoMezzoEnum] = None
    fornitore: Optional[str] = None
    costo: Optional[float] = None
    dettagli: Optional[str] = None
    file_biglietto: Optional[str] = None

    # Alloggio
    tipo_alloggio: Optional[TipoAlloggioEnum] = None
    nome_struttura: Optional[str] = None
    citta: Optional[str] = None
    costo_alloggio: Optional[float] = None
    indirizzo: Optional[str] = None
    valutazione: Optional[float] = None
    numero_recensioni: Optional[int] = None
    link_hotel: Optional[str] = None
    hotel_key: Optional[str] = None
    chk_in: Optional[date] = None
    chk_out: Optional[date] = None

# ============================
# ADMIN
# ============================
class PasswordResetRequest(BaseModel):
    new_password: Optional[str] = None

class RoleUpdateRequest(BaseModel):
    ruolo: Optional[RuoloEnum] = None


# ============================================================
# HOTEL API PARAMS (NUOVI SCHEMI)
# ============================================================

class HotelApiParamsBase(BaseModel):
    id_hotel: Optional[int] = None
    hotel_key: Optional[str] = None
    chk_in: Optional[str] = None
    chk_out: Optional[str] = None
    rooms: Optional[int] = 1
    adults: Optional[int] = 1
    currency: Optional[str] = "USD"

class HotelApiParamsCreate(HotelApiParamsBase):
    id_hotel: int
    hotel_key: str
    chk_in: str
    chk_out: str
    alloggio: Optional[str] = None
    exists_in_db: Optional[bool] = False


class HotelApiParamsRead(HotelApiParamsBase):
    id: int
    created_at: datetime
    alloggio: Optional[str] = None
    exists_in_db: Optional[bool] = False

    model_config = {
        "from_attributes": True
    }



class HotelApiParamsUpdate(BaseModel):
    hotel_key: Optional[str] = None
    chk_in: Optional[str] = None
    chk_out: Optional[str] = None
    rooms: Optional[int] = None
    adults: Optional[int] = None
    currency: Optional[str] = None
    alloggio: Optional[str] = None
    exists_in_db: Optional[bool] = False



class CityHotelsResponse(BaseModel):
    city_name: str
    location_key: str

    class Config:
        from_attributes = True  # per supportare SQLAlchemy ORM
