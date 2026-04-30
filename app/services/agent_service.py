from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentUpdate


class AgentService:
    def __init__(self, db: Session):
        self.db = db

    # ---------------------------
    # GET ALL AGENTS
    # ---------------------------
    def get_all(self):
        return self.db.query(Agent).all()

    # ---------------------------
    # GET ONE AGENT
    # ---------------------------
    def get(self, agent_id: int):
        return self.db.query(Agent).filter(Agent.id == agent_id).first()

    # ---------------------------
    # CREATE AGENT
    # ---------------------------
    def create(self, data: AgentCreate):
        agent = Agent(
            name=data.name,
            role=data.role,
            email=data.email,
            department=data.department,
            skills=data.skills,
            status=data.status,
            price=data.price
        )
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)
        return agent

    # ---------------------------
    # UPDATE AGENT
    # ---------------------------
    def update(self, agent_id: int, data: AgentUpdate):
        agent = self.get(agent_id)
        if not agent:
            return None

        for field, value in data.dict(exclude_unset=True).items():
            setattr(agent, field, value)

        self.db.commit()
        self.db.refresh(agent)
        return agent

    # ---------------------------
    # DELETE AGENT
    # ---------------------------
    def delete(self, agent_id: int):
        agent = self.get(agent_id)
        if not agent:
            return False

        self.db.delete(agent)
        self.db.commit()
        return True
