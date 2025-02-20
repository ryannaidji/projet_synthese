import pytest
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from backend.app.main import app 
from app.database import Base, get_db

SQLITE_DATABASE_URL = "sqlite:///./test_db.db"

engine = create_engine(
    SQLITE_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="module")
def db_session():
    """Create a new database session with a rollback at the end of the test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="module")
def test_client(db_session):
    """Create a test client that uses the override_get_db fixture to return a session."""

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="module")
def test_user(test_client):
    """Create a test user for authentication."""
    response = test_client.post("/api/users/register", json={"username": "testuser", "password": "testpassword", "role": "admin", "fullname": "Test User", "disabled": "False", "email":"testuser@localhost.local"})
    assert response.status_code == 200
    return {"username": "testuser", "password": "testpassword"}

@pytest.fixture(scope="module")
def token(test_client, test_user):
    """Authenticate test user and retrieve token."""
    response = test_client.post("/token", data={"username": test_user["username"], "password": test_user["password"]})
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture(scope="module")
def auth_headers(token):
    """Provide authorization headers for authenticated requests."""
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture()
def user_payload():
    """Generate a user payload."""
    return {
        "username": "johndoe",
        "fullname": "John Doe",
        "email": "johndoe@videotron.ca",
        "password": "secret",
        "role": "admin",
        "disabled": False
    }

@pytest.fixture()
def user_payload_updated():
    """Generate a user payload."""
    return {
        "username": "janedoe",
        "fullname": "Jane Doe",
        "email": "janedoe@videotron.ca",
        "password": "secret",
        "role": "admin",
        "disabled": False
    }

@pytest.fixture()
def patient_payload():
    """Generate a patient payload."""
    return {
        "name": "Guy Bol",
        "dob": "1999-03-03",
        "gender": "male",
        "phone": "444-444-4444",
        "address": "rue du Moulin",
    }

@pytest.fixture()
def patient_payload_updated():
    """Generate an updated patient payload."""
    return {
        "name": "Guy Bol",
        "dob": "1999-03-03",
        "gender": "male",
        "phone": "444-444-4444",
        "address": "rue des Moulins"
    }

@pytest.fixture()
def diagnostic_payload():
    """Generate a diagnostic payload."""
    return {
        "patient_id": 1,
        "analysis_link": "some link",
        "prediction": "TUMOR TYPE",
        "confidence": "0.99",
        "reviewed_comment": "average",
        "review_status": False,
        "doctor_id":2
    }


@pytest.fixture()
def diagnostic_payload_updated():
    """Generate an updated diagnostic payload."""
    return {
        "patient_id": 1,
        "analysis_link": "some link",
        "prediction": "TUMOR TYPE",
        "confidence": "0.99"
        "reviewed_comment": "critical",
        "review_status": False,
        "doctor_id":2
    }


