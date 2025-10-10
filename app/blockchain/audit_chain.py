import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional

class BlockchainAudit:
    def __init__(self):
        self.difficulty = 2
    
    def add_block(self, db, action: str, user_id: int, entity_type: str, entity_id: int, details: Optional[Dict]) -> object:
        """Add a new block to the blockchain"""
        from app.db.models.blockchain_audit import BlockchainAudit as BlockModel
        
        # Get previous hash
        last_block = db.query(BlockModel).order_by(BlockModel.id.desc()).first()
        previous_hash = last_block.block_hash if last_block else "0" * 64
        
        # Create new block
        timestamp = datetime.utcnow()
        nonce = 0
        block_data = {
            "previous_hash": previous_hash,
            "timestamp": timestamp.isoformat(),
            "action": action,
            "user_id": user_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "details": details or {}
        }
        
        # Mine block
        block_hash = self._calculate_hash(block_data, nonce)
        while not block_hash.startswith("0" * self.difficulty):
            nonce += 1
            block_hash = self._calculate_hash(block_data, nonce)
        
        # Generate proof
        proof = self._generate_proof(block_hash, previous_hash)
        
        # Save to database
        new_block = BlockModel(
            block_hash=block_hash,
            previous_hash=previous_hash,
            timestamp=timestamp,
            action=action,
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            proof=proof,
            nonce=nonce
        )
        
        db.add(new_block)
        db.commit()
        db.refresh(new_block)
        
        return new_block
    
    def verify_block(self, db, block_hash: str) -> bool:
        """Verify a single block"""
        from app.db.models.blockchain_audit import BlockchainAudit as BlockModel
        
        block = db.query(BlockModel).filter(BlockModel.block_hash == block_hash).first()
        if not block:
            return False
        
        block_data = {
            "previous_hash": block.previous_hash,
            "timestamp": block.timestamp.isoformat(),
            "action": block.action,
            "user_id": block.user_id,
            "entity_type": block.entity_type,
            "entity_id": block.entity_id,
            "details": block.details or {}
        }
        
        calculated_hash = self._calculate_hash(block_data, block.nonce)
        return calculated_hash == block.block_hash
    
    def verify_chain(self, db) -> Dict:
        """Verify entire blockchain"""
        from app.db.models.blockchain_audit import BlockchainAudit as BlockModel
        
        blocks = db.query(BlockModel).order_by(BlockModel.id).all()
        
        if not blocks:
            return {"is_valid": True, "total_blocks": 0, "compromised_blocks": []}
        
        compromised = []
        for i, block in enumerate(blocks):
            if not self.verify_block(db, block.block_hash):
                compromised.append(block.block_hash)
            
            if i > 0 and block.previous_hash != blocks[i-1].block_hash:
                compromised.append(block.block_hash)
        
        return {
            "is_valid": len(compromised) == 0,
            "total_blocks": len(blocks),
            "compromised_blocks": compromised
        }
    
    def get_audit_trail(self, db, entity_type: str, entity_id: int) -> List[Dict]:
        """Get audit trail for entity"""
        from app.db.models.blockchain_audit import BlockchainAudit as BlockModel
        
        blocks = db.query(BlockModel).filter(
            BlockModel.entity_type == entity_type,
            BlockModel.entity_id == entity_id
        ).order_by(BlockModel.timestamp.desc()).all()
        
        return [self._block_to_dict(block) for block in blocks]
    
    def get_user_actions(self, db, user_id: int, limit: int) -> List[Dict]:
        """Get user action history"""
        from app.db.models.blockchain_audit import BlockchainAudit as BlockModel
        
        blocks = db.query(BlockModel).filter(
            BlockModel.user_id == user_id
        ).order_by(BlockModel.timestamp.desc()).limit(limit).all()
        
        return [self._block_to_dict(block) for block in blocks]
    
    def get_recent_logs(self, db, limit: int) -> List[Dict]:
        """Get recent audit logs"""
        from app.db.models.blockchain_audit import BlockchainAudit as BlockModel
        
        blocks = db.query(BlockModel).order_by(BlockModel.timestamp.desc()).limit(limit).all()
        return [self._block_to_dict(block) for block in blocks]
    
    def get_chain_statistics(self, db) -> Dict:
        """Get blockchain statistics"""
        from app.db.models.blockchain_audit import BlockchainAudit as BlockModel
        
        total_blocks = db.query(BlockModel).count()
        verification_result = self.verify_chain(db)
        
        return {
            "total_blocks": total_blocks,
            "chain_valid": verification_result["is_valid"],
            "difficulty": self.difficulty,
            "last_block_time": db.query(BlockModel).order_by(BlockModel.timestamp.desc()).first().timestamp.isoformat() if total_blocks > 0 else None
        }
    
    def _calculate_hash(self, block_data: Dict, nonce: int) -> str:
        """Calculate block hash"""
        block_string = json.dumps({**block_data, "nonce": nonce}, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def _generate_proof(self, block_hash: str, previous_hash: str) -> str:
        """Generate cryptographic proof"""
        proof_string = f"{block_hash}:{previous_hash}"
        return hashlib.sha256(proof_string.encode()).hexdigest()
    
    def _block_to_dict(self, block) -> Dict:
        """Convert block model to dictionary"""
        return {
            "id": block.id,
            "block_hash": block.block_hash,
            "previous_hash": block.previous_hash,
            "timestamp": block.timestamp.isoformat(),
            "action": block.action,
            "user_id": block.user_id,
            "entity_type": block.entity_type,
            "entity_id": block.entity_id,
            "details": block.details,
            "proof": block.proof
        }
