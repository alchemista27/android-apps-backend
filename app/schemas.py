from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None
    role: str   # ✅ ditambahkan supaya tidak KeyError di test

    class Config:
        from_attributes = True  # ganti orm_mode

# ------------------- Project -------------------
class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    owner_id: int

    class Config:
        orm_mode = True

# ------------------- Material -------------------
class MaterialCreate(BaseModel):
    project_id: int
    title: str
    content: Optional[str]

class MaterialResponse(MaterialCreate):
    id: int
    created_at: datetime   # ✅ perbaikan: sebelumnya str → datetime

    class Config:
        orm_mode = True

# ------------------- Project Assignment -------------------
class ProjectAssign(BaseModel):
    project_id: int
    user_id: int

class ProjectAssignResponse(ProjectAssign):
    id: int
    assigned_at: datetime   # ✅ sudah benar

    class Config:
        orm_mode = True