from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, func, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(String, default="mahasiswa")  # admin/dosen/mahasiswa
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # relationship ke projects yang dimiliki
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    assignments = relationship("ProjectAssignment", back_populates="user", cascade="all, delete-orphan")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"))  # siapa yang buat project

    # relasi ke User
    owner = relationship("User", back_populates="projects")

    # relasi ke Material
    materials = relationship("Material", back_populates="project", cascade="all, delete-orphan")

    # relasi ke Assignment
    assignments = relationship("ProjectAssignment", back_populates="project", cascade="all, delete-orphan")

class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    title = Column(String, nullable=False)
    content = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="materials")


class ProjectAssignment(Base):
    __tablename__ = "project_assignments"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="assignments")
    user = relationship("User")
