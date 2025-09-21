from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, schemas, database, auth

router = APIRouter(prefix="/materials", tags=["Materials"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Create Material (Admin/Dosen only) ---
@router.post("/", response_model=schemas.MaterialResponse)
def create_material(material: schemas.MaterialCreate,
                    current_user: models.User = Depends(auth.require_roles("admin", "dosen")),
                    db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == material.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    new_material = models.Material(
        title=material.title,
        content=material.content,
        project_id=material.project_id
    )
    db.add(new_material)
    db.commit()
    db.refresh(new_material)
    return new_material

# --- Update Material (Admin/Dosen only) ---
@router.put("/{material_id}", response_model=schemas.MaterialResponse)
def update_material(material_id: int, material: schemas.MaterialCreate,
                    current_user: models.User = Depends(auth.require_roles("admin", "dosen")),
                    db: Session = Depends(get_db)):
    existing = db.query(models.Material).filter(models.Material.id == material_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Material not found")

    # pastikan project_id valid
    project = db.query(models.Project).filter(models.Project.id == material.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    existing.title = material.title
    existing.content = material.content
    existing.project_id = material.project_id

    db.commit()
    db.refresh(existing)
    return existing

# --- Delete Material (Admin/Dosen only) ---
@router.delete("/{material_id}", status_code=204)
def delete_material(material_id: int,
                    current_user: models.User = Depends(auth.require_roles("admin", "dosen")),
                    db: Session = Depends(get_db)):
    material = db.query(models.Material).filter(models.Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    db.delete(material)
    db.commit()
    return

# --- List Materials (All roles, pagination + role-based filtering) ---
@router.get("/", response_model=List[schemas.MaterialResponse])
def list_materials(skip: int = 0, limit: int = Query(default=10, lte=50),
                   project_id: Optional[int] = None,
                   current_user: models.User = Depends(auth.get_current_user),
                   db: Session = Depends(get_db)):
    query = db.query(models.Material)
    
    # Filter by project if diberikan
    if project_id:
        query = query.filter(models.Material.project_id == project_id)
    
    # Mahasiswa hanya lihat materi project yang diassign
    if current_user.role == "mahasiswa":
        assignments = db.query(models.ProjectAssignment).filter(
            models.ProjectAssignment.user_id == current_user.id
        ).all()
        project_ids = [a.project_id for a in assignments]
        query = query.filter(models.Material.project_id.in_(project_ids))
    
    materials = query.offset(skip).limit(limit).all()
    return materials