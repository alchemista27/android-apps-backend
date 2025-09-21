from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app import models, database
from app.routes import users, auth, projects, materials
from app.middleware.log_requests import LoggingMiddleware
from app.middleware.error_handler import http_exception_handler, validation_exception_handler, generic_exception_handler
from starlette.exceptions import HTTPException as HTTPException
from fastapi.exceptions import RequestValidationError

# Inisialisasi database
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="PJBLMS Backend")

# Tambahkan middleware logging
app.add_middleware(LoggingMiddleware)

# Registrasi global exception handler
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include routers
app.include_router(users.router)
app.include_router(auth.router) 
app.include_router(projects.router)
app.include_router(materials.router)

# Global exception handler untuk memastikan semua error JSON
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# fallback generic exception
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # tetap log error
    from app.logger import logger
    logger.exception(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

@app.get("/")
def read_root():
    return {"message": "Welcome to PJBLMS Backend API 🚀"}