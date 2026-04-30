import requests
import sys
import time

BASE_URL = "http://localhost:8000"

def check_response(r, step_name, expected=200):
    if r.status_code != expected:
        print(f"{step_name} FAILED: {r.status_code} {r.text}")
        sys.exit(1)
    else:
        print(f"{step_name} OK: {r.status_code} {r.text}")
    return r

def register_user(email):
    payload = {"email": email, "password": "secret123"}
    r = requests.post(f"{BASE_URL}/users/register", json=payload)
    return check_response(r, "Register")

def login_user(email):
    payload = {"username": email, "password": "secret123"}
    r = requests.post(f"{BASE_URL}/auth/login", data=payload)
    r = check_response(r, "Login")
    return r.json()["access_token"]

def create_agent(token):
    agent_name = f"TestAgent_{int(time.time())}"
    payload = {
        "name": agent_name,
        "role": "Support",
        "email": "agent@example.com",
        "department": "Sales",
        "skills": "Communication",
        "status": True   # тепер булеве значення
    }
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(f"{BASE_URL}/agents/", json=payload, headers=headers)
    r = check_response(r, "Create Agent")
    agent_id = r.json().get("id")
    if not agent_id:
        print("Create Agent FAILED: no agent_id in response")
        sys.exit(1)
    return agent_id

def purchase_agent(token, agent_id):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(f"{BASE_URL}/agents/purchase?agent_id={agent_id}", headers=headers)
    return check_response(r, "Purchase Agent")

def get_purchases(token):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE_URL}/users/me/purchases", headers=headers)
    return check_response(r, "My Purchases")

if __name__ == "__main__":
    # генеруємо унікальний email для кожного запуску
    email = f"testuser_{int(time.time())}@example.com"

    register_user(email)
    token = login_user(email)
    agent_id = create_agent(token)
    purchase_agent(token, agent_id)
    get_purchases(token)
