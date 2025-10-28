from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime
from app.db.session import Base

class BlockchainAudit(Base):
    __tablename__ = "blockchain_audit"
    __table_args__ = {'extend_existing': True} 
    
    id = Column(Integer, primary_key=True, index=True)
    block_hash = Column(String(64), unique=True, nullable=False, index=True)
    previous_hash = Column(String(64), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    action = Column(String(100), nullable=False)
    user_id = Column(Integer, nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    details = Column(JSON, nullable=True)
    proof = Column(Text, nullable=False)
    nonce = Column(Integer, default=0, nullable=False)
