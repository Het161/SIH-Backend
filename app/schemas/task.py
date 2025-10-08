from pydantic import BaseModel
import datetime

class TaskCreate(BaseModel):
    title: str
    description: str
    assigned_to: str
    assigned_by: str
    due_date: datetime.datetime

class TaskStatusUpdate(BaseModel):
    status: str

class GPSLogCreate(BaseModel):
    user_id: str
    latitude: float
    longitude: float

class EvidenceCreate(BaseModel):
    user_id: str

class ReviewCreate(BaseModel):
    manager_id: str
    status: str
    feedback: str
