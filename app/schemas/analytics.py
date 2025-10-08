from pydantic import BaseModel
from typing import Optional
import datetime

class UserProductivity(BaseModel):
    user_id: str
    user_name: str
    score: float
    total_tasks: int
    completed_tasks: int
    on_time_tasks: int
    overdue_tasks: int
    avg_completion_time: float
    completion_rate: float

class TeamProductivity(BaseModel):
    department: str
    total_employees: int
    avg_score: float
    total_tasks: int
    completed_tasks: int
    team_completion_rate: float

class OrganizationMetrics(BaseModel):
    total_employees: int
    total_tasks: int
    completed_tasks: int
    avg_productivity_score: float
    total_overdue: int
    departments: list

class SLABreach(BaseModel):
    task_id: str
    title: str
    assigned_to: str
    assigned_to_name: str
    due_date: datetime.datetime
    days_overdue: int
    status: str
