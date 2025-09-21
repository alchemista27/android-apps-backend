from fastapi import FastAPI
from app import models, database
from app.routes import users, auth

# Inisialisasi database
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="PJBLMS Backend")

# Tambahkan middleware logging
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(users.router)
app.include_router(auth.router) 
app.include_router(projects.router)
app.include_router(materials.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to PJBLMS Backend API 🚀"}