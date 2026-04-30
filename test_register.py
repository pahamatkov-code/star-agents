import requests

BASE_URL = "http://localhost:8000"

def test_register():
    payload = {
        "email": "testuser@example.com",
        "password": "secret123"
    }
    response = requests.post(f"{BASE_URL}/users/register", json=payload)
    print("Status:", response.status_code)
    print("Response:", response.text)

def test_login():
    payload = {
        "username": "testuser@example.com",
        "password": "secret123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", data=payload)
    print("Status:", response.status_code)
    print("Response:", response.text)

if __name__ == "__main__":
    print("=== Register ===")
    test_register()
    print("\n=== Login ===")
    test_login()
