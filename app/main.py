print(">>> LOADED: suggerimenti_hotel router")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, transfers, expenses, bookings, admin, cities, hotels
from app.routers import hotel_suggeriti, xotelo  # <-- import router Xotelo
from app.database.session import create_tables
from app.routers import hotel_api_params

app = FastAPI(
    title="Applicazione Trasferte",
    description="API per gestione dipendenti, trasferte, spese e prenotazioni",
    version="1.0"
)

# -------------------- CORS --------------------
origins = [
    "http://localhost:9000",
    "http://127.0.0.1:9000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- Routers --------------------
app.include_router(auth.router)
app.include_router(transfers.router)
app.include_router(expenses.router)
app.include_router(bookings.router)
app.include_router(admin.router)
app.include_router(cities.router)
app.include_router(hotels.router)
app.include_router(hotel_suggeriti.router)
app.include_router(xotelo.router)  # <-- aggiunto qui
app.include_router(hotel_api_params.router)
# ======================================
# CREAZIONE TABELLE AUTOMATICA ALL'AVVIO
# ======================================
@app.on_event("startup")
def on_startup():
    create_tables()

# -------------------- Root test --------------------
@app.get("/")
def read_root():
    return {"message": "API Trasferte attiva!"}
