from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.db.session import get_db
from app.blockchain.audit_chain import BlockchainAudit

router = APIRouter(prefix="/api/blockchain", tags=["Blockchain Audit"])
blockchain = BlockchainAudit()

class AuditLogRequest(BaseModel):
    action: str
    user_id: int
    entity_type: str
    entity_id: int
    details: Optional[dict] = None

class AuditLogResponse(BaseModel):
    block_hash: str
    previous_hash: str
    timestamp: datetime
    action: str
    user_id: int
    entity_type: str
    entity_id: int
    details: Optional[dict]
    proof_of_integrity: str

class VerificationResponse(BaseModel):
    is_valid: bool
    block_hash: str
    verification_timestamp: datetime
    message: str

class ChainIntegrityResponse(BaseModel):
    is_valid: bool
    total_blocks: int
    verification_timestamp: datetime
    compromised_blocks: List[str]

@router.post("/log-action", response_model=AuditLogResponse)
async def log_audit_action(audit_data: AuditLogRequest, db: Session = Depends(get_db)):
    block = blockchain.add_block(db=db, action=audit_data.action, user_id=audit_data.user_id, entity_type=audit_data.entity_type, entity_id=audit_data.entity_id, details=audit_data.details)
    return {"block_hash": block.block_hash, "previous_hash": block.previous_hash, "timestamp": block.timestamp, "action": block.action, "user_id": block.user_id, "entity_type": block.entity_type, "entity_id": block.entity_id, "details": block.details, "proof_of_integrity": block.proof}

@router.get("/verify-block/{block_hash}", response_model=VerificationResponse)
async def verify_block(block_hash: str, db: Session = Depends(get_db)):
    is_valid = blockchain.verify_block(db, block_hash)
    return {"is_valid": is_valid, "block_hash": block_hash, "verification_timestamp": datetime.utcnow(), "message": "Block is valid and untampered" if is_valid else "Block integrity compromised"}

@router.get("/verify-chain", response_model=ChainIntegrityResponse)
async def verify_entire_chain(db: Session = Depends(get_db)):
    result = blockchain.verify_chain(db)
    return {"is_valid": result["is_valid"], "total_blocks": result["total_blocks"], "verification_timestamp": datetime.utcnow(), "compromised_blocks": result.get("compromised_blocks", [])}

@router.get("/audit-trail/{entity_type}/{entity_id}")
async def get_entity_audit_trail(entity_type: str, entity_id: int, db: Session = Depends(get_db)):
    trail = blockchain.get_audit_trail(db, entity_type=entity_type, entity_id=entity_id)
    return {"entity_type": entity_type, "entity_id": entity_id, "total_records": len(trail), "audit_trail": trail}

@router.get("/user-actions/{user_id}")
async def get_user_action_history(user_id: int, limit: Optional[int] = 100, db: Session = Depends(get_db)):
    actions = blockchain.get_user_actions(db, user_id=user_id, limit=limit)
    return {"user_id": user_id, "action_count": len(actions), "actions": actions}

@router.get("/recent-audits")
async def get_recent_audit_logs(limit: int = 50, db: Session = Depends(get_db)):
    recent_logs = blockchain.get_recent_logs(db, limit=limit)
    return {"count": len(recent_logs), "logs": recent_logs}

@router.get("/chain-stats")
async def get_blockchain_statistics(db: Session = Depends(get_db)):
    stats = blockchain.get_chain_statistics(db)
    return stats
