from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.db.models.task import Task, TaskStatus, Review
from app.models.user import User
from pydantic import BaseModel
from typing import List
import datetime

router = APIRouter()

class DashboardSummary(BaseModel):
    total_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    completed_tasks: int
    overdue_tasks: int
    total_users: int
    recent_tasks: List[dict]

@router.get("/dashboard/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get dashboard summary statistics"""
    
    # Total tasks
    total_tasks = db.query(Task).count()
    
    # Count by status
    pending = db.query(TaskStatus).filter(TaskStatus.status == "Assigned").count()
    in_progress = db.query(TaskStatus).filter(TaskStatus.status == "In Progress").count()
    completed = db.query(Review).filter(Review.status == "Approved").count()
    
    # Overdue tasks
    overdue = db.query(Task).filter(
        Task.due_date < datetime.datetime.utcnow()
    ).filter(
        ~Task.id.in_(
            db.query(Review.task_id).filter(Review.status == "Approved")
        )
    ).count()
    
    # Total users
    total_users = db.query(User).count()
    
    # Recent tasks (last 5)
    recent = db.query(Task).order_by(Task.created_at.desc()).limit(5).all()
    recent_tasks = [
        {
            "id": str(task.id),
            "title": task.title,
            "created_at": task.created_at,
            "due_date": task.due_date
        }
        for task in recent
    ]
    
    return DashboardSummary(
        total_tasks=total_tasks,
        pending_tasks=pending,
        in_progress_tasks=in_progress,
        completed_tasks=completed,
        overdue_tasks=overdue,
        total_users=total_users,
        recent_tasks=recent_tasks
    )

@router.get("/dashboard/user/{user_id}")
def get_user_dashboard(user_id: str, db: Session = Depends(get_db)):
    """Get dashboard for a specific user"""
    
    # User's tasks
    my_tasks = db.query(Task).filter(Task.assigned_to == user_id).count()
    
    # My pending tasks
    my_pending = db.query(Task).filter(
        Task.assigned_to == user_id
    ).filter(
        ~Task.id.in_(
            db.query(Review.task_id).filter(Review.status == "Approved")
        )
    ).count()
    
    # My completed tasks
    my_completed = db.query(Task).join(Review).filter(
        Task.assigned_to == user_id,
        Review.status == "Approved"
    ).count()
    
    # My overdue tasks
    my_overdue = db.query(Task).filter(
        Task.assigned_to == user_id,
        Task.due_date < datetime.datetime.utcnow()
    ).filter(
        ~Task.id.in_(
            db.query(Review.task_id).filter(Review.status == "Approved")
        )
    ).count()
    
    return {
        "total_tasks": my_tasks,
        "pending_tasks": my_pending,
        "completed_tasks": my_completed,
        "overdue_tasks": my_overdue
    }
