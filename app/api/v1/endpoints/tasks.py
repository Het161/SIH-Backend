from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.db.session import get_db
from app.models.task import Task, TaskStatus
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

# ===== PYDANTIC SCHEMAS =====

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    status: str = "pending"
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None

class UpdateTaskStatusRequest(BaseModel):
    status: str

# ===== ENDPOINTS =====

@router.get("/")
def get_all_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all tasks with pagination"""
    try:
        tasks = db.query(Task).offset(skip).limit(limit).all()
        
        return {
            "success": True,
            "data": [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "priority": task.priority,
                    "assigned_to": task.assigned_to,
                    "created_by": task.created_by if hasattr(task, 'created_by') else None,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                }
                for task in tasks
            ],
            "total": len(tasks),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
def create_task(
    request: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new task"""
    try:
        task_data = request.dict()
        task_data['created_by'] = current_user.id
        
        task = Task(**task_data)
        db.add(task)
        db.commit()
        db.refresh(task)
        
        # Add initial status record
        try:
            db.add(TaskStatus(task_id=task.id, status="pending"))
            db.commit()
        except Exception as e:
            print(f"Failed to add TaskStatus: {e}")
        
        return {
            "success": True,
            "data": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "priority": task.priority,
                "created_by": task.created_by,
            },
            "message": "Task created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}")
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific task by ID"""
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "success": True,
        "data": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "assigned_to": task.assigned_to,
            "created_by": task.created_by if hasattr(task, 'created_by') else None,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "created_at": task.created_at.isoformat() if task.created_at else None,
        }
    }

@router.put("/{task_id}")
def update_task(
    task_id: int,
    request: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    for key, value in request.dict(exclude_unset=True).items():
        if value is not None:
            setattr(task, key, value)
    
    db.commit()
    db.refresh(task)
    
    return {
        "success": True,
        "message": "Task updated successfully"
    }

@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    
    return {
        "success": True,
        "message": "Task deleted successfully"
    }

@router.patch("/{task_id}/status")
def update_task_status(
    task_id: int,
    request: UpdateTaskStatusRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update task status"""
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.status = request.status
    db.commit()
    
    return {
        "success": True,
        "message": "Task status updated"
    }

@router.get("/search/all")
def search_tasks(
    status: Optional[str] = None,
    assigned_to: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = Query(50, le=100),
    skip: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search and filter tasks"""
    query = db.query(Task)
    
    if assigned_to:
        query = query.filter(Task.assigned_to == assigned_to)
    
    if status:
        query = query.filter(Task.status == status)
    
    if search:
        query = query.filter(
            (Task.title.ilike(f"%{search}%")) |
            (Task.description.ilike(f"%{search}%"))
        )
    
    tasks = query.offset(skip).limit(limit).all()
    
    return {
        "success": True,
        "data": [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "assigned_to": task.assigned_to,
                "created_by": task.created_by if hasattr(task, 'created_by') else None,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "created_at": task.created_at.isoformat() if task.created_at else None
            }
            for task in tasks
        ]
    }



