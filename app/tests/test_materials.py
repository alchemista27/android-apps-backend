# app/tests/test_materials.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import database, models
from app.auth import create_access_token

client = TestClient(app)

# ===== Fixture setup/teardown DB =====
@pytest.fixture(autouse=True)
def setup_db():
    db = database.SessionLocal()
    db.query(models.Material).delete()
    db.query(models.ProjectAssignment).delete()
    db.query(models.Project).delete()
    db.query(models.User).delete()
    db.commit()
    db.close()
    yield
    db = database.SessionLocal()
    db.query(models.Material).delete()
    db.query(models.ProjectAssignment).delete()
    db.query(models.Project).delete()
    db.query(models.User).delete()
    db.commit()
    db.close()

# ===== Helper buat user/project/material =====
def create_user_helper(email, role="admin"):
    db = database.SessionLocal()
    user = models.User(
        email=email,
        full_name="Test User",
        hashed_password="fakehash",
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    token = create_access_token({"sub": email})
    return {"Authorization": f"Bearer {token}"}, user

def create_project_helper(owner_id):
    db = database.SessionLocal()
    project = models.Project(title="Test Proj", description="Desc", owner_id=owner_id)
    db.add(project)
    db.commit()
    db.refresh(project)
    db.close()
    return project

def create_material_helper(project_id):
    db = database.SessionLocal()
    material = models.Material(title="Materi 1", content="Isi", project_id=project_id)
    db.add(material)
    db.commit()
    db.refresh(material)
    db.close()
    return material

# ===== Tests =====
def test_create_material_admin():
    headers, user = create_user_helper("admin@example.com", role="admin")
    project = create_project_helper(user.id)
    response = client.post(
        "/materials/",
        json={"title": "Materi 1", "content": "Isi materi", "project_id": project.id},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Materi 1"

def test_create_material_forbidden_mahasiswa():
    headers, user = create_user_helper("stud@example.com", role="mahasiswa")
    project = create_project_helper(user.id)
    response = client.post(
        "/materials/",
        json={"title": "Materi Mahasiswa", "content": "Isi", "project_id": project.id},
        headers=headers
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden"

def test_update_material():
    headers, user = create_user_helper("dosen@example.com", role="dosen")
    project = create_project_helper(user.id)
    material = create_material_helper(project.id)
    response = client.put(
        f"/materials/{material.id}",
        json={"title": "Updated Materi", "content": "Updated Content", "project_id": project.id},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Materi"

def test_delete_material():
    headers, user = create_user_helper("admin2@example.com", role="admin")
    project = create_project_helper(user.id)
    material = create_material_helper(project.id)
    response = client.delete(f"/materials/{material.id}", headers=headers)
    assert response.status_code == 204

    db = database.SessionLocal()
    deleted = db.query(models.Material).filter_by(id=material.id).first()
    db.close()
    assert deleted is None