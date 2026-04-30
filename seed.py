from app.database import SessionLocal
from app.models import User, Agent, Purchase
from app.core.security import hash_password
from datetime import datetime


# ============================
# HELPERS
# ============================
def log(msg: str):
    print(f"[SEED] {msg}")


# ============================
# CREATE USER IF NOT EXISTS
# ============================
def create_user(db, email: str, password: str, role: str, balance: int = 0):
    user = db.query(User).filter(User.email == email).first()
    if user:
        log(f"User already exists: {email}")
        return user

    user = User(
        email=email,
        hashed_password=hash_password(password),
        role=role,
        balance=balance,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    log(f"Created {role}: {email}")
    return user


# ============================
# CREATE AGENT IF NOT EXISTS
# ============================
def create_agent(db, name: str, role: str, price: int, department: str = None):
    agent = db.query(Agent).filter(Agent.name == name).first()
    if agent:
        log(f"Agent already exists: {name}")
        return agent

    agent = Agent(
        name=name,
        role=role,
        price=price,
        department=department,
        status=True,
        skills="Demo skills",
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)

    log(f"Created agent: {name}")
    return agent


# ============================
# CREATE PURCHASE IF NOT EXISTS
# ============================
def create_purchase(db, user_id: int, agent_id: int, price: int):
    purchase = (
        db.query(Purchase)
        .filter(Purchase.user_id == user_id, Purchase.agent_id == agent_id)
        .first()
    )
    if purchase:
        log(f"Purchase already exists for user {user_id} -> agent {agent_id}")
        return purchase

    purchase = Purchase(
        user_id=user_id,
        agent_id=agent_id,
        price=price,
        created_at=datetime.utcnow(),
    )
    db.add(purchase)
    db.commit()
    db.refresh(purchase)

    log(f"Created purchase: user {user_id} bought agent {agent_id}")
    return purchase


# ============================
# MAIN SEED FUNCTION
# ============================
def run_seed():
    db = SessionLocal()
    log("=== Starting SEED ===")

    # 1. USERS
    admin = create_user(db, "admin@example.com", "admin123", "admin", balance=0)
    user = create_user(db, "user@example.com", "user123", "user", balance=200)

    # 2. DEMO AGENTS
    agent1 = create_agent(db, "SEO Agent", "SEO Specialist", price=50)
    agent2 = create_agent(db, "Marketing Agent", "Marketing Expert", price=70)
    agent3 = create_agent(db, "Analytics Agent", "Data Analyst", price=40)
    agent4 = create_agent(db, "Support Agent", "Customer Support", price=30)
    agent5 = create_agent(db, "Sales Agent", "Sales Manager", price=60)

    # 3. TEST PURCHASES (user buys 3 agents)
    create_purchase(db, user.id, agent1.id, agent1.price)
    create_purchase(db, user.id, agent3.id, agent3.price)
    create_purchase(db, user.id, agent5.id, agent5.price)

    log("=== SEED COMPLETED ===")
    db.close()


if __name__ == "__main__":
    run_seed()
