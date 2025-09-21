from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None

    class Config:
        from_attributes = True  # ganti orm_mode

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

class MaterialCreate(BaseModel):
    project_id: int
    title: str
    content: Optional[str]

class MaterialResponse(MaterialCreate):
    id: int
    created_at: str

    class Config:
        orm_mode = True

class ProjectAssign(BaseModel):
    project_id: int
    user_id: int

class ProjectAssignResponse(ProjectAssign):
    id: int
    assigned_at: str

    class Config:
        orm_mode = True

class ProjectCreate(BaseModel):
    title: str
    description: Optional[str]

class ProjectResponse(ProjectCreate):
    id: int
    created_at: str

    class Config:
        orm_mode = True
