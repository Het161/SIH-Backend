from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from app.db.session import Base
import datetime

class ProductivityScore(Base):
    __tablename__ = "productivity_scores"
    __table_args__ = {'extend_existing': True} 
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))  # ✅ Changed from UUID to Integer
    score = Column(Float)
    total_tasks = Column(Integer)
    completed_tasks = Column(Integer)
    on_time_tasks = Column(Integer)
    overdue_tasks = Column(Integer)
    avg_completion_time = Column(Float)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    calculated_at = Column(DateTime, default=datetime.datetime.utcnow)

