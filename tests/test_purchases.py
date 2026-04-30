from fastapi.testclient import TestClient

from app import crud, schemas


def _get_auth_header(client: TestClient, username: str, password: str) -> dict:
    response = client.post(
        "/auth/login",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_purchases_me_requires_auth(client):
    """GET /purchases/me без токена має повертати 401."""
    response = client.get("/purchases/me")
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"


def test_purchases_me_empty_for_new_user(client, test_user):
    """Новий користувач з валідним токеном має порожній список покупок."""
    headers = _get_auth_header(client, test_user.email, "testpassword")
    response = client.get("/purchases/me", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


def test_create_purchase_and_list_it(client, test_user, db_session):
    """Після POST /purchases/ покупка створюється і відображається у /purchases/me."""
    # Створюємо агента, який буде куплений
    agent = crud.create_agent(
        db_session,
        schemas.AgentCreate(name="Test Agent", role="tester"),
    )

    headers = _get_auth_header(client, test_user.email, "testpassword")

    # Створюємо покупку
    response = client.post(
        "/purchases/",
        json={"user_id": test_user.id, "agent_id": agent.id},
        headers=headers,
    )
    assert response.status_code == 200
    purchase = response.json()
    assert purchase["user_id"] == test_user.id
    assert purchase["agent_id"] == agent.id

    # Перевіряємо, що покупка відображається у /purchases/me
    response = client.get("/purchases/me", headers=headers)
    assert response.status_code == 200
    purchases = response.json()
    assert len(purchases) == 1
    assert purchases[0]["agent_id"] == agent.id
    assert purchases[0]["agent_name"] == agent.name
    assert purchases[0]["agent_role"] == agent.role
