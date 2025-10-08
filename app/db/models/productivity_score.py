import uuid
import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base

class ProductivityScore(Base):
    __tablename__ = "productivity_scores"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    score = Column(Float)
    total_tasks = Column(Integer)
    completed_tasks = Column(Integer)
    on_time_tasks = Column(Integer)
    overdue_tasks = Column(Integer)
    avg_completion_time = Column(Float)  # in hours
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    calculated_at = Column(DateTime, default=datetime.datetime.utcnow)
