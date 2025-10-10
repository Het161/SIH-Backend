from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from uuid import UUID

from app.db.session import get_db
from app.db.models.task import Task
from app.db.models.user import User
from app.ml.performance_predictor import PerformancePredictor

router = APIRouter(prefix="/api/predictions", tags=["ML Predictions"])
predictor = PerformancePredictor()

class DelayPredictionResponse(BaseModel):
    task_id: str
    delay_risk_score: float
    risk_level: str
    predicted_completion_delay_days: int
    recommendations: List[str]

class BurnoutPredictionResponse(BaseModel):
    user_id: str
    burnout_risk_score: float
    risk_level: str
    contributing_factors: List[str]
    recommendations: List[str]

class PerformanceForecastResponse(BaseModel):
    department_id: Optional[int]
    forecast_period_days: int
    predicted_completion_rate: float
    predicted_avg_delay_hours: float
    trend: str

@router.post("/task-delay-risk/{task_id}", response_model=DelayPredictionResponse)
async def predict_task_delay_risk(task_id: str, db: Session = Depends(get_db)):
    """Predict delay risk for a specific task using ML model"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    prediction = predictor.predict_task_delay(db, task_id)
    
    if prediction is None:
        raise HTTPException(status_code=400, detail="Insufficient data to make prediction")
    
    return prediction

@router.post("/user-burnout-risk/{user_id}", response_model=BurnoutPredictionResponse)
async def predict_user_burnout(user_id: str, db: Session = Depends(get_db)):
    """Predict burnout risk for a user based on workload patterns"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    prediction = predictor.predict_user_burnout(db, user_id)
    
    if prediction is None:
        raise HTTPException(status_code=400, detail="Insufficient user task history for prediction")
    
    return prediction

@router.get("/performance-forecast", response_model=PerformanceForecastResponse)
async def forecast_department_performance(department_id: Optional[int] = None, forecast_days: int = 30, db: Session = Depends(get_db)):
    """Forecast department or organization-wide performance trends"""
    forecast = predictor.forecast_performance(db, department_id=department_id, days_ahead=forecast_days)
    return forecast

@router.post("/train-model")
async def train_prediction_model(db: Session = Depends(get_db)):
    """Train/retrain the ML model with latest task data"""
    try:
        metrics = predictor.train_model(db)
        return {"status": "success", "message": "Model trained successfully", "metrics": metrics, "timestamp": datetime.utcnow()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model training failed: {str(e)}")

@router.get("/model-info")
async def get_model_info():
    """Get information about the current ML model"""
    return predictor.get_model_info()
