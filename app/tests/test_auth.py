import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import database, models, auth
from app.tests.utils import create_user
from app.database import SessionLocal, Base, engine

# jangan lagi panggil User langsung pakai password
admin = create_user(db_session, "admin@test.com", "adminpass", "admin")

client = TestClient(app)

# fixture untuk setup & teardown DB
@pytest.fixture(autouse=True)
def setup_db():
    db = database.SessionLocal()
    db.query(models.User).delete()
    db.commit()
    db.close()
    yield
    db = database.SessionLocal()
    db.query(models.User).delete()
    db.commit()
    db.close()

def test_register_user_success():
    response = client.post(
        "/auth/register",
        json={
            "email": "testuser@example.com",
            "password": "secret123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert "id" in data

def test_register_user_duplicate():
    # pertama kali register
    client.post(
        "/auth/register",
        json={
            "email": "dupe@example.com",
            "password": "secret123",
            "full_name": "User Dupe"
        }
    )
    # kedua kali harus gagal
    response = client.post(
        "/auth/register",
        json={
            "email": "dupe@example.com",
            "password": "secret123",
            "full_name": "User Dupe"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email sudah terdaftar"

def test_login_success():
    client.post(
        "/auth/register",
        json={
            "email": "loginuser@example.com",
            "password": "mypassword",
            "full_name": "Login User"
        }
    )
    response = client.post(
        "/auth/login",
        json={
            "email": "loginuser@example.com",
            "password": "mypassword"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_password():
    client.post(
        "/auth/register",
        json={
            "email": "wrongpass@example.com",
            "password": "correctpass",
            "full_name": "Wrong Pass"
        }
    )
    response = client.post(
        "/auth/login",
        json={
            "email": "wrongpass@example.com",
            "password": "wrongpass"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_login_nonexistent_user():
    response = client.post(
        "/auth/login",
        json={
            "email": "nouser@example.com",
            "password": "doesntmatter"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

# ==== Tambahan extra tests di sini (tidak dipisah file) ====

def create_user(email="user@example.com", password="password123", role="mahasiswa"):
    db = database.SessionLocal()
    user = models.User(
        email=email,
        full_name="Test User",
        hashed_password=auth.hash_password(password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user

def get_token(email, password):
    response = client.post(
        "/auth/login",
        json={"email": email, "password": password}
    )
    return response.json()["access_token"]

def test_get_current_user_success():
    create_user("me@example.com", "mypassword", role="mahasiswa")
    token = get_token("me@example.com", "mypassword")

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    assert data["role"] == "mahasiswa"

def test_get_current_user_invalid_token():
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalidtoken123"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

def test_get_current_user_missing_token():
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_role_assignment_and_access():
    create_user("lecturer@example.com", "dosenpass", role="dosen")
    token_dosen = get_token("lecturer@example.com", "dosenpass")

    response = client.post(
        "/projects/assign",
        headers={"Authorization": f"Bearer {token_dosen}"},
        json={"project_id": 1, "student_id": 1}
    )
    assert response.status_code in (404, 422)

def test_role_access_denied_for_mahasiswa():
    create_user("student@example.com", "studpass", role="mahasiswa")
    token_student = get_token("student@example.com", "studpass")

    response = client.post(
        "/projects/assign",
        headers={"Authorization": f"Bearer {token_student}"},
        json={"project_id": 1, "student_id": 1}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden"

def test_token_case_insensitive_bearer():
    create_user("case@example.com", "casepass")
    token = get_token("case@example.com", "casepass")

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"bEaReR {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "case@example.com"