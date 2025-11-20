from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional, List
from app.database.models import (
    RuoloEnum,
    StatoTrasfertaEnum,
    TipoMezzoEnum,
    TipoScontrinoEnum,   # <--- nuovo ENUM importato
)

# ============================
# DIPENDENTE
# ============================
class DipendenteBase(BaseModel):
    nome: str
    cognome: str
    email: EmailStr
    telefono: Optional[str] = None
    area_lavoro: Optional[str] = None
    ruolo: RuoloEnum = RuoloEnum.dipendente

class DipendenteCreate(DipendenteBase):
    password: str

class DipendenteRead(DipendenteBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class DipendenteUpdate(BaseModel):
    nome: Optional[str] = None
    cognome: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    area_lavoro: Optional[str] = None
    ruolo: Optional[RuoloEnum] = None
    password: Optional[str] = None

# ============================
# TRASFERTA
# ============================
class TrasfertaBase(BaseModel):
    id_dipendente: int
    data_partenza: date
    data_rientro: date
    luogo_destinazione: str
    luogo_extra: Optional[str] = None
    tipo_commessa: Optional[str] = None
    stato: StatoTrasfertaEnum = StatoTrasfertaEnum.inviata
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

class TrasfertaUpdate(BaseModel):
    data_partenza: Optional[date] = None
    data_rientro: Optional[date] = None
    luogo_destinazione: Optional[str] = None
    luogo_extra: Optional[str] = None
    tipo_commessa: Optional[str] = None
    stato: Optional[StatoTrasfertaEnum] = None
    note_dipendente: Optional[str] = None
    note_segreteria: Optional[str] = None


# ============================
# SPESA - FILE MULTIPLI
# ============================
class SpesaFileBase(BaseModel):
    filename: str
    mimetype: Optional[str] = None
    data: str  # base64 del file

class SpesaFileResponse(SpesaFileBase):
    id: int

    class Config:
        orm_mode = True


# ============================
# SPESA
# ============================
class SpesaBase(BaseModel):
    id_trasferta: int
    categoria: str
    importo: float
    valuta: str = "EUR"
    tipo_scontrino: TipoScontrinoEnum  # <--- nuovo campo
    data_spesa: date

class SpesaCreate(SpesaBase):
    pass

class SpesaRead(SpesaBase):
    id: int
    created_at: datetime
    updated_at: datetime
    files: List[SpesaFileResponse] = []  # <--- allegati multipli

    class Config:
        orm_mode = True

class SpesaUpdate(BaseModel):
    categoria: Optional[str] = None
    importo: Optional[float] = None
    valuta: Optional[str] = None
    tipo_scontrino: Optional[TipoScontrinoEnum] = None
    data_spesa: Optional[date] = None


# ============================
# PRENOTAZIONE
# ============================
class PrenotazioneBase(BaseModel):
    id_trasferta: int
    tipo_mezzo: TipoMezzoEnum
    fornitore: Optional[str] = None
    costo: Optional[float] = None
    dettagli: Optional[str] = None
    file_biglietto: Optional[str] = None

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


# ============================
# ADMIN SCHEMAS
# ============================
class PasswordResetRequest(BaseModel):
    new_password: str

class RoleUpdateRequest(BaseModel):
    ruolo: RuoloEnum
