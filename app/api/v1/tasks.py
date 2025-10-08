from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.task import Task, TaskStatus, GPSLog, Evidence, Review
from app.schemas.task import TaskCreate, GPSLogCreate, ReviewCreate
import datetime
import shutil
import os

router = APIRouter()

@router.post("/tasks")
def create_task(
    request: TaskCreate, db: Session = Depends(get_db)
):
    task = Task(**request.dict())
    db.add(task)
    db.commit()
    db.refresh(task)
    task_status = TaskStatus(task_id=task.id, status="Assigned")
    db.add(task_status)
    db.commit()
    return {"task_id": str(task.id)}

@router.post("/tasks/{task_id}/start")
def start_task(task_id: str, gps_data: GPSLogCreate, db: Session = Depends(get_db)):
    log = GPSLog(task_id=task_id, **gps_data.dict())
    db.add(log)
    db.add(TaskStatus(task_id=task_id, status="In Progress"))
    db.commit()
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
    return {"message": "Evidence uploaded"}

@router.post("/tasks/{task_id}/submit")
def submit_task(task_id: str, db: Session = Depends(get_db)):
    db.add(TaskStatus(task_id=task_id, status="Submitted"))
    db.commit()
    return {"message": "Task submitted for review"}

@router.post("/tasks/{task_id}/review")
def review_task(task_id: str, review: ReviewCreate, db: Session = Depends(get_db)):
    review_inst = Review(task_id=task_id, **review.dict())
    db.add(review_inst)
    db.add(TaskStatus(task_id=task_id, status=review.status))
    db.commit()
    return {"message": f"Task {review.status} by manager"}

@router.get("/tasks/{task_id}/lifecycle")
def get_task_lifecycle(task_id: str, db: Session = Depends(get_db)):
    status_history = db.query(TaskStatus).filter(TaskStatus.task_id == task_id).order_by(TaskStatus.created_at).all()
    return [{"status": item.status, "timestamp": item.created_at} for item in status_history]
