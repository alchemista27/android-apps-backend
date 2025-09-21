import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import database, models

client = TestClient(app)

# fixture untuk setup & teardown DB
@pytest.fixture(autouse=True)
def setup_db():
    # sebelum test: bersihkan DB
    db = database.SessionLocal()
    db.query(models.User).delete()
    db.commit()
    db.close()
    yield
    # sesudah test: bersihkan lagi
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
    # daftar user dulu
    client.post(
        "/auth/register",
        json={
            "email": "loginuser@example.com",
            "password": "mypassword",
            "full_name": "Login User"
        }
    )
    # login
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
    # daftar user dulu
    client.post(
        "/auth/register",
        json={
            "email": "wrongpass@example.com",
            "password": "correctpass",
            "full_name": "Wrong Pass"
        }
    )
    # coba login dengan password salah
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