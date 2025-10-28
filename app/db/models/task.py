from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Numeric
from sqlalchemy.sql import func
from app.db.session import Base
import datetime


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = {'extend_existing': True} 
    
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    assigned_to = Column(Integer, ForeignKey("users.id"))
    assigned_by = Column(Integer, ForeignKey("users.id"))
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    due_date = Column(DateTime)
    priority = Column(String(20))
    status = Column(String(20))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)


class TaskStatus(Base):
    __tablename__ = "task_statuses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))  # ✅ Changed from UUID to Integer
    status = Column(String(20))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class GPSLog(Base):
    __tablename__ = "gps_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))  # ✅ Changed from UUID to Integer
    user_id = Column(Integer, ForeignKey("users.id"))  # ✅ Changed from UUID to Integer
    latitude = Column(Numeric)
    longitude = Column(Numeric)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)


class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))  # ✅ Changed from UUID to Integer
    user_id = Column(Integer, ForeignKey("users.id"))  # ✅ Changed from UUID to Integer
    file_path = Column(Text)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)


class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))  # ✅ Changed from UUID to Integer
    manager_id = Column(Integer, ForeignKey("users.id"))  # ✅ Changed from UUID to Integer
    status = Column(String(10))
    feedback = Column(Text)
    reviewed_at = Column(DateTime, default=datetime.datetime.utcnow)

