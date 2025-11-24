from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .base import Base

# URL del database
DATABASE_URL = "sqlite:///./db.sqlite3"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # solo SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ======================================
# CREA TUTTE LE TABELLE ALL'AVVIO
# ======================================
def create_tables():
    import app.database.models
    Base.metadata.create_all(bind=engine)

# ======================================
# FUNZIONE get_db (IMPORTANTE ⚠️)
# ======================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
