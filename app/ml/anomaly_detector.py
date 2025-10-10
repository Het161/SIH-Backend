from sklearn.ensemble import IsolationForest
import numpy as np

class AnomalyDetector:
    def __init__(self):
        # Initialize Isolation Forest
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self.trained = False

    def train(self, feature_matrix):
        self.model.fit(feature_matrix)
        self.trained = True

    def detect(self, sample):
        if not self.trained:
            raise RuntimeError("Model not trained")
        pred = self.model.predict([sample])
        return pred[0] == -1  # True means an anomaly

    def batch_detect(self, samples):
        if not self.trained:
            raise RuntimeError("Model not trained")
        return self.model.predict(samples) == -1
