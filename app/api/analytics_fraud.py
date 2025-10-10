from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.ml.anomaly_detector import AnomalyDetector
import numpy as np
from app.db.models.audit_log import AuditLog

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

# Instantiate detector (train on startup or in background in production)
detector = AnomalyDetector()

# Mock function to extract features from audit logs
def extract_features(logs):
    # For demo: use numeric encoding e.g. [action_code, user_id % 100, timestamp % 1000]
    features = []
    for log in logs:
        action_code = hash(log.action) % 100
        user_mod = log.user_id.int % 100
        time_mod = int(log.timestamp.timestamp()) % 1000
        features.append([action_code, user_mod, time_mod])
    return np.array(features)

@router.get("/fraud-alerts")
def fraud_alerts(db: Session = Depends(get_db)):
    logs = db.query(AuditLog).all()
    features = extract_features(logs)

    if not features.size:
        return {"alerts": [], "message": "No data to analyze"}

    if not detector.trained:
        detector.train(features)

    anomalies = detector.batch_detect(features)

    alerts = []
    for i, is_anomaly in enumerate(anomalies):
        if is_anomaly:
            alerts.append({
                "id": logs[i].id,
                "user_id": logs[i].user_id,
                "action": logs[i].action,
                "timestamp": logs[i].timestamp.isoformat()
            })

    return {
        "alert_count": len(alerts),
        "alerts": alerts
    }
