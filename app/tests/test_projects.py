# app/tests/test_projects.py
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
    db.query(models.ProjectAssignment).delete()
    db.query(models.Project).delete()
    db.query(models.User).delete()
    db.commit()
    db.close()
    yield
    db = database.SessionLocal()
    db.query(models.ProjectAssignment).delete()
    db.query(models.Project).delete()
    db.query(models.User).delete()
    db.commit()
    db.close()

# ===== Helper buat user/project =====
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

# ===== Tests =====
def test_create_project_admin():
    headers, _ = create_user_helper("admin@example.com", role="admin")
    response = client.post(
        "/projects/",
        json={"title": "Project A", "description": "Desc A"},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Project A"

def test_create_project_forbidden_mahasiswa():
    headers, _ = create_user_helper("student@example.com", role="mahasiswa")
    response = client.post(
        "/projects/",
        json={"title": "Project B", "description": "Desc B"},
        headers=headers
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden"

def test_update_project():
    headers, user = create_user_helper("dosen@example.com", role="dosen")
    project = create_project_helper(user.id)
    response = client.put(
        f"/projects/{project.id}",
        json={"title": "Updated Title", "description": "Updated Desc"},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"

def test_delete_project():
    headers, user = create_user_helper("admin2@example.com", role="admin")
    project = create_project_helper(user.id)
    response = client.delete(f"/projects/{project.id}", headers=headers)
    assert response.status_code == 204

    db = database.SessionLocal()
    deleted = db.query(models.Project).filter_by(id=project.id).first()
    db.close()
    assert deleted is None

# --- Test Assign Project ---
def test_assign_project_success():
    headers, admin = create_user_helper("adminassign@example.com", role="admin")
    _, mahasiswa = create_user_helper("studentassign@example.com", role="mahasiswa")
    project = create_project_helper(admin.id)
    response = client.post(
        "/projects/assign",
        json={"user_id": mahasiswa.id, "project_id": project.id},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == mahasiswa.id
    assert data["project_id"] == project.id

def test_assign_project_duplicate():
    headers, admin = create_user_helper("admindup@example.com", role="admin")
    _, mahasiswa = create_user_helper("studentdup@example.com", role="mahasiswa")
    project = create_project_helper(admin.id)

    # assign pertama
    client.post(
        "/projects/assign",
        json={"user_id": mahasiswa.id, "project_id": project.id},
        headers=headers
    )
    # assign kedua harus gagal
    response = client.post(
        "/projects/assign",
        json={"user_id": mahasiswa.id, "project_id": project.id},
        headers=headers
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Project already assigned to this student"

def test_assign_project_not_found():
    headers, admin = create_user_helper("adminnf@example.com", role="admin")
    _, mahasiswa = create_user_helper("studentnf@example.com", role="mahasiswa")
    response = client.post(
        "/projects/assign",
        json={"user_id": mahasiswa.id, "project_id": 999},
        headers=headers
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User or Project not found"

def test_assign_project_forbidden_mahasiswa():
    headers, mahasiswa = create_user_helper("mahasiswaassign@example.com", role="mahasiswa")
    _, target = create_user_helper("studenttarget@example.com", role="mahasiswa")
    project = create_project_helper(mahasiswa.id)
    response = client.post(
        "/projects/assign",
        json={"user_id": target.id, "project_id": project.id},
        headers=headers
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden"