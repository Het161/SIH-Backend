from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.task import Task
import csv
from io import StringIO
from datetime import datetime


router = APIRouter(prefix="/api/data", tags=["Data Transfer"])


@router.post("/import")
async def import_tasks(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Import tasks from CSV file"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    try:
        content = await file.read()
        csv_content = StringIO(content.decode('utf-8'))
        reader = csv.DictReader(csv_content)
        
        imported_count = 0
        for row in reader:
            task = Task(
                title=row.get("title"),
                description=row.get("description", ""),
                assigned_to=row.get("assigned_to"),
                due_date=datetime.fromisoformat(row.get("due_date")) if row.get("due_date") else None,
                priority=row.get("priority", "medium"),
                status=row.get("status", "pending")
            )
            db.add(task)
            imported_count += 1
        
        db.commit()
        return {
            "message": "Tasks imported successfully",
            "count": imported_count
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")


@router.get("/export")
def export_tasks(db: Session = Depends(get_db)):
    """Export all tasks to CSV file"""
    tasks = db.query(Task).all()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(["id", "title", "description", "assigned_to", "due_date", "priority", "status", "created_at"])
    
    # Write data
    for task in tasks:
        writer.writerow([
            str(task.id),
            task.title,
            task.description,
            str(task.assigned_to),
            task.due_date.isoformat() if task.due_date else "",
            task.priority,
            task.status,
            task.created_at.isoformat() if hasattr(task, 'created_at') else ""
        ])
    
    csv_data = output.getvalue()
    
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=tasks_export.csv"
        }
    )


@router.get("/export-audit-logs")
def export_audit_logs(db: Session = Depends(get_db)):
    """Export audit logs to CSV"""
    from app.db.models.audit_log import AuditLog
    
    logs = db.query(AuditLog).all()
    
    output = StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["id", "user_id", "action", "resource_type", "resource_id", "timestamp"])
    
    for log in logs:
        writer.writerow([
            log.id,
            str(log.user_id),
            log.action,
            log.resource_type,
            log.resource_id,
            log.timestamp.isoformat()
        ])
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_logs.csv"}
    )
