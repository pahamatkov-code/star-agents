from sqlalchemy.orm import Session
from datetime import datetime, UTC

from app import models, schemas
from app.utils import get_password_hash


# === КОРИСТУВАЧІ ===
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate, hashed_password: str | None = None):
    # якщо передали готовий хеш — використовуємо його, інакше хешуємо тут
    hashed_pw = hashed_password or get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_pw, is_active=True)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# === АГЕНТИ ===
def get_agent(db: Session, agent_id: int):
    return db.query(models.Agent).filter(models.Agent.id == agent_id).first()


def get_agents(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Agent).offset(skip).limit(limit).all()


def create_agent(db: Session, agent: schemas.AgentCreate):
    db_agent = models.Agent(
        name=agent.name,
        role=agent.role,
        email=agent.email,
        department=agent.department,
        skills=agent.skills,
        status=agent.status,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent


def update_agent(db: Session, agent_id: int, agent_update: schemas.AgentPartialUpdate):
    db_agent = get_agent(db, agent_id)
    if not db_agent:
        return None

    for field, value in agent_update.dict(exclude_unset=True).items():
        setattr(db_agent, field, value)

    db_agent.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(db_agent)
    return db_agent


def delete_agent(db: Session, agent_id: int):
    db_agent = get_agent(db, agent_id)
    if not db_agent:
        return None
    db.delete(db_agent)
    db.commit()
    return db_agent


# === ПОКУПКИ ===
def create_purchase(db: Session, purchase: schemas.PurchaseCreate):
    db_purchase = models.Purchase(
        user_id=purchase.user_id,
        agent_id=purchase.agent_id,
        timestamp=datetime.now(UTC),
    )
    db.add(db_purchase)
    db.commit()
    db.refresh(db_purchase)
    return db_purchase


def get_purchase(db: Session, purchase_id: int):
    return db.query(models.Purchase).filter(models.Purchase.id == purchase_id).first()


def get_purchases(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Purchase).offset(skip).limit(limit).all()


def get_purchases_by_user(db: Session, user_id: int):
    return db.query(models.Purchase).filter(models.Purchase.user_id == user_id).all()


def delete_purchase(db: Session, purchase_id: int):
    db_purchase = get_purchase(db, purchase_id)
    if not db_purchase:
        return None
    db.delete(db_purchase)
    db.commit()
    return db_purchase
