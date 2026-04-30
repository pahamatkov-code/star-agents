# app/routers/agents.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, crud, database
from app.auth import get_current_user

router = APIRouter(
    prefix="/agents",
    tags=["agents"],
)

@router.get("/", response_model=list[schemas.Agent])
def read_agents(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_agents(db)

@router.get("/{agent_id}", response_model=schemas.Agent)
def read_agent(agent_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    agent = crud.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.post("/", response_model=schemas.Agent)
def create_agent(agent: schemas.AgentCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_agent(db, agent)

@router.patch("/{agent_id}", response_model=schemas.Agent)
def update_agent(agent_id: int, agent_update: schemas.AgentUpdate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    updated_agent = crud.update_agent(db, agent_id, agent_update)
    if not updated_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return updated_agent

@router.delete("/{agent_id}")
def delete_agent(agent_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    deleted = crud.delete_agent(db, agent_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"detail": "Agent deleted"}
