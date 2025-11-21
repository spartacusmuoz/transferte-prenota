from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, transfers, expenses, bookings, admin
from app.database.session import create_tables

app = FastAPI(
    title="Applicazione Trasferte",
    description="API per gestione dipendenti, trasferte, spese e prenotazioni",
    version="1.0"
)

origins = [
    "http://localhost:9000",
    "http://127.0.0.1:9000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(transfers.router)
app.include_router(expenses.router)
app.include_router(bookings.router)
app.include_router(admin.router)

# ======================================
# CREAZIONE TABELLE AUTOMATICA ALL'AVVIO
# ======================================
@app.on_event("startup")
def on_startup():
    create_tables()

@app.get("/")
def read_root():
    return {"message": "API Trasferte attiva!"}
