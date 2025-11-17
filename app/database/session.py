from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .base import Base

# URL del database (SQLite per esempio)
DATABASE_URL = "sqlite:///./db.sqlite3"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}  # necessario solo per SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    # Importa tutti i modelli per creare le tabelle
    import app.database.models
    Base.metadata.create_all(bind=engine)
