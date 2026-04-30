import requests

BASE_URL = "http://127.0.0.1:8000"

# Допоміжна функція для безпечного друку
def safe_print_response(label, response):
    try:
        print(label, response.json())
    except Exception:
        print(label, response.text)

# 1. Реєстрація користувача
def register_user(email, password):
    # Використовуємо json замість params
    response = requests.post(f"{BASE_URL}/users/", json={"email": email, "password": password})
    safe_print_response("Register:", response)

# 2. Логін
def login(email, password):
    response = requests.post(f"{BASE_URL}/login", data={"username": email, "password": password})
    safe_print_response("Login:", response)
    token = None
    try:
        token = response.json().get("access_token")
    except Exception:
        pass
    return token

# 3. Створення агента
def create_agent(token, agent_data):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/agent/", json=agent_data, headers=headers)
    safe_print_response("Create Agent:", response)
    try:
        return response.json().get("id")
    except Exception:
        return None

# 4. Отримати список агентів
def get_agents(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/agents/", headers=headers)
    safe_print_response("Agents:", response)

# 5. Оновлення агента (PUT)
def update_agent(token, agent_id, agent_data):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(f"{BASE_URL}/agent/{agent_id}", json=agent_data, headers=headers)
    safe_print_response("Update Agent:", response)

# 6. Часткове оновлення агента (PATCH)
def patch_agent(token, agent_id, partial_data):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.patch(f"{BASE_URL}/agent/{agent_id}", json=partial_data, headers=headers)
    safe_print_response("Patch Agent:", response)

# 7. Видалення агента
def delete_agent(token, agent_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{BASE_URL}/agent/{agent_id}", headers=headers)
    safe_print_response("Delete Agent:", response)

# 8. Пошук за email
def search_agent_by_email(token, email):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/agent/by_email/{email}", headers=headers)
    safe_print_response("Search by Email:", response)

# 9. Пошук за роллю
def search_agents_by_role(token, role):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/agents/by_role/{role}", headers=headers)
    safe_print_response("Search by Role:", response)

# 10. Пошук за відділом
def search_agents_by_department(token, department):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/agents/by_department/{department}", headers=headers)
    safe_print_response("Search by Department:", response)

# 11. Пошук за навичкою
def search_agents_by_skill(token, skill):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/agents/by_skill/{skill}", headers=headers)
    safe_print_response("Search by Skill:", response)

if __name__ == "__main__":
    email = "test@example.com"
    password = "MyStrongPass123"

    # Реєстрація
    register_user(email, password)

    # Логін
    token = login(email, password)

    if token:
        # Створення агента
        agent_data = {
            "name": "SEO Agent",
            "role": "SEO Specialist",
            "email": "seo@example.com",
            "department": "Marketing",
            "skills": "SEO, Keywords, Analytics",
            "status": True
        }
        agent_id = create_agent(token, agent_data)

        # Отримати список агентів
        get_agents(token)

        # Пошук за email
        search_agent_by_email(token, "seo@example.com")

        # Пошук за роллю
        search_agents_by_role(token, "SEO Specialist")

        # Пошук за відділом
        search_agents_by_department(token, "Marketing")

        # Пошук за навичкою
        search_agents_by_skill(token, "SEO")

        # Оновлення агента (PUT)
        if agent_id:
            updated_agent = {
                "name": "SEO Agent Updated",
                "role": "Senior SEO Specialist",
                "email": "seo@example.com",
                "department": "Marketing",
                "skills": "SEO, Keywords, Analytics, SEM",
                "status": True
            }
            update_agent(token, agent_id, updated_agent)

            # Часткове оновлення агента (PATCH)
            patch_agent(token, agent_id, {"role": "Head of SEO", "status": False})

            # Видалення агента
            delete_agent(token, agent_id)

            # Перевірити список агентів після видалення
            get_agents(token)
