import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import database, models
from sqlalchemy.orm import Session
from app.tests.utils import create_user

# jangan lagi panggil User langsung pakai password
admin = create_user(db_session, "admin@test.com", "adminpass", "admin")


client = TestClient(app)

# --- Fixture DB session ---
@pytest.fixture()
def db_session():
    db: Session = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Helper: buat user & login ---
def create_user(db, email, password, role):
    user = models.User(email=email, password=password, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_token(email, password):
    response = client.post("/auth/login", json={"email": email, "password": password})
    return response.json()["access_token"]

# ------------------ TESTS ------------------

def test_mahasiswa_cannot_see_unassigned_projects(db_session):
    # Buat admin & mahasiswa
    admin = create_user(db_session, "admin2@test.com", "adminpass", "admin")
    mahasiswa = create_user(db_session, "mhs2@test.com", "mhs123", "mahasiswa")

    # Buat project assign ke admin saja
    project = models.Project(title="Admin Project", description="Desc", owner_id=admin.id)
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    token = get_token(mahasiswa.email, "mhs123")

    # Mahasiswa request list projects
    response = client.get("/projects/", headers={"Authorization": f"Bearer {token}"})
    projects = response.json()

    # Mahasiswa tidak boleh lihat project milik admin
    assert all(p["id"] != project.id for p in projects)


def test_mahasiswa_sees_assigned_projects(db_session):
    # Buat admin & mahasiswa
    admin = create_user(db_session, "admin3@test.com", "adminpass", "admin")
    mahasiswa = create_user(db_session, "mhs3@test.com", "mhs123", "mahasiswa")

    # Buat project assign ke mahasiswa
    project = models.Project(title="Assigned Project", description="Desc", owner_id=admin.id)
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    # Assign project ke mahasiswa
    assignment = models.ProjectAssignment(user_id=mahasiswa.id, project_id=project.id)
    db_session.add(assignment)
    db_session.commit()

    token = get_token(mahasiswa.email, "mhs123")

    response = client.get("/projects/", headers={"Authorization": f"Bearer {token}"})
    projects = response.json()

    assert any(p["id"] == project.id for p in projects)


def test_admin_sees_all_projects(db_session):
    admin = create_user(db_session, "admin4@test.com", "adminpass", "admin")
    mahasiswa = create_user(db_session, "mhs4@test.com", "mhs123", "mahasiswa")

    # Buat beberapa project
    p1 = models.Project(title="Project 1", description="Desc", owner_id=admin.id)
    p2 = models.Project(title="Project 2", description="Desc", owner_id=admin.id)
    db_session.add_all([p1, p2])
    db_session.commit()

    token = get_token(admin.email, "adminpass")
    response = client.get("/projects/", headers={"Authorization": f"Bearer {token}"})
    projects = response.json()

    assert len(projects) >= 2
    assert any(p["title"] == "Project 1" for p in projects)
    assert any(p["title"] == "Project 2" for p in projects)

# ------------------ MATERIALS ------------------

def test_mahasiswa_cannot_see_unassigned_materials(db_session):
    # Buat admin & mahasiswa
    admin = create_user(db_session, "admin_mat@test.com", "adminpass", "admin")
    mahasiswa = create_user(db_session, "mhs_mat@test.com", "mhs123", "mahasiswa")

    # Buat project & material
    project = models.Project(title="Admin Project", description="Desc", owner_id=admin.id)
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    material = models.Material(title="Admin Material", content="Content", project_id=project.id)
    db_session.add(material)
    db_session.commit()
    db_session.refresh(material)

    token = get_token(mahasiswa.email, "mhs123")
    response = client.get("/materials/", headers={"Authorization": f"Bearer {token}"})
    materials = response.json()

    # Mahasiswa tidak boleh lihat material project yang tidak di-assign
    assert all(m["id"] != material.id for m in materials)


def test_mahasiswa_sees_assigned_materials(db_session):
    # Buat admin & mahasiswa
    admin = create_user(db_session, "admin_mat2@test.com", "adminpass", "admin")
    mahasiswa = create_user(db_session, "mhs_mat2@test.com", "mhs123", "mahasiswa")

    # Buat project & material
    project = models.Project(title="Assigned Project", description="Desc", owner_id=admin.id)
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    material = models.Material(title="Assigned Material", content="Content", project_id=project.id)
    db_session.add(material)
    db_session.commit()
    db_session.refresh(material)

    # Assign project ke mahasiswa
    assignment = models.ProjectAssignment(user_id=mahasiswa.id, project_id=project.id)
    db_session.add(assignment)
    db_session.commit()

    token = get_token(mahasiswa.email, "mhs123")
    response = client.get("/materials/", headers={"Authorization": f"Bearer {token}"})
    materials = response.json()

    assert any(m["id"] == material.id for m in materials)


def test_admin_sees_all_materials(db_session):
    admin = create_user(db_session, "admin_mat3@test.com", "adminpass", "admin")
    
    # Buat beberapa project & material
    p1 = models.Project(title="Project 1", description="Desc", owner_id=admin.id)
    p2 = models.Project(title="Project 2", description="Desc", owner_id=admin.id)
    db_session.add_all([p1, p2])
    db_session.commit()

    m1 = models.Material(title="Material 1", content="Content", project_id=p1.id)
    m2 = models.Material(title="Material 2", content="Content", project_id=p2.id)
    db_session.add_all([m1, m2])
    db_session.commit()

    token = get_token(admin.email, "adminpass")
    response = client.get("/materials/", headers={"Authorization": f"Bearer {token}"})
    materials = response.json()

    assert len(materials) >= 2
    assert any(m["title"] == "Material 1" for m in materials)
    assert any(m["title"] == "Material 2" for m in materials)