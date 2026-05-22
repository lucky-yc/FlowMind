import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine, SessionLocal
from app.models.user import User
from app.core.security import hash_password, create_access_token

client = TestClient(app)


def get_auth_header():
    db = SessionLocal()
    user = db.query(User).filter(User.username == "tktest").first()
    if not user:
        user = User(username="tktest", email="tk@test.com", hashed_password=hash_password("pass123"))
        db.add(user)
        db.commit()
        db.refresh(user)
    db.close()
    token = create_access_token({"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield


class TestTasks:
    def test_create_task(self):
        headers = get_auth_header()
        response = client.post("/api/v1/tasks", json={
            "name": "Test Task",
            "schedule_type": "manual",
            "priority": 5,
        }, headers=headers)
        assert response.status_code == 200
        assert response.json()["name"] == "Test Task"

    def test_list_tasks(self):
        headers = get_auth_header()
        response = client.get("/api/v1/tasks", headers=headers)
        assert response.status_code == 200

    def test_run_task(self):
        headers = get_auth_header()
        create = client.post("/api/v1/tasks", json={"name": "Run Task"}, headers=headers)
        task_id = create.json()["id"]
        response = client.post(f"/api/v1/tasks/{task_id}/run", headers=headers)
        assert response.status_code == 200
        assert response.json()["status"] == "completed"

    def test_dashboard_stats(self):
        headers = get_auth_header()
        response = client.get("/api/v1/dashboard/stats", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "workflow_count" in data
        assert "agent_count" in data
