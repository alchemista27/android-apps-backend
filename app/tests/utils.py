# app/tests/utils.py
from app import models, auth

def create_user(db, email: str, password: str, role: str):
    hashed = auth.get_password_hash(password)
    user = models.User(email=email, hashed_password=hashed, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
