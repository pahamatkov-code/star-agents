from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role
from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentRead
from app.services.agent_service import AgentService

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.get("/", response_model=list[AgentRead])
def list_agents(db: Session = Depends(get_db)):
    service = AgentService(db)
    return service.get_all()


@router.post("/", response_model=AgentRead, dependencies=[Depends(require_role("admin"))])
def create_agent(
    data: AgentCreate,
    db: Session = Depends(get_db)
):
    service = AgentService(db)
    return service.create(data)


@router.get("/{agent_id}", response_model=AgentRead)
def get_agent(
    agent_id: int,
    db: Session = Depends(get_db)
):
    service = AgentService(db)
    agent = service.get(agent_id)

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return agent
