from fastapi import FastAPI
from app import models, database

# Inisialisasi database
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="PJBLMS Backend")

@app.get("/")
def read_root():
    return {"message": "Welcome to PJBLMS Backend API 🚀"}