import pytest
from sqlalchemy.orm import sessionmaker
from app.database import engine, Base
from app.tests.utils import create_user

# Fixture untuk membuat session database
@pytest.fixture(scope="function")
def db_session():
    # Drop & create semua table tiap test supaya bersih
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Fixture untuk admin user
@pytest.fixture
def admin(db_session):
    return create_user(db_session, "admin@test.com", "adminpass", "admin")

# Fixture untuk mahasiswa user
@pytest.fixture
def mahasiswa(db_session):
    return create_user(db_session, "student@test.com", "studentpass", "mahasiswa")