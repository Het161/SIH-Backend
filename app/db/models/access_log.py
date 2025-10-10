from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.session import Base


class APIAccessLog(Base):
    __tablename__ = "api_access_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_role = Column(String, index=True)
    path = Column(String, index=True)
    method = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
