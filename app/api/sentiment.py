from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.db.session import get_db
from app.db.models.task import Task
from app.models.user import User
from app.ml.sentiment_analyzer import SentimentAnalyzer

router = APIRouter(prefix="/api/sentiment", tags=["Sentiment Analysis"])
analyzer = SentimentAnalyzer()

class SentimentResponse(BaseModel):
    text: str
    sentiment: str
    confidence: float
    scores: dict

class TaskSentimentResponse(BaseModel):
    task_id: int
    overall_sentiment: str
    average_confidence: float
    comment_count: int
    sentiment_breakdown: dict

class TeamMoraleResponse(BaseModel):
    department_id: Optional[int]
    overall_morale: str
    morale_score: float
    positive_percentage: float
    negative_percentage: float
    neutral_percentage: float
    trend: str
    alert_level: str

class UserSentimentTimelineResponse(BaseModel):
    user_id: int
    timeline: List[dict]
    burnout_indicators: List[str]

@router.post("/analyze-text", response_model=SentimentResponse)
async def analyze_text_sentiment(text: str):
    if not text or len(text.strip()) < 3:
        raise HTTPException(status_code=400, detail="Text must be at least 3 characters long")
    result = analyzer.analyze_text(text)
    return result

@router.get("/task-sentiment/{task_id}", response_model=TaskSentimentResponse)
async def get_task_sentiment(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    sentiment_data = analyzer.analyze_task_comments(db, task_id)
    if sentiment_data is None:
        raise HTTPException(status_code=400, detail="No comments found for this task")
    return sentiment_data

@router.get("/team-morale", response_model=TeamMoraleResponse)
async def get_team_morale(department_id: Optional[int] = None, days: int = 30, db: Session = Depends(get_db)):
    morale_data = analyzer.analyze_team_morale(db, department_id=department_id, days_back=days)
    return morale_data

@router.get("/user-sentiment-timeline/{user_id}", response_model=UserSentimentTimelineResponse)
async def get_user_sentiment_timeline(user_id: int, days: int = 90, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    timeline_data = analyzer.get_user_sentiment_timeline(db, user_id=user_id, days_back=days)
    return timeline_data

@router.get("/burnout-alerts")
async def get_burnout_alerts(threshold: float = 0.7, db: Session = Depends(get_db)):
    alerts = analyzer.detect_burnout_signals(db, threshold=threshold)
    return {"alert_count": len(alerts), "alerts": alerts, "timestamp": datetime.utcnow()}
