import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine, SessionLocal
from app.models.user import User
from app.core.security import hash_password, create_access_token

client = TestClient(app)


def get_auth_header():
    db = SessionLocal()
    user = db.query(User).filter(User.username == "wftest").first()
    if not user:
        user = User(username="wftest", email="wf@test.com", hashed_password=hash_password("pass123"))
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


class TestWorkflows:
    def test_create_workflow(self):
        headers = get_auth_header()
        response = client.post("/api/v1/workflows", json={
            "name": "Test Workflow",
            "description": "A test workflow",
            "nodes": [{"id": "n1", "type": "llm", "position": {"x": 100, "y": 100}, "data": {"label": "LLM"}}],
            "edges": []
        }, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Workflow"
        assert len(data["nodes"]) == 1

    def test_list_workflows(self):
        headers = get_auth_header()
        response = client.get("/api/v1/workflows", headers=headers)
        assert response.status_code == 200
        assert "items" in response.json()

    def test_execute_workflow(self):
        headers = get_auth_header()
        create = client.post("/api/v1/workflows", json={
            "name": "Exec Test",
            "nodes": [{"id": "start", "type": "input", "position": {"x": 0, "y": 0}, "data": {"label": "Start"}}],
        }, headers=headers)
        wf_id = create.json()["id"]
        response = client.post(f"/api/v1/workflows/{wf_id}/execute", headers=headers, json={})
        assert response.status_code == 200
        assert response.json()["status"] == "completed"

    def test_delete_workflow(self):
        headers = get_auth_header()
        create = client.post("/api/v1/workflows", json={"name": "Delete Test"}, headers=headers)
        wf_id = create.json()["id"]
        response = client.delete(f"/api/v1/workflows/{wf_id}", headers=headers)
        assert response.status_code == 200

    def test_workflow_not_found(self):
        headers = get_auth_header()
        response = client.get("/api/v1/workflows/99999", headers=headers)
        assert response.status_code == 404
