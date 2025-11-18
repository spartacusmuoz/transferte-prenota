from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.database import models, schemas, session
from pydantic import BaseModel

# =========================
# CONFIG
# =========================
SECRET_KEY = "questa_dovrai_cambiarla_con_un_valore_super_segreto"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(prefix="/auth", tags=["auth"])

# Dipendenza DB
def get_db():
    db = session.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# UTILITY
# =========================
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    # Aggiungiamo il ruolo al token
    if "role" not in to_encode and "sub" in to_encode:
        db = next(get_db())  # otteniamo sessione db
        user = db.query(models.Dipendente).filter(models.Dipendente.id == int(to_encode["sub"])).first()
        if user:
            to_encode.update({"role": user.ruolo.value})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# =========================
# LOGIN/REGISTRAZIONE
# =========================
class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/register", response_model=schemas.DipendenteRead)
def register(dipendente: schemas.DipendenteCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.Dipendente).filter(models.Dipendente.email == dipendente.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email già registrata")

    hashed_password = get_password_hash(dipendente.password)

    new_user = models.Dipendente(
        nome=dipendente.nome,
        cognome=dipendente.cognome,
        email=dipendente.email,
        telefono=dipendente.telefono,
        area_lavoro=dipendente.area_lavoro,
        ruolo=dipendente.ruolo,
        password=hashed_password   # <-- QUI LA CORREZIONE
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=TokenResponse)
def login(form_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.Dipendente).filter(models.Dipendente.email == form_data.email).first()

    # <-- QUI ALTRA CORREZIONE
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Email o password errati")

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
