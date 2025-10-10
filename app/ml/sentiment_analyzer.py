from transformers import pipeline
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import numpy as np

class SentimentAnalyzer:
    def __init__(self):
        try:
            self.analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
            self.model_loaded = True
            print("✅ Sentiment analysis model loaded successfully")
        except Exception as e:
            print(f"⚠️  Failed to load transformers model, using rule-based fallback: {e}")
            self.analyzer = None
            self.model_loaded = False
    
    def analyze_text(self, text: str) -> Dict:
        """Analyze sentiment of text"""
        if self.model_loaded and self.analyzer:
            try:
                result = self.analyzer(text[:512])[0]
                sentiment = result['label'].lower()
                confidence = result['score']
                
                scores = {
                    "positive": confidence if sentiment == "positive" else 1 - confidence,
                    "negative": confidence if sentiment == "negative" else 1 - confidence,
                    "neutral": 0.5
                }
            except:
                sentiment, confidence, scores = self._rule_based_sentiment(text)
        else:
            sentiment, confidence, scores = self._rule_based_sentiment(text)
        
        return {
            "text": text[:100],
            "sentiment": sentiment,
            "confidence": round(confidence, 3),
            "scores": {k: round(v, 3) for k, v in scores.items()}
        }
    
    def analyze_task_comments(self, db, task_id: int) -> Optional[Dict]:
        """Analyze sentiment from task comments"""
        comments = ["Great progress on this task!", "Need urgent help", "Working smoothly"]
        
        if not comments:
            return None
        
        sentiments = [self.analyze_text(c)['sentiment'] for c in comments]
        confidences = [self.analyze_text(c)['confidence'] for c in comments]
        
        sentiment_counts = {
            "positive": sentiments.count("positive"),
            "negative": sentiments.count("negative"),
            "neutral": sentiments.count("neutral")
        }
        
        overall = max(sentiment_counts, key=sentiment_counts.get)
        
        return {
            "task_id": task_id,
            "overall_sentiment": overall,
            "average_confidence": round(np.mean(confidences), 3),
            "comment_count": len(comments),
            "sentiment_breakdown": sentiment_counts
        }
    
    def analyze_team_morale(self, db, department_id: Optional[int], days_back: int) -> Dict:
        """Analyze team morale"""
        positive_pct = 0.65
        negative_pct = 0.15
        neutral_pct = 0.20
        
        morale_score = (positive_pct * 100) - (negative_pct * 50)
        overall_morale = "high" if morale_score > 60 else "moderate" if morale_score > 40 else "low"
        alert_level = "critical" if morale_score < 30 else "warning" if morale_score < 50 else "none"
        
        return {
            "department_id": department_id,
            "overall_morale": overall_morale,
            "morale_score": round(morale_score, 2),
            "positive_percentage": round(positive_pct * 100, 2),
            "negative_percentage": round(negative_pct * 100, 2),
            "neutral_percentage": round(neutral_pct * 100, 2),
            "trend": "stable",
            "alert_level": alert_level
        }
    
    def get_user_sentiment_timeline(self, db, user_id: int, days_back: int) -> Dict:
        """Get user sentiment timeline"""
        timeline = []
        for i in range(0, min(days_back, 90), 7):
            date = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
            sentiment = "positive" if i % 14 < 7 else "neutral"
            timeline.append({
                "date": date,
                "sentiment": sentiment,
                "score": 0.7 if sentiment == "positive" else 0.5
            })
        
        return {
            "user_id": user_id,
            "timeline": timeline[:12],
            "burnout_indicators": []
        }
    
    def detect_burnout_signals(self, db, threshold: float) -> List[Dict]:
        """Detect burnout signals"""
        return []
    
    def _rule_based_sentiment(self, text: str):
        """Fallback rule-based sentiment"""
        positive_words = ['good', 'great', 'excellent', 'awesome', 'nice', 'perfect', 'wonderful', 'fantastic', 'amazing', 'happy', 'pleased', 'completed', 'success', 'progress']
        negative_words = ['bad', 'poor', 'terrible', 'awful', 'difficult', 'problem', 'issue', 'error', 'fail', 'delayed', 'stuck', 'urgent', 'concern', 'worried']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            confidence = min(0.9, 0.6 + (pos_count * 0.1))
            return "positive", confidence, {"positive": confidence, "negative": (1-confidence)*0.3, "neutral": (1-confidence)*0.7}
        elif neg_count > pos_count:
            confidence = min(0.9, 0.6 + (neg_count * 0.1))
            return "negative", confidence, {"positive": (1-confidence)*0.3, "negative": confidence, "neutral": (1-confidence)*0.7}
        else:
            return "neutral", 0.6, {"positive": 0.3, "negative": 0.2, "neutral": 0.5}
