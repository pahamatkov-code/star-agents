from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import get_password_hash
from app.models.user import User
from app.models.agent import Agent
from app.models.purchase import Purchase
from app.models.balance_transaction import BalanceTransaction

router = APIRouter(prefix="/seed", tags=["Seed"])


@router.post("/users")
def seed_users(db: Session = Depends(get_db)):
    # Admin
    admin = db.query(User).filter(User.email == "admin@example.com").first()
    if not admin:
        admin = User(
            email="admin@example.com",
            hashed_password=get_password_hash("admin"),
            role="admin",
            balance=1000,
        )
        db.add(admin)

    # Regular user
    user = db.query(User).filter(User.email == "user@example.com").first()
    if not user:
        user = User(
            email="user@example.com",
            hashed_password=get_password_hash("user"),
            role="user",
            balance=500,
        )
        db.add(user)

    db.commit()
    return {"status": "ok", "message": "Users seeded"}


@router.post("/agents")
def seed_agents(db: Session = Depends(get_db)):
    agents = [
        Agent(
            name="Agent Alpha",
            role="assistant",
            email="alpha@ai.com",
            department="AI",
            skills="NLP",
            status="active",
            price=50,
        ),
        Agent(
            name="Agent Beta",
            role="helper",
            email="beta@ai.com",
            department="Automation",
            skills="Scripting",
            status="active",
            price=30,
        ),
    ]

    db.add_all(agents)
    db.commit()
    return {"status": "ok", "created": len(agents)}


@router.post("/clear")
def clear_all(db: Session = Depends(get_db)):
    db.query(Purchase).delete()
    db.query(BalanceTransaction).delete()
    db.query(Agent).delete()
    db.query(User).delete()
    db.commit()
    return {"status": "cleared"}
