import joblib
import numpy as np
import pandas as pd
import shap
import os
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder

# ── paths ────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
EXP_PATH   = os.path.join(BASE_DIR, "explainer.pkl")
FEAT_PATH  = os.path.join(BASE_DIR, "features.pkl")
DATA_PATH  = os.path.join(BASE_DIR, "processed_student_data.csv")

# ── features (G3 intentionally excluded to prevent leakage) ──────────────────
FEATURE_NAMES = [
    'G1', 'G2', 'absences', 'failures', 'studytime',
    'Medu', 'Fedu', 'goout',
    'Dalc', 'Walc', 'health',
    'famrel', 'freetime', 'traveltime', 'age'
]

RISK_LABELS = {0: "Low", 1: "Medium", 2: "High"}


# ─────────────────────────────────────────────────────────────────────────────
# TRAINING  (run this file directly: python ml_model.py)
# ─────────────────────────────────────────────────────────────────────────────
def train():
    df = pd.read_csv(DATA_PATH)

    # Encode categorical columns
    for col in df.select_dtypes(include="object").columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))

    # 3-tier risk label from G3 (G3 is NOT used as a feature)
    def assign_risk(g3):
        if g3 >= 14:  return 0   # Low
        elif g3 >= 10: return 1  # Medium
        else:          return 2  # High

    df["risk_label"] = df["G3"].apply(assign_risk)

    X = df[FEATURE_NAMES]
    y = df["risk_label"]

    print("Class distribution:\n", y.value_counts().to_string())

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    model = XGBClassifier(
        n_estimators=200,
        max_depth=4,           # Shallow = less overfitting
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=5,    # Prevents tiny-leaf memorisation
        objective="multi:softprob",
        num_class=3,
        eval_metric="mlogloss",
        random_state=42,
        verbosity=0,
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False,
    )

    y_pred = model.predict(X_test)
    print("\n── Evaluation ──────────────────────────────")
    print(classification_report(
        y_test, y_pred,
        target_names=["Low Risk", "Medium Risk", "High Risk"]
    ))

    explainer = shap.TreeExplainer(model)

    joblib.dump(model,        MODEL_PATH)
    joblib.dump(explainer,    EXP_PATH)
    joblib.dump(FEATURE_NAMES, FEAT_PATH)
    print("✅  Saved model.pkl, explainer.pkl, features.pkl")


# ─────────────────────────────────────────────────────────────────────────────
# INFERENCE SERVICE  (imported by FastAPI)
# ─────────────────────────────────────────────────────────────────────────────
class MLModel:
    def __init__(self):
        self.model     = joblib.load(MODEL_PATH)
        self.explainer = joblib.load(EXP_PATH)
        self.features  = joblib.load(FEAT_PATH)
        print("✅  Model and explainer loaded.")

    def predict_risk(self, data: dict) -> dict:
        row = [float(data.get(feat, 0)) for feat in self.features]
        X   = np.array(row).reshape(1, -1)

        # probabilities for all 3 classes
        proba      = self.model.predict_proba(X)[0]   # shape (3,)
        pred_class = int(np.argmax(proba))
        risk_label = RISK_LABELS[pred_class]

        # Confidence score (0-100) for the predicted class
        risk_score = round(float(proba[pred_class]) * 100, 2)

        # SHAP – TreeExplainer returns array of shape (n_samples, n_features, n_classes)
        shap_vals_all = self.explainer.shap_values(X)   # list of 3 arrays
        shap_for_class = shap_vals_all[pred_class][0]   # values for predicted class

        shap_dict = {
            feat: round(float(val), 4)
            for feat, val in zip(self.features, shap_for_class)
        }

        top_factors = sorted(
            shap_dict.items(), key=lambda x: abs(x[1]), reverse=True
        )[:3]

        factor_labels = {
            "G1": "Mid-term grade 1", "G2": "Mid-term grade 2",
            "absences": "Absences", "failures": "Past failures",
            "studytime": "Study time", "Medu": "Mother's education",
            "Fedu": "Father's education", "goout": "Going out frequency",
            "Dalc": "Weekday alcohol", "Walc": "Weekend alcohol",
            "health": "Health status", "famrel": "Family relationship",
            "freetime": "Free time", "traveltime": "Travel time", "age": "Age"
        }

        explanation = "Top risk factors: " + ", ".join(
            [factor_labels.get(f[0], f[0]) for f in top_factors]
        )

        return {
            "risk_score": risk_score,
            "risk_label": risk_label,
            "probabilities": {
                "Low":    round(float(proba[0]) * 100, 2),
                "Medium": round(float(proba[1]) * 100, 2),
                "High":   round(float(proba[2]) * 100, 2),
            },
            "shap_values": shap_dict,
            "top_factors": [{"feature": f[0], "label": factor_labels.get(f[0], f[0]), "value": f[1]} for f in top_factors],
            "explanation": explanation,
        }


# ─────────────────────────────────────────────────────────────────────────────
# singleton used by FastAPI routers
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    train()
else:
    if not os.path.exists(MODEL_PATH):
        train()
    prediction_service = MLModel()
