from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.automation_rule import AutomationRule
from pydantic import BaseModel
from typing import Optional, Dict, Any, List


router = APIRouter(prefix="/api/automation", tags=["Workflow Automation"])


class RuleCreateRequest(BaseModel):
    name: str
    trigger_event: str
    action: str
    parameters: Optional[Dict[str, Any]] = None


class RuleResponse(BaseModel):
    id: int
    name: str
    trigger_event: str
    action: str
    parameters: Optional[Dict[str, Any]]
    is_active: bool

    class Config:
        from_attributes = True


@router.post("/create", response_model=RuleResponse)
def create_rule(request: RuleCreateRequest, db: Session = Depends(get_db)):
    """Create a new automation rule"""
    # Check if rule with same name already exists
    existing = db.query(AutomationRule).filter(AutomationRule.name == request.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Rule with this name already exists")
    
    rule = AutomationRule(**request.dict())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.get("/list", response_model=List[RuleResponse])
def list_rules(db: Session = Depends(get_db)):
    """List all automation rules"""
    rules = db.query(AutomationRule).all()
    return rules


@router.get("/run/{event_name}")
def run_rules(event_name: str, db: Session = Depends(get_db)):
    """Trigger all active rules for a given event"""
    rules = (
        db.query(AutomationRule)
        .filter(
            AutomationRule.trigger_event == event_name,
            AutomationRule.is_active == True
        )
        .all()
    )
    
    triggered = []
    for rule in rules:
        # Execute action logic based on rule.action
        if rule.action == "send_email":
            # Call email notification service
            pass
        elif rule.action == "blockchain_log":
            # Log to blockchain
            pass
        elif rule.action == "escalate":
            # Escalate task to manager
            pass
        
        triggered.append(rule.name)
    
    return {
        "event": event_name,
        "triggered_rules": triggered,
        "count": len(triggered)
    }


@router.delete("/delete/{rule_id}")
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    """Delete an automation rule"""
    rule = db.query(AutomationRule).filter(AutomationRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    db.delete(rule)
    db.commit()
    return {"message": f"Rule '{rule.name}' deleted successfully"}
