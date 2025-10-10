import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import joblib
import os

class PerformancePredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = "app/ml/models/performance_model.pkl"
        self.scaler_path = "app/ml/models/scaler.pkl"
        self._load_model()
    
    def _load_model(self):
        """Load pre-trained model if exists"""
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
    
    def _save_model(self):
        """Save trained model"""
        os.makedirs("app/ml/models", exist_ok=True)
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
    
    def predict_task_delay(self, db, task_id: int) -> Optional[Dict]:
        """Predict if a task will be delayed"""
        from app.db.models.task import Task
        
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None
        
        # Extract features from task
        features = self._extract_task_features(db, task)
        if features is None:
            return None
        
        # If model not trained, use rule-based prediction
        if self.model is None:
            return self._rule_based_delay_prediction(task, features)
        
        # ML-based prediction
        X = np.array([features]).reshape(1, -1)
        X_scaled = self.scaler.transform(X)
        delay_prob = self.model.predict_proba(X_scaled)[0][1]
        
        risk_level = "high" if delay_prob > 0.7 else "medium" if delay_prob > 0.4 else "low"
        delay_days = int(delay_prob * 10)
        
        recommendations = self._generate_recommendations(delay_prob, task)
        
        return {
            "task_id": task_id,
            "delay_risk_score": round(delay_prob, 3),
            "risk_level": risk_level,
            "predicted_completion_delay_days": delay_days,
            "recommendations": recommendations
        }
    
    def predict_user_burnout(self, db, user_id: int) -> Optional[Dict]:
        """Predict user burnout risk"""
        from app.db.models.task import Task
        
        # Get user's recent tasks
        recent_tasks = db.query(Task).filter(
            Task.assigned_to == user_id,
            Task.created_at >= datetime.utcnow() - timedelta(days=30)
        ).all()
        
        if len(recent_tasks) < 3:
            return None
        
        # Calculate burnout indicators
        total_tasks = len(recent_tasks)
        overdue_tasks = sum(1 for t in recent_tasks if t.status == 'overdue')
        avg_completion_time = np.mean([
            (t.completed_at - t.created_at).days 
            for t in recent_tasks if t.completed_at
        ]) if any(t.completed_at for t in recent_tasks) else 7
        
        # Burnout score calculation
        burnout_score = min(1.0, (
            (overdue_tasks / total_tasks * 0.4) +
            (min(total_tasks / 20, 1.0) * 0.3) +
            (min(avg_completion_time / 14, 1.0) * 0.3)
        ))
        
        risk_level = "high" if burnout_score > 0.7 else "medium" if burnout_score > 0.4 else "low"
        
        factors = []
        if overdue_tasks / total_tasks > 0.3:
            factors.append(f"High overdue rate: {overdue_tasks}/{total_tasks} tasks")
        if total_tasks > 15:
            factors.append(f"Heavy workload: {total_tasks} tasks in 30 days")
        if avg_completion_time > 10:
            factors.append(f"Slow completion: avg {avg_completion_time:.1f} days")
        
        recommendations = self._generate_burnout_recommendations(burnout_score, factors)
        
        return {
            "user_id": user_id,
            "burnout_risk_score": round(burnout_score, 3),
            "risk_level": risk_level,
            "contributing_factors": factors,
            "recommendations": recommendations
        }
    
    def forecast_performance(self, db, department_id: Optional[int] = None, days_ahead: int = 30) -> Dict:
        """Forecast department performance"""
        from app.db.models.task import Task
        
        query = db.query(Task).filter(
            Task.created_at >= datetime.utcnow() - timedelta(days=90)
        )
        
        if department_id:
            query = query.filter(Task.department_id == department_id)
        
        tasks = query.all()
        
        if len(tasks) < 10:
            return {
                "department_id": department_id,
                "forecast_period_days": days_ahead,
                "predicted_completion_rate": 0.75,
                "predicted_avg_delay_hours": 48.0,
                "trend": "insufficient_data"
            }
        
        # Calculate metrics
        completed_tasks = [t for t in tasks if t.status == 'completed']
        completion_rate = len(completed_tasks) / len(tasks)
        
        delays = [
            (t.completed_at - t.due_date).total_seconds() / 3600
            for t in completed_tasks if t.completed_at and t.due_date and t.completed_at > t.due_date
        ]
        avg_delay = np.mean(delays) if delays else 0
        
        # Trend analysis
        recent_rate = len([t for t in tasks[-30:] if t.status == 'completed']) / min(30, len(tasks))
        trend = "improving" if recent_rate > completion_rate else "declining" if recent_rate < completion_rate - 0.05 else "stable"
        
        return {
            "department_id": department_id,
            "forecast_period_days": days_ahead,
            "predicted_completion_rate": round(completion_rate, 3),
            "predicted_avg_delay_hours": round(avg_delay, 2),
            "trend": trend
        }
    
    def train_model(self, db) -> Dict:
        """Train the ML model with historical data"""
        from app.db.models.task import Task
        
        # Get historical tasks
        tasks = db.query(Task).filter(Task.completed_at.isnot(None)).all()
        
        if len(tasks) < 50:
            return {
                "status": "insufficient_data",
                "message": "Need at least 50 completed tasks to train model",
                "current_count": len(tasks)
            }
        
        # Prepare training data
        X, y = [], []
        for task in tasks:
            features = self._extract_task_features(db, task)
            if features is not None:
                X.append(features)
                is_delayed = 1 if (task.completed_at and task.due_date and task.completed_at > task.due_date) else 0
                y.append(is_delayed)
        
        X = np.array(X)
        y = np.array(y)
        
        # Train model
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_scaled, y)
        
        # Save model
        self._save_model()
        
        accuracy = self.model.score(X_scaled, y)
        
        return {
            "accuracy": round(accuracy, 3),
            "samples_trained": len(X),
            "model_type": "RandomForestClassifier",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_model_info(self) -> Dict:
        """Get model information"""
        return {
            "model_loaded": self.model is not None,
            "model_type": "RandomForestClassifier" if self.model else "Rule-based",
            "model_path": self.model_path,
            "last_updated": datetime.fromtimestamp(os.path.getmtime(self.model_path)).isoformat() if os.path.exists(self.model_path) else None
        }
    
    def _extract_task_features(self, db, task) -> Optional[List[float]]:
        """Extract numerical features from task"""
        try:
            priority_map = {"low": 1, "medium": 2, "high": 3, "critical": 4}
            priority = priority_map.get(task.priority, 2)
            
            days_since_creation = (datetime.utcnow() - task.created_at).days
            
            # User workload
            from app.db.models.task import Task
            user_active_tasks = db.query(Task).filter(
                Task.assigned_to == task.assigned_to,
                Task.status.in_(['pending', 'in_progress'])
            ).count()
            
            return [priority, days_since_creation, user_active_tasks]
        except:
            return None
    
    def _rule_based_delay_prediction(self, task, features) -> Dict:
        """Fallback rule-based prediction"""
        priority, days_since, workload = features
        
        delay_score = min(1.0, (
            (priority / 4 * 0.3) +
            (min(days_since / 30, 1) * 0.4) +
            (min(workload / 10, 1) * 0.3)
        ))
        
        risk_level = "high" if delay_score > 0.7 else "medium" if delay_score > 0.4 else "low"
        delay_days = int(delay_score * 7)
        
        return {
            "task_id": task.id,
            "delay_risk_score": round(delay_score, 3),
            "risk_level": risk_level,
            "predicted_completion_delay_days": delay_days,
            "recommendations": self._generate_recommendations(delay_score, task)
        }
    
    def _generate_recommendations(self, delay_prob: float, task) -> List[str]:
        """Generate recommendations based on delay probability"""
        recommendations = []
        
        if delay_prob > 0.7:
            recommendations.append("URGENT: Consider reassigning or breaking down this task")
            recommendations.append("Schedule immediate review meeting with assignee")
        elif delay_prob > 0.4:
            recommendations.append("Monitor progress closely")
            recommendations.append("Check if assignee needs additional resources")
        else:
            recommendations.append("Task on track - continue monitoring")
        
        return recommendations
    
    def _generate_burnout_recommendations(self, burnout_score: float, factors: List[str]) -> List[str]:
        """Generate burnout prevention recommendations"""
        recommendations = []
        
        if burnout_score > 0.7:
            recommendations.append("CRITICAL: Redistribute workload immediately")
            recommendations.append("Schedule wellness check-in with employee")
            recommendations.append("Consider temporary task freeze for this user")
        elif burnout_score > 0.4:
            recommendations.append("Monitor workload and provide support")
            recommendations.append("Encourage time management training")
        else:
            recommendations.append("Employee workload is manageable")
        
        return recommendations
