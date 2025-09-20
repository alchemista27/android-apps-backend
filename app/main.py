from fastapi import FastAPI
from app import models, database
from app.routes import users

# Inisialisasi database
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="PJBLMS Backend")

app.include_router(users.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to PJBLMS Backend API 🚀"}