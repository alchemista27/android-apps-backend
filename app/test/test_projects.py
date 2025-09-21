import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import database, models
from app.auth import create_access_token

client = TestClient(app)

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

def create_user(email, role="admin"):
    db = database.SessionLocal()
    user = models.User(
        email=email,
        hashed_password="fakehash",
        full_name="Test",
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    token = create_access_token({"sub": email})
    return {"Authorization": f"Bearer {token}"}, user

def create_project(owner_id):
    db = database.SessionLocal()
    project = models.Project(title="Test Proj", description="Desc", owner_id=owner_id)
    db.add(project)
    db.commit()
    db.refresh(project)
    db.close()
    return project

def test_create_project_admin():
    headers, user = create_user("admin@example.com", role="admin")
    response = client.post(
        "/projects/",
        json={"title": "Project A", "description": "Desc A"},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Project A"

def test_create_project_forbidden_mahasiswa():
    headers, _ = create_user("student@example.com", role="mahasiswa")
    response = client.post(
        "/projects/",
        json={"title": "Project B", "description": "Desc B"},
        headers=headers,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"

def test_update_project():
    headers, user = create_user("dosen@example.com", role="dosen")
    project = create_project(owner_id=user.id)

    response = client.put(
        f"/projects/{project.id}",
        json={"title": "Updated Title", "description": "Updated Desc"},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"

def test_delete_project():
    headers, user = create_user("admin2@example.com", role="admin")
    project = create_project(owner_id=user.id)

    response = client.delete(f"/projects/{project.id}", headers=headers)
    assert response.status_code == 204

    # cek kalau sudah terhapus
    db = database.SessionLocal()
    deleted = db.query(models.Project).filter_by(id=project.id).first()
    db.close()
    assert deleted is None