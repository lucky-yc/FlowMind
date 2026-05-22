import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine, SessionLocal
from app.models.user import User
from app.core.security import hash_password, create_access_token

client = TestClient(app)


def get_auth_header():
    db = SessionLocal()
    user = db.query(User).filter(User.username == "agtest").first()
    if not user:
        user = User(username="agtest", email="ag@test.com", hashed_password=hash_password("pass123"))
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


class TestAgents:
    def test_create_agent(self):
        headers = get_auth_header()
        response = client.post("/api/v1/agents", json={
            "name": "Test Bot",
            "description": "A test agent",
            "agent_type": "chatbot",
            "model_name": "GPT-4",
        }, headers=headers)
        assert response.status_code == 200
        assert response.json()["name"] == "Test Bot"

    def test_list_agents(self):
        headers = get_auth_header()
        response = client.get("/api/v1/agents", headers=headers)
        assert response.status_code == 200

    def test_agent_chat(self):
        headers = get_auth_header()
        create = client.post("/api/v1/agents", json={"name": "ChatBot", "agent_type": "chatbot"}, headers=headers)
        agent_id = create.json()["id"]
        response = client.post(f"/api/v1/agents/{agent_id}/chat", json={"message": "hello"}, headers=headers)
        assert response.status_code == 200
        assert "response" in response.json()

    def test_delete_agent(self):
        headers = get_auth_header()
        create = client.post("/api/v1/agents", json={"name": "Del Bot"}, headers=headers)
        agent_id = create.json()["id"]
        response = client.delete(f"/api/v1/agents/{agent_id}", headers=headers)
        assert response.status_code == 200
