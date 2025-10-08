from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.db.session import get_db
from app.db.models.task import Task, TaskStatus, Review
from app.db.models.user import User
from app.schemas.analytics import UserProductivity, TeamProductivity, OrganizationMetrics, SLABreach
import datetime

router = APIRouter()

@router.get("/analytics/user/{user_id}")
def get_user_productivity(user_id: str, db: Session = Depends(get_db)):
    """Get productivity metrics for a specific user"""
    
    # Get user info
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get all tasks assigned to user
    total_tasks = db.query(Task).filter(Task.assigned_to == user_id).count()
    
    # Get completed tasks (Approved status)
    completed_tasks = db.query(Task).join(Review).filter(
        Task.assigned_to == user_id,
        Review.status == "Approved"
    ).count()
    
    # Get on-time tasks (completed before due date)
    on_time_tasks = db.query(Task).join(Review).filter(
        Task.assigned_to == user_id,
        Review.status == "Approved",
        Review.reviewed_at <= Task.due_date
    ).count()
    
    # Get overdue tasks
    overdue_tasks = db.query(Task).filter(
        Task.assigned_to == user_id,
        Task.due_date < datetime.datetime.utcnow()
    ).filter(
        ~Task.id.in_(
            db.query(Review.task_id).filter(Review.status == "Approved")
        )
    ).count()
    
    # Calculate average completion time
    avg_time_query = db.query(
        func.avg(
            func.extract('epoch', Review.reviewed_at - Task.created_at) / 3600
        )
    ).join(Task).filter(
        Task.assigned_to == user_id,
        Review.status == "Approved"
    ).scalar()
    
    avg_completion_time = round(avg_time_query, 2) if avg_time_query else 0
    
    # Calculate productivity score (0-100)
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    on_time_rate = (on_time_tasks / completed_tasks * 100) if completed_tasks > 0 else 0
    score = (completion_rate * 0.6 + on_time_rate * 0.4)
    
    return UserProductivity(
        user_id=str(user.id),
        user_name=user.name,
        score=round(score, 2),
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        on_time_tasks=on_time_tasks,
        overdue_tasks=overdue_tasks,
        avg_completion_time=avg_completion_time,
        completion_rate=round(completion_rate, 2)
    )

@router.get("/analytics/team/{department}")
def get_team_productivity(department: str, db: Session = Depends(get_db)):
    """Get productivity metrics for a department/team"""
    
    # Get all users in department
    users = db.query(User).filter(User.department == department).all()
    if not users:
        raise HTTPException(status_code=404, detail="Department not found")
    
    user_ids = [str(u.id) for u in users]
    
    # Aggregate metrics
    total_tasks = db.query(Task).filter(Task.assigned_to.in_(user_ids)).count()
    completed_tasks = db.query(Task).join(Review).filter(
        Task.assigned_to.in_(user_ids),
        Review.status == "Approved"
    ).count()
    
    # Calculate team average score
    team_scores = []
    for user_id in user_ids:
        user_data = get_user_productivity(user_id, db)
        team_scores.append(user_data.score)
    
    avg_score = sum(team_scores) / len(team_scores) if team_scores else 0
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return TeamProductivity(
        department=department,
        total_employees=len(users),
        avg_score=round(avg_score, 2),
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        team_completion_rate=round(completion_rate, 2)
    )

@router.get("/analytics/organization")
def get_organization_metrics(db: Session = Depends(get_db)):
    """Get organization-wide productivity metrics"""
    
    total_employees = db.query(User).count()
    total_tasks = db.query(Task).count()
    completed_tasks = db.query(Task).join(Review).filter(
        Review.status == "Approved"
    ).count()
    
    # Get overdue tasks
    total_overdue = db.query(Task).filter(
        Task.due_date < datetime.datetime.utcnow()
    ).filter(
        ~Task.id.in_(
            db.query(Review.task_id).filter(Review.status == "Approved")
        )
    ).count()
    
    # Get department list with stats
    departments = db.query(User.department).distinct().all()
    dept_list = [dept[0] for dept in departments if dept[0]]
    
    # Calculate average productivity score across organization
    all_users = db.query(User).all()
    all_scores = []
    for user in all_users:
        try:
            user_data = get_user_productivity(str(user.id), db)
            all_scores.append(user_data.score)
        except:
            pass
    
    avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
    
    return OrganizationMetrics(
        total_employees=total_employees,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        avg_productivity_score=round(avg_score, 2),
        total_overdue=total_overdue,
        departments=dept_list
    )

@router.get("/analytics/sla-breaches")
def get_sla_breaches(db: Session = Depends(get_db)):
    """Get all tasks that are overdue (SLA breaches)"""
    
    # Get overdue tasks
    overdue_tasks = db.query(Task, User).join(
        User, Task.assigned_to == User.id
    ).filter(
        Task.due_date < datetime.datetime.utcnow()
    ).filter(
        ~Task.id.in_(
            db.query(Review.task_id).filter(Review.status == "Approved")
        )
    ).all()
    
    breaches = []
    for task, user in overdue_tasks:
        days_overdue = (datetime.datetime.utcnow() - task.due_date).days
        
        # Get current status
        latest_status = db.query(TaskStatus).filter(
            TaskStatus.task_id == task.id
        ).order_by(TaskStatus.created_at.desc()).first()
        
        breaches.append(SLABreach(
            task_id=str(task.id),
            title=task.title,
            assigned_to=str(user.id),
            assigned_to_name=user.name,
            due_date=task.due_date,
            days_overdue=days_overdue,
            status=latest_status.status if latest_status else "Unknown"
        ))
    
    return breaches
