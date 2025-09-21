from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from app import schemas, models, database, auth
from app.logger import logger

# Konfigurasi router
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Constants (ambil dari auth.py supaya konsisten)
SECRET_KEY = auth.SECRET_KEY
ALGORITHM = auth.ALGORITHM

# Dependency untuk ambil DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Register ---
@router.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        logger.warning(f"Gagal register: email {user.email} sudah terdaftar")
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")

    hashed_password = auth.hash_password(user.password)
    new_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"User baru terdaftar: id={new_user.id}, email={new_user.email}")
    return new_user


# --- Login ---
@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user:
        logger.warning(f"Gagal login: email {user.email} tidak ditemukan")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not auth.verify_password(user.password, db_user.hashed_password):
        logger.warning(f"Gagal login: password salah untuk email {user.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = auth.create_access_token({"sub": db_user.email})
    logger.info(f"User login sukses: id={db_user.id}, email={db_user.email}")
    return {"access_token": token, "token_type": "bearer"}

# --- Get Current User ---
def get_current_user(token: str = Depends(oauth2_scheme)):
    db: Session = database.SessionLocal()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            logger.warning("Token tidak valid atau sub kosong")
            raise HTTPException(status_code=401, detail="Invalid token")

        user = db.query(models.User).filter(models.User.email == email).first()
        if user is None:
            logger.warning(f"Token valid tapi user tidak ditemukan: {email}")
            raise HTTPException(status_code=401, detail="User not found")

        logger.info(f"Current user token valid: id={user.id}, email={user.email}")
        return user

    except JWTError:
        logger.warning("JWT decode error: token invalid")
        raise HTTPException(status_code=401, detail="Invalid token")

    finally:
        db.close()

@router.get("/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user