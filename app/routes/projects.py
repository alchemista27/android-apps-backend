from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, database, auth
from typing import List

router = APIRouter(prefix="/projects", tags=["Projects"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.ProjectResponse)
def create_project(project: schemas.ProjectCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    new_project = models.Project(
        title=project.title,
        description=project.description,
        owner_id=current_user.id
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

@router.get("/", response_model=List[schemas.ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    return db.query(models.Project).all()

# --- Create Material (Admin/Dosen only) ---
@router.post("/materials", response_model=schemas.MaterialResponse)
def create_material(material: schemas.MaterialCreate,
                    current_user: models.User = Depends(auth.require_roles("admin", "dosen")),
                    db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == material.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    new_material = models.Material(
        project_id=material.project_id,
        title=material.title,
        content=material.content
    )
    db.add(new_material)
    db.commit()
    db.refresh(new_material)
    return new_material

# --- Assign Project to Mahasiswa (Admin/Dosen only) ---
@router.post("/assign", response_model=schemas.ProjectAssignResponse)
def assign_project(assign: schemas.ProjectAssign,
                   current_user: models.User = Depends(auth.require_roles("admin", "dosen")),
                   db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == assign.user_id).first()
    project = db.query(models.Project).filter(models.Project.id == assign.project_id).first()
    if not user or not project:
        raise HTTPException(status_code=404, detail="User or Project not found")

    assignment = models.ProjectAssignment(
        user_id=assign.user_id,
        project_id=assign.project_id
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment