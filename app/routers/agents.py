from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import Agent, User, Purchase
from app.schemas import AgentCreate, AgentData, AgentPartialUpdate, PurchaseData
from app.routers.auth import get_current_user  # токен-автентифікація

router = APIRouter(prefix="/agents", tags=["agents"])

# === CRUD для Agent ===
@router.post("/", response_model=AgentData)
def create_agent(agent: AgentCreate,
                 db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    db_agent = Agent(**agent.dict())
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

@router.get("/{agent_id}", response_model=AgentData)
def read_agent(agent_id: int,
               db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.get("/", response_model=List[AgentData])
def read_agents(db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    return db.query(Agent).all()

@router.put("/{agent_id}", response_model=AgentData)
def update_agent(agent_id: int, agent: AgentCreate,
                 db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    for key, value in agent.dict().items():
        setattr(db_agent, key, value)
    db.commit()
    db.refresh(db_agent)
    return db_agent

@router.patch("/{agent_id}", response_model=AgentData)
def partial_update_agent(agent_id: int, agent: AgentPartialUpdate,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    for key, value in agent.dict(exclude_unset=True).items():
        setattr(db_agent, key, value)
    db.commit()
    db.refresh(db_agent)
    return db_agent

@router.delete("/{agent_id}")
def delete_agent(agent_id: int,
                 db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    db.delete(db_agent)
    db.commit()
    return {"detail": "Agent deleted"}

# === Пошукові ендпоінти ===
@router.get("/by_role/{role}", response_model=List[AgentData])
def get_agents_by_role(role: str,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    return db.query(Agent).filter(func.lower(Agent.role) == role.lower()).all()

@router.get("/by_email/{email}", response_model=AgentData)
def get_agent_by_email(email: str,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    agent = db.query(Agent).filter(func.lower(Agent.email) == email.lower()).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.get("/by_skill/{skill}", response_model=List[AgentData])
def get_agents_by_skill(skill: str,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    return db.query(Agent).filter(func.lower(Agent.skills).contains(skill.strip().lower())).all()

@router.get("/by_skills/", response_model=List[AgentData])
def get_agents_by_skills(skills: List[str] = Query(...),
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    query = db.query(Agent)
    for skill in skills:
        query = query.filter(func.lower(Agent.skills).contains(skill.strip().lower()))
    return query.all()

@router.get("/by_department/{department}", response_model=List[AgentData])
def get_agents_by_department(department: str,
                             db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user)):
    return db.query(Agent).filter(func.lower(Agent.department) == department.lower()).all()

@router.get("/search/", response_model=List[AgentData])
def search_agents(department: Optional[str] = None,
                  skill: Optional[str] = None,
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    query = db.query(Agent)
    if department:
        query = query.filter(func.lower(Agent.department) == department.lower())
    if skill:
        query = query.filter(func.lower(Agent.skills).contains(skill.strip().lower()))
    return query.all()

# === Покупки ===
@router.post("/purchase", response_model=PurchaseData)
def purchase_agent(agent_id: int,
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    purchase = Purchase(
        user_id=current_user.id,
        agent_id=agent.id,
        agent_name=agent.name,
        agent_role=agent.role,
        timestamp=datetime.utcnow()
    )
    db.add(purchase)
    db.commit()
    db.refresh(purchase)
    return purchase

@router.get("/my_purchases", response_model=List[PurchaseData])
def get_my_purchases(db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    return db.query(Purchase).filter(Purchase.user_id == current_user.id).all()

# Додай імпорти на початку файлу
from app.services.ai_service import ask_agent
from app.schemas import ChatMessage, ChatResponse

# Додай в кінець файлу
@router.post("/{agent_id}/chat", response_model=ChatResponse)
def chat_with_agent(
    agent_id: int,
    chat: ChatMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Відправити повідомлення AI-агенту і отримати відповідь.
    """
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if not agent.status:
        raise HTTPException(status_code=400, detail="Agent is inactive")

    try:
        response_text = ask_agent(
            message=chat.message,
            agent_name=agent.name,
            role=agent.role,
            skills=agent.skills
        )

        return ChatResponse(
            agent_id=agent.id,
            agent_name=agent.name,
            message=chat.message,
            response=response_text,
            status="success"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Помилка AI агента: {str(e)}"
        )
