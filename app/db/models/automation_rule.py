from sqlalchemy import Column, Integer, String, Boolean, JSON
from app.db.session import Base


class AutomationRule(Base):
    __tablename__ = "automation_rules"
    __table_args__ = {'extend_existing': True} 
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    trigger_event = Column(String, nullable=False)  # e.g., "task_overdue", "burnout_detected"
    action = Column(String, nullable=False)  # e.g., "send_email", "escalate", "blockchain_log"
    parameters = Column(JSON)  # JSON object for flexible configuration
    is_active = Column(Boolean, default=True)
