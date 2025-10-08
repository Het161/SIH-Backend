from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import shutil
import os
import datetime
from app.schemas.task import TaskCreate, GPSLogCreate, ReviewCreate
from app.db.session import get_db
from app.db.models.task import Task, TaskStatus, GPSLog, Evidence, Review
from app.utils.audit import log_action

router = APIRouter()

# Pydantic model for bulk task creation
class BulkTaskCreate(BaseModel):
    title: str
    description: str
    assigned_to_list: List[str]
    assigned_by: str
    due_date: datetime.datetime


@router.post("/tasks")
def create_task(request: TaskCreate, db: Session = Depends(get_db)):
    task = Task(**request.dict())
    db.add(task)
    db.commit()
    db.refresh(task)
    
    db.add(TaskStatus(task_id=task.id, status="Assigned"))
    db.commit()
    
    # Log the action
    log_action(
        db=db,
        user_id=str(request.assigned_by),
        action="CREATE_TASK",
        resource_type="task",
        resource_id=str(task.id),
        details={
            "title": task.title,
            "assigned_to": str(task.assigned_to),
            "due_date": str(task.due_date)
        }
    )
    
    return {"task_id": str(task.id)}


@router.post("/tasks/bulk")
def create_bulk_tasks(request: BulkTaskCreate, db: Session = Depends(get_db)):
    """Create multiple tasks - same task assigned to multiple users"""
    created_tasks = []
    
    for user_id in request.assigned_to_list:
        task = Task(
            title=request.title,
            description=request.description,
            assigned_to=user_id,
            assigned_by=request.assigned_by,
            due_date=request.due_date
        )
        db.add(task)
        db.flush()
        db.add(TaskStatus(task_id=task.id, status="Assigned"))
        log_action(
            db=db, 
            user_id=str(request.assigned_by), 
            action="BULK_CREATE_TASK", 
            resource_type="task", 
            resource_id=str(task.id), 
            details={"title": task.title, "assigned_to": str(user_id)}
        )
        created_tasks.append(str(task.id))
    
    db.commit()
    return {"message": f"Created {len(created_tasks)} tasks", "task_ids": created_tasks}


@router.post("/tasks/{task_id}/start")
def start_task(task_id: str, gps: GPSLogCreate, db: Session = Depends(get_db)):
    log = GPSLog(task_id=task_id, **gps.dict())
    db.add(log)
    db.add(TaskStatus(task_id=task_id, status="In Progress"))
    db.commit()
    
    # Log the action
    log_action(
        db=db,
        user_id=str(gps.user_id),
        action="START_TASK",
        resource_type="task",
        resource_id=task_id,
        details={
            "latitude": float(gps.latitude),
            "longitude": float(gps.longitude)
        }
    )
    
    return {"message": "Started with GPS logged"}


@router.post("/tasks/{task_id}/evidence")
def upload_evidence(task_id: str, user_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_location = f"{upload_dir}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    evidence = Evidence(task_id=task_id, user_id=user_id, file_path=file_location)
    db.add(evidence)
    db.commit()
    
    # Log the action
    log_action(
        db=db,
        user_id=user_id,
        action="UPLOAD_EVIDENCE",
        resource_type="task",
        resource_id=task_id,
        details={
            "filename": file.filename,
            "file_path": file_location
        }
    )
    
    return {"message": "Evidence uploaded"}


@router.post("/tasks/{task_id}/submit")
def submit_task(task_id: str, user_id: str, db: Session = Depends(get_db)):
    db.add(TaskStatus(task_id=task_id, status="Submitted"))
    db.commit()
    
    # Log the action
    log_action(
        db=db,
        user_id=user_id,
        action="SUBMIT_TASK",
        resource_type="task",
        resource_id=task_id,
        details={"status": "Submitted"}
    )
    
    return {"message": "Task submitted for review"}


@router.post("/tasks/{task_id}/review")
def review_task(task_id: str, review: ReviewCreate, db: Session = Depends(get_db)):
    db.add(Review(task_id=task_id, **review.dict()))
    db.add(TaskStatus(task_id=task_id, status=review.status))
    db.commit()
    
    # Log the action
    log_action(
        db=db,
        user_id=str(review.manager_id),
        action="REVIEW_TASK",
        resource_type="task",
        resource_id=task_id,
        details={
            "status": review.status,
            "feedback": review.feedback
        }
    )
    
    return {"message": f"Task {review.status} by manager"}


@router.get("/tasks/{task_id}/lifecycle")
def get_task_lifecycle(task_id: str, db: Session = Depends(get_db)):
    status_history = db.query(TaskStatus).filter(TaskStatus.task_id == task_id).order_by(TaskStatus.created_at).all()
    return [{"status": item.status, "timestamp": item.created_at} for item in status_history]


@router.get("/tasks/search")
def search_tasks(
    status: Optional[str] = None,
    assigned_to: Optional[str] = None,
    assigned_by: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(50, le=100),
    skip: int = 0,
    db: Session = Depends(get_db)
):
    """Search and filter tasks with multiple criteria"""
    
    query = db.query(Task)
    
    # Filter by assigned user
    if assigned_to:
        query = query.filter(Task.assigned_to == assigned_to)
    
    # Filter by manager
    if assigned_by:
        query = query.filter(Task.assigned_by == assigned_by)
    
    # Filter by date range
    if from_date:
        query = query.filter(Task.created_at >= from_date)
    if to_date:
        query = query.filter(Task.created_at <= to_date)
    
    # Search in title/description
    if search:
        query = query.filter(
            (Task.title.ilike(f"%{search}%")) | 
            (Task.description.ilike(f"%{search}%"))
        )
    
    # Filter by status (join with latest TaskStatus)
    if status:
        latest_status = db.query(
            TaskStatus.task_id
        ).filter(
            TaskStatus.status == status
        ).distinct().subquery()
        
        query = query.filter(Task.id.in_(latest_status))
    
    tasks = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "assigned_to": str(task.assigned_to),
            "assigned_by": str(task.assigned_by),
            "due_date": task.due_date,
            "created_at": task.created_at
        }
        for task in tasks
    ]
