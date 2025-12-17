from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Enum, ForeignKey, Boolean,func,Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base
import enum

# =============================
# ENUMS
# =============================

class RuoloEnum(str, enum.Enum):
    dipendente = "dipendente"
    manager = "manager"
    admin = "admin"

class StatoTrasfertaEnum(str, enum.Enum):
    inviata = "inviata"
    approvata = "approvata"
    rifiutata = "rifiutata"
    completata = "completata"

class TipoMezzoEnum(str, enum.Enum):
    aereo = "aereo"
    treno = "treno"
    auto = "auto"
    altro = "altro"

class TipoAlloggioEnum(str, enum.Enum):
    hotel = "Hotel"
    bnb = "Bed & Breakfast"
    ostello = "Ostello"
    appartamento = "Appartamento"
    casa_vacanze = "Casa vacanze"
    agriturismo = "Agriturismo"
    guesthouse = "Guesthouse"
    altro = "Altro"

# =============================
# MODELS
# =============================

class Dipendente(Base):
    __tablename__ = "dipendenti"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String, nullable=False)
    cognome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    telefono = Column(String, nullable=True)
    area_lavoro = Column(String, nullable=True)
    ruolo = Column(Enum(RuoloEnum), default=RuoloEnum.dipendente)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    trasferte = relationship("Trasferta", back_populates="dipendente")


class Trasferta(Base):
    __tablename__ = "trasferte"

    id = Column(Integer, primary_key=True, index=True)
    id_dipendente = Column(Integer, ForeignKey("dipendenti.id"))
    data_partenza = Column(Date, nullable=False)
    data_rientro = Column(Date, nullable=False)
    luogo_destinazione = Column(String, nullable=False)
    luogo_extra = Column(String, nullable=True)
    tipo_commessa = Column(String, nullable=True)
    stato = Column(Enum(StatoTrasfertaEnum), default=StatoTrasfertaEnum.inviata)
    note_dipendente = Column(String, nullable=True)
    note_segreteria = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    dipendente = relationship("Dipendente", back_populates="trasferte")
    spese = relationship("Spesa", back_populates="trasferta")
    prenotazioni = relationship("Prenotazione", back_populates="trasferta")

    hotels_suggeriti = relationship(
        "HotelSuggerito",
        back_populates="trasferta",
        cascade="all, delete"
    )


class Spesa(Base):
    __tablename__ = "spese"

    id = Column(Integer, primary_key=True, index=True)
    id_trasferta = Column(Integer, ForeignKey("trasferte.id"))
    categoria = Column(String, nullable=False)
    importo = Column(Float, nullable=False)
    valuta = Column(String, default="EUR")
    tipo_scontrino = Column(String, default="altro", nullable=False)
    file_scontrino = Column(String, nullable=True)
    data_spesa = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    trasferta = relationship("Trasferta", back_populates="spese")
    files = relationship("SpesaFile", back_populates="spesa")


class SpesaFile(Base):
    __tablename__ = "spesa_files"

    id = Column(Integer, primary_key=True, index=True)
    id_spesa = Column(Integer, ForeignKey("spese.id"), nullable=False)

    filename = Column(String, nullable=False)
    mimetype = Column(String, nullable=True)
    data = Column(String, nullable=False)  # base64

    created_at = Column(DateTime, default=datetime.utcnow)

    spesa = relationship("Spesa", back_populates="files")


class Prenotazione(Base):
    __tablename__ = "prenotazioni"

    id = Column(Integer, primary_key=True, index=True)
    id_trasferta = Column(Integer, ForeignKey("trasferte.id"), nullable=False)

    # Trasporto
    tipo_mezzo = Column(Enum(TipoMezzoEnum), nullable=True)
    fornitore = Column(String, nullable=True)
    costo = Column(Float, nullable=True)
    dettagli = Column(String, nullable=True)
    file_biglietto = Column(String, nullable=True)

    # Alloggio
    tipo_alloggio = Column(Enum(TipoAlloggioEnum), nullable=True)
    nome_struttura = Column(String, nullable=True)
    citta = Column(String, nullable=True)
    costo_alloggio = Column(Float, nullable=True)
    indirizzo = Column(String, nullable=True)
    valutazione = Column(Float, nullable=True)
    numero_recensioni = Column(Integer, nullable=True)
    link_hotel = Column(String, nullable=True)
    hotel_key = Column(String, nullable=True)
    id_hotel = Column(Integer, nullable=True)
    chk_in = Column(Date, nullable=True)
    chk_out = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    trasferta = relationship("Trasferta", back_populates="prenotazioni")


class HotelSuggerito(Base):
    __tablename__ = "hotel_suggeriti"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    id_trasferta = Column(Integer, ForeignKey("trasferte.id", ondelete="CASCADE"))
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)  # nuovo campo
    nome = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    indirizzo = Column(String, nullable=True)
    citta = Column(String, nullable=False)
    hotel_key = Column(String, nullable=True)
    esiste = Column(Boolean, default=False)
    image_url = Column(Text, nullable=True)  # 🔥 nuova colonna
    trasferta = relationship("Trasferta", back_populates="hotels_suggeriti")
    location = relationship("Location", backref="hotels_suggeriti")
    
    # relazione automatica aggiunta dal backref del nuovo modello:
    # api_params = relationship("HotelApiParams", back_populates="hotel")


# ============================================================
# NUOVO MODELLO: PARAMETRI API XOTELO
# ============================================================

class HotelApiParams(Base):
    __tablename__ = "hotel_api_params"

    id = Column(Integer, primary_key=True, index=True)

    id_hotel = Column(Integer, ForeignKey("hotel_suggeriti.id", ondelete="CASCADE"), nullable=False)
    hotel_key = Column(String, nullable=False)

    chk_in = Column(String, nullable=False)
    chk_out = Column(String, nullable=False)
    rooms = Column(Integer, default=1)
    adults = Column(Integer, default=1)
    currency = Column(String, default="USD")
    alloggio = Column(String, nullable=True)  # nuovo campo
    exists_in_db = Column(Boolean, default=False)  # nuovo campo
    created_at = Column(DateTime, default=datetime.utcnow)

    # relazione verso HotelSuggerito
    hotel = relationship("HotelSuggerito", backref="api_params")

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    city_name = Column(String(100), unique=True, nullable=False)
    location_key = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
