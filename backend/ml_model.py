import joblib
import numpy as np
import shap
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

FEATURE_NAMES = ['G1', 'G2', 'G3', 'absences', 'failures', 'studytime', 
                  'Medu', 'Fedu', 'goout', 'Dalc', 'Walc', 'health']

class MLModel:
    def __init__(self):
        self.model = joblib.load(MODEL_PATH)
        # Use KernelExplainer for pipeline models
        background = np.zeros((1, len(FEATURE_NAMES)))
        self.explainer = shap.KernelExplainer(
            lambda x: self.model.predict_proba(x)[:, 1], background
        )
        print("Model and explainer loaded successfully.")

    def predict_risk(self, data: dict) -> dict:
        row = [float(data.get(feat, 0)) for feat in FEATURE_NAMES]
        X = np.array(row).reshape(1, -1)
        
        risk_score = float(self.model.predict_proba(X)[0][1]) * 100

        if risk_score >= 60:
            risk_label = "High"
        elif risk_score >= 35:
            risk_label = "Medium"
        else:
            risk_label = "Low"

        # SHAP values
        shap_values = self.explainer.shap_values(X, nsamples=50)[0]
        shap_dict = {feat: round(float(val), 4) for feat, val in zip(FEATURE_NAMES, shap_values)}

        top_factors = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)[:3]
        explanation = "Top risk factors: " + ", ".join([f[0] for f in top_factors])

        return {
            "risk_score": round(risk_score, 2),
            "risk_label": risk_label,
            "shap_values": shap_dict,
            "explanation": explanation
        }

prediction_service = MLModel()
