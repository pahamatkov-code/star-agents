# -*- coding: utf-8 -*-
"""
API для роботи з агентами - ФІНАЛЬНА ВЕРСІЯ
Повний CRUD з авторизацією, валідацією та розширеними можливостями
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, require_admin, require_role
from app.models.agent import Agent
from app.models.user import User
from app.schemas.agent import AgentCreate, AgentUpdate, AgentRead, AgentList
from app.services.agent_service import AgentService

router = APIRouter(prefix="/agents", tags=["Agents"])


# ============================================================
# GET / - Список всіх агентів
# ============================================================
@router.get("/", response_model=AgentList)
async def list_agents(
    skip: int = Query(0, ge=0, description="Кількість записів для пропуску"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальна кількість записів"),
    search: Optional[str] = Query(None, description="Пошук за назвою або описом"),
    active_only: bool = Query(False, description="Тільки активні агенти"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Отримати список всіх агентів з пагінацією та фільтрацією.
    
    - **skip**: Кількість записів для пропуску (пагінація)
    - **limit**: Максимальна кількість записів
    - **search**: Пошук за назвою або описом
    - **active_only**: Показати тільки активні агенти
    """
    service = AgentService(db)
    
    # Будуємо фільтри
    filters = {}
    if active_only:
        filters["is_active"] = True
    if search:
        filters["search"] = search
    
    agents = service.get_all(skip=skip, limit=limit, **filters)
    total = service.count(**filters)
    
    return {
        "agents": agents,
        "total": total,
        "skip": skip,
        "limit": limit
    }


# ============================================================
# GET /{agent_id} - Отримати агента за ID
# ============================================================
@router.get("/{agent_id}", response_model=AgentRead)
async def get_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Отримати детальну інформацію про агента за ID.
    """
    service = AgentService(db)
    agent = service.get(agent_id)
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID {agent_id} not found"
        )
    
    return agent


# ============================================================
# POST / - Створити нового агента
# ============================================================
@router.post("/", response_model=AgentRead, status_code=status.HTTP_201_CREATED)
async def create_agent(
    data: AgentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Створити нового агента (тільки для адміністратора).
    
    - **name**: Унікальна назва агента
    - **description**: Опис агента
    - **model**: Модель для використання (за замовчуванням: gpt-4)
    - **system_prompt**: Системний промпт для агента
    - **is_active**: Статус активності (за замовчуванням: true)
    """
    service = AgentService(db)
    
    # Перевіряємо чи агент з таким ім'ям вже існує
    existing = service.get_by_name(data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent with name '{data.name}' already exists"
        )
    
    try:
        agent = service.create(data.dict())
        return agent
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create agent: {str(e)}"
        )


# ============================================================
# PUT /{agent_id} - Оновити агента
# ============================================================
@router.put("/{agent_id}", response_model=AgentRead)
async def update_agent(
    agent_id: int,
    data: AgentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Оновити інформацію про агента (тільки для адміністратора).
    
    Можна оновити будь-які поля: назву, опис, модель, системний промпт, статус.
    """
    service = AgentService(db)
    
    # Перевіряємо чи агент існує
    agent = service.get(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID {agent_id} not found"
        )
    
    # Перевіряємо унікальність назви (якщо змінюється)
    if data.name and data.name != agent.name:
        existing = service.get_by_name(data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Agent with name '{data.name}' already exists"
            )
    
    try:
        updated_agent = service.update(agent_id, data.dict(exclude_unset=True))
        return updated_agent
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update agent: {str(e)}"
        )


# ============================================================
# DELETE /{agent_id} - Видалити агента
# ============================================================
@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Видалити агента (тільки для адміністратора).
    
    Увага! Ця дія незворотна.
    """
    service = AgentService(db)
    
    # Перевіряємо чи агент існує
    agent = service.get(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID {agent_id} not found"
        )
    
    try:
        service.delete(agent_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete agent: {str(e)}"
        )


# ============================================================
# PATCH /{agent_id}/toggle - Переключити статус агента
# ============================================================
@router.patch("/{agent_id}/toggle", response_model=AgentRead)
async def toggle_agent_status(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Переключити статус активності агента (тільки для адміністратора).
    """
    service = AgentService(db)
    
    agent = service.get(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID {agent_id} not found"
        )
    
    try:
        updated_agent = service.toggle_status(agent_id)
        return updated_agent
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to toggle agent status: {str(e)}"
        )


# ============================================================
# GET /{agent_id}/stats - Статистика агента
# ============================================================
@router.get("/{agent_id}/stats")
async def get_agent_stats(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Отримати статистику використання агента.
    """
    service = AgentService(db)
    
    agent = service.get(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID {agent_id} not found"
        )
    
    stats = service.get_stats(agent_id)
    return stats


# ============================================================
# GET /stats/global - Глобальна статистика
# ============================================================
@router.get("/stats/global")
async def get_global_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Отримати глобальну статистику по всіх агентах (тільки для адміністратора).
    """
    service = AgentService(db)
    stats = service.get_global_stats()
    return stats