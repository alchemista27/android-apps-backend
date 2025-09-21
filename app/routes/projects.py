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

# --- Create Project (Admin/Dosen only) ---
@router.post("/", response_model=schemas.ProjectResponse)
def create_project(project: schemas.ProjectCreate,
                   current_user: models.User = Depends(auth.require_roles("admin", "dosen")),
                   db: Session = Depends(get_db)):
    new_project = models.Project(
        title=project.title,
        description=project.description,
        owner_id=current_user.id
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

# --- Update Project (Admin/Dosen only) ---
@router.put("/{project_id}", response_model=schemas.ProjectResponse)
def update_project(project_id: int, project: schemas.ProjectCreate,
                   current_user: models.User = Depends(auth.require_roles("admin", "dosen")),
                   db: Session = Depends(get_db)):
    existing_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not existing_project:
        raise HTTPException(status_code=404, detail="Project not found")
    existing_project.title = project.title
    existing_project.description = project.description
    db.commit()
    db.refresh(existing_project)
    return existing_project

# --- Delete Project (Admin/Dosen only) ---
@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int,
                   current_user: models.User = Depends(auth.require_roles("admin", "dosen")),
                   db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return

# --- List Projects (All users, role-based + pagination + optional filtering) ---
@router.get("/", response_model=List[schemas.ProjectResponse])
def list_projects(skip: int = 0, limit: int = Query(default=10, lte=50),
                  owner_id: Optional[int] = None,
                  current_user: models.User = Depends(auth.get_current_user),
                  db: Session = Depends(get_db)):
    query = db.query(models.Project)
    
    # Filter by owner if param diberikan
    if owner_id:
        query = query.filter(models.Project.owner_id == owner_id)
    
    if current_user.role == "mahasiswa":
        assignments = db.query(models.ProjectAssignment).filter(
            models.ProjectAssignment.user_id == current_user.id
        ).all()
        project_ids = [a.project_id for a in assignments]
        query = query.filter(models.Project.id.in_(project_ids))
    
    projects = query.offset(skip).limit(limit).all()
    return projects

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

    existing = db.query(models.ProjectAssignment).filter_by(
        user_id=assign.user_id,
        project_id=assign.project_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Project already assigned to this student")

    assignment = models.ProjectAssignment(
        user_id=assign.user_id,
        project_id=assign.project_id
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment