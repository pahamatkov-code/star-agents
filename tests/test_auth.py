
def test_successful_login(client, test_user):
    """Тест успішного логіну з правильними даними."""
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_failed_login_wrong_password(client, test_user):
    """Тест невдалого логіну з неправильним паролем."""
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid credentials"


def test_failed_login_nonexistent_user(client):
    """Тест невдалого логіну з неіснуючим користувачем."""
    response = client.post(
        "/auth/login",
        data={"username": "nonexistent@example.com", "password": "password"}
    )
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid credentials"