# app/tests/test_role_access.py
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
    db.query(models.Material).delete()
    db.query(models.Project).delete()
    db.query(models.User).delete()
    db.commit()
    db.close()
    yield
    db = database.SessionLocal()
    db.query(models.ProjectAssignment).delete()
    db.query(models.Material).delete()
    db.query(models.Project).delete()
    db.query(models.User).delete()
    db.commit()
    db.close()

# ===== Helper buat user/project/material =====
def create_user_helper(email, role="mahasiswa"):
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
    project = models.Project(title="Project Test", description="Desc", owner_id=owner_id)
    db.add(project)
    db.commit()
    db.refresh(project)
    db.close()
    return project

def create_material_helper(project_id):
    db = database.SessionLocal()
    material = models.Material(title="Material Test", content="Content", project_id=project_id)
    db.add(material)
    db.commit()
    db.refresh(material)
    db.close()
    return material

# ===== TEST PROJECT ACCESS =====
def test_mahasiswa_cannot_see_unassigned_projects():
    headers_admin, admin = create_user_helper("admin2@test.com", "admin")
    headers_mhs, mahasiswa = create_user_helper("mhs2@test.com", "mahasiswa")
    project = create_project_helper(admin.id)

    response = client.get("/projects/", headers=headers_mhs)
    projects = response.json()
    assert all(p["id"] != project.id for p in projects)

def test_mahasiswa_sees_assigned_projects():
    headers_admin, admin = create_user_helper("admin3@test.com", "admin")
    headers_mhs, mahasiswa = create_user_helper("mhs3@test.com", "mahasiswa")
    project = create_project_helper(admin.id)

    # assign project
    db = database.SessionLocal()
    assignment = models.ProjectAssignment(user_id=mahasiswa.id, project_id=project.id)
    db.add(assignment)
    db.commit()
    db.close()

    response = client.get("/projects/", headers=headers_mhs)
    projects = response.json()
    assert any(p["id"] == project.id for p in projects)

def test_admin_sees_all_projects():
    headers_admin, admin = create_user_helper("admin4@test.com", "admin")
    headers_mhs, _ = create_user_helper("mhs4@test.com", "mahasiswa")
    p1 = create_project_helper(admin.id)
    p2 = create_project_helper(admin.id)

    response = client.get("/projects/", headers=headers_admin)
    projects = response.json()
    assert len(projects) >= 2
    assert any(p["id"] == p1.id for p in projects)
    assert any(p["id"] == p2.id for p in projects)

# ===== TEST MATERIAL ACCESS =====
def test_mahasiswa_cannot_see_unassigned_materials():
    headers_admin, admin = create_user_helper("admin_mat@test.com", "admin")
    headers_mhs, mahasiswa = create_user_helper("mhs_mat@test.com", "mahasiswa")
    project = create_project_helper(admin.id)
    material = create_material_helper(project.id)

    response = client.get("/materials/", headers=headers_mhs)
    materials = response.json()
    assert all(m["id"] != material.id for m in materials)

def test_mahasiswa_sees_assigned_materials():
    headers_admin, admin = create_user_helper("admin_mat2@test.com", "admin")
    headers_mhs, mahasiswa = create_user_helper("mhs_mat2@test.com", "mahasiswa")
    project = create_project_helper(admin.id)
    material = create_material_helper(project.id)

    # assign project
    db = database.SessionLocal()
    assignment = models.ProjectAssignment(user_id=mahasiswa.id, project_id=project.id)
    db.add(assignment)
    db.commit()
    db.close()

    response = client.get("/materials/", headers=headers_mhs)
    materials = response.json()
    assert any(m["id"] == material.id for m in materials)

def test_admin_sees_all_materials():
    headers_admin, admin = create_user_helper("admin_mat3@test.com", "admin")
    p1 = create_project_helper(admin.id)
    p2 = create_project_helper(admin.id)
    m1 = create_material_helper(p1.id)
    m2 = create_material_helper(p2.id)

    response = client.get("/materials/", headers=headers_admin)
    materials = response.json()
    assert len(materials) >= 2
    assert any(m["id"] == m1.id for m in materials)
    assert any(m["id"] == m2.id for m in materials)