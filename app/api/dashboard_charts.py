from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.task import Task
from datetime import datetime, timedelta
from sqlalchemy import func
from typing import List
from pydantic import BaseModel


router = APIRouter(prefix="/api/dashboard", tags=["Dashboard Charts"])


class TaskTrendData(BaseModel):
    date: str
    tasks_due: int


class MoraleData(BaseModel):
    positive: int
    neutral: int
    negative: int


@router.get("/task-trends", response_model=List[TaskTrendData])
def task_trends(days: int = 7, db: Session = Depends(get_db)):
    """Get task trends for the last N days"""
    today = datetime.utcnow()
    dates = [today - timedelta(days=i) for i in range(days)]
    trends = []
    
    for day in reversed(dates):
        count = db.query(Task).filter(
            func.date(Task.due_date) == day.date()
        ).count()
        
        trends.append({
            "date": day.strftime("%Y-%m-%d"),
            "tasks_due": count
        })
    
    return trends


@router.get("/team-morale", response_model=MoraleData)
def team_morale(db: Session = Depends(get_db)):
    """Get team morale statistics based on sentiment analysis"""
    # In production, fetch from actual sentiment data
    # For demo, return realistic mock data
    morale = {
        "positive": 65,
        "neutral": 25,
        "negative": 10
    }
    return morale


@router.get("/productivity-over-time")
def productivity_over_time(days: int = 30, db: Session = Depends(get_db)):
    """Get productivity score trends over time"""
    today = datetime.utcnow()
    dates = [today - timedelta(days=i) for i in range(days)]
    
    trends = []
    for day in reversed(dates):
        # Calculate completed tasks for that day
        completed = db.query(Task).filter(
            func.date(Task.updated_at) == day.date(),
            Task.status == "completed"
        ).count()
        
        trends.append({
            "date": day.strftime("%Y-%m-%d"),
            "completed_tasks": completed,
            "productivity_score": min(completed * 10, 100)  # Simple scoring
        })
    
    return {"trends": trends}


@router.get("/task-status-distribution")
def task_status_distribution(db: Session = Depends(get_db)):
    """Get distribution of tasks by status"""
    results = db.query(
        Task.status,
        func.count(Task.id).label("count")
    ).group_by(Task.status).all()
    
    return [{"status": r.status, "count": r.count} for r in results]


@router.get("/tasks-by-priority")
def tasks_by_priority(db: Session = Depends(get_db)):
    """Get task distribution by priority"""
    results = db.query(
        Task.priority,
        func.count(Task.id).label("count")
    ).group_by(Task.priority).all()
    
    return [{"priority": r.priority, "count": r.count} for r in results]
