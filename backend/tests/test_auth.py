import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine, SessionLocal
from app.models.user import User
from app.core.security import hash_password

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    existing = db.query(User).filter(User.username == "testuser").first()
    if not existing:
        user = User(username="testuser", email="test@test.com", hashed_password=hash_password("testpass123"))
        db.add(user)
        db.commit()
    db.close()
    yield
    # Don't drop tables between tests


class TestAuth:
    def test_register(self):
        response = client.post("/api/v1/auth/register", json={
            "username": "newuser",
            "email": "new@test.com",
            "password": "password123",
            "full_name": "New User"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["username"] == "newuser"

    def test_register_duplicate(self):
        client.post("/api/v1/auth/register", json={
            "username": "dupuser", "email": "dup@test.com", "password": "pass123"
        })
        response = client.post("/api/v1/auth/register", json={
            "username": "dupuser", "email": "dup2@test.com", "password": "pass123"
        })
        assert response.status_code == 400

    def test_login_success(self):
        response = client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_wrong_password(self):
        response = client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "wrongpass"
        })
        assert response.status_code == 401

    def test_get_me(self):
        login = client.post("/api/v1/auth/login", json={"username": "testuser", "password": "testpass123"})
        token = login.json()["access_token"]
        response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["username"] == "testuser"

    def test_get_me_no_token(self):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 403
