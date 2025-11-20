from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Enum, ForeignKey
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


class TipoScontrinoEnum(str, enum.Enum):
    aereo = "aereo"
    treno = "treno"
    taxi = "taxi"
    hotel = "hotel"
    ristorante = "ristorante"
    altro = "altro"

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

class Spesa(Base):
    __tablename__ = "spese"

    id = Column(Integer, primary_key=True, index=True)
    id_trasferta = Column(Integer, ForeignKey("trasferte.id"))
    categoria = Column(String, nullable=False)
    importo = Column(Float, nullable=False)
    valuta = Column(String, default="EUR")
    tipo_scontrino = Column(Enum(TipoScontrinoEnum), nullable=False)
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
    data = Column(String, nullable=False)  # base64 per compatibilità SQLite

    created_at = Column(DateTime, default=datetime.utcnow)

    spesa = relationship("Spesa", back_populates="files")


class Prenotazione(Base):
    __tablename__ = "prenotazioni"

    id = Column(Integer, primary_key=True, index=True)
    id_trasferta = Column(Integer, ForeignKey("trasferte.id"))
    tipo_mezzo = Column(Enum(TipoMezzoEnum), nullable=False)
    fornitore = Column(String, nullable=True)
    costo = Column(Float, nullable=True)
    dettagli = Column(String, nullable=True)
    file_biglietto = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    trasferta = relationship("Trasferta", back_populates="prenotazioni")
