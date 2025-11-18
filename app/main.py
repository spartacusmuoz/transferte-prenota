from fastapi import FastAPI
from app.routers import auth, transfers, expenses, bookings, admin
from app.database.session import create_tables

# =========================
# CREA TABELLE AL PRIMO AVVIO
# =========================
create_tables()

# =========================
# ISTANZA APP
# =========================
app = FastAPI(
    title="Applicazione Trasferte",
    description="API per gestione dipendenti, trasferte, spese e prenotazioni",
    version="1.0"
)

# =========================
# INCLUDI ROUTER
# =========================
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(transfers.router, prefix="/trasferte", tags=["trasferte"])
app.include_router(expenses.router, prefix="/spese", tags=["spese"])
app.include_router(bookings.router, prefix="/prenotazioni", tags=["prenotazioni"])
app.include_router(admin.router)
# =========================
# ROUTA DI TEST
# =========================
@app.get("/")
def read_root():
    return {"message": "API Trasferte attiva!"}
