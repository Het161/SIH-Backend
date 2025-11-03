from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/tasks", tags=["tasks"])

# ===== SCHEMAS =====
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    status: str = "pending"
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# ===== GET ALL TASKS =====
@router.get("/", response_model=List[TaskResponse])
async def get_all_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all tasks
    - **skip**: Number of tasks to skip (for pagination)
    - **limit**: Maximum number of tasks to return
    - **status**: Filter by status (optional)
    """
    # Return empty list for now (add database query later)
    return []

# ===== GET TASK BY ID =====
@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get task by ID"""
    # TODO: Add database query
    raise HTTPException(status_code=404, detail="Task not found")

# ===== CREATE TASK =====
@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new task"""
    # Mock response for now
    return {
        "id": 1,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "status": task.status,
        "created_at": datetime.utcnow()
    }

# ===== UPDATE TASK =====
@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a task"""
    raise HTTPException(status_code=404, detail="Task not found")

# ===== DELETE TASK =====
@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a task"""
    raise HTTPException(status_code=404, detail="Task not found")
