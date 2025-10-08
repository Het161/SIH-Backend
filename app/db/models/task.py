import uuid
import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base

class Task(Base):
    __tablename__ = "tasks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(100))
    description = Column(Text)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    due_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

class TaskStatus(Base):
    __tablename__ = "task_statuses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"))
    status = Column(String(20))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class GPSLog(Base):
    __tablename__ = "gps_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    latitude = Column(Numeric)
    longitude = Column(Numeric)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    file_path = Column(Text)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"))
    manager_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    status = Column(String(10))
    feedback = Column(Text)
    reviewed_at = Column(DateTime, default=datetime.datetime.utcnow)
