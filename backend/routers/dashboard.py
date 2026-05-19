from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import models, schemas, auth, database
from datetime import datetime, timedelta

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/faculty")
def faculty_dashboard(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.require_role(["faculty", "hod"]))):
    # Get latest predictions for all students
    subquery = db.query(
        models.Prediction.student_id,
        func.max(models.Prediction.predicted_on).label('latest_prediction')
    ).group_by(models.Prediction.student_id).subquery()

    latest_preds = db.query(models.Prediction).join(
        subquery,
        (models.Prediction.student_id == subquery.c.student_id) &
        (models.Prediction.predicted_on == subquery.c.latest_prediction)
    ).all()

    stats = {
        "total_students": db.query(models.Student).count(),
        "high_risk": len([p for p in latest_preds if p.risk_label == 'High']),
        "medium_risk": len([p for p in latest_preds if p.risk_label == 'Medium']),
        "low_risk": len([p for p in latest_preds if p.risk_label == 'Low']),
    }
    
    # Enrich with student details
    flagged_students = []
    for p in latest_preds:
        student = db.query(models.Student).filter(models.Student.id == p.student_id).first()
        user = db.query(models.User).filter(models.User.id == student.user_id).first()
        flagged_students.append({
            "student_id": student.id,
            "name": user.name,
            "roll_no": student.roll_no,
            "department": student.department,
            "semester": student.semester,
            "risk_score": p.risk_score,
            "risk_label": p.risk_label
        })

    return {"stats": stats, "students": flagged_students}

@router.get("/hod")
def hod_dashboard(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.require_role(["hod"]))):
    # Time series of risk levels
    # Simply get all predictions and group by date for trends
    predictions = db.query(models.Prediction).all()
    
    trends = {}
    for p in predictions:
        date_str = p.predicted_on.strftime("%Y-%m-%d")
        if date_str not in trends:
            trends[date_str] = {"High": 0, "Medium": 0, "Low": 0}
        trends[date_str][p.risk_label] += 1
        
    trend_list = [{"date": k, **v} for k, v in trends.items()]
    trend_list.sort(key=lambda x: x["date"])

    stats = {
        "critical_cases": sum(1 for p in predictions if p.risk_label == "High"),
        "total_interventions": db.query(models.Intervention).count(),
        "completed_interventions": db.query(models.Intervention).filter(models.Intervention.status == "complete").count()
    }
    return {"trends": trend_list, "stats": stats}

@router.get("/student/{student_id}")
def student_dashboard(student_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role == "student":
        student_record = db.query(models.Student).filter(models.Student.user_id == current_user.id).first()
        if not student_record or student_record.id != student_id:
            raise HTTPException(status_code=403, detail="Not authorized")
            
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    latest_pred = db.query(models.Prediction).filter(models.Prediction.student_id == student_id).order_by(models.Prediction.predicted_on.desc()).first()
    interventions = db.query(models.Intervention).filter(models.Intervention.student_id == student_id).all()
    
    # SHAP explanation string generated at prediction time or dynamically
    from ml_model import prediction_service
    explanation = "No predictions yet."
    if latest_pred and latest_pred.shap_values:
        top_factors = sorted(latest_pred.shap_values.items(), key=lambda x: abs(x[1]), reverse=True)[:3]
        explanation = "Top risk factors: " + ", ".join([f[0] for f in top_factors])
    return {
        "student": {
            "roll_no": student.roll_no,
            "department": student.department,
            "semester": student.semester,
            "cgpa": student.cgpa
        },
        "latest_prediction": latest_pred,
        "explanation": explanation,
        "interventions": [
            {
                "id": i.id,
                "type": i.type,
                "description": i.description,
                "status": i.status
            } for i in interventions
        ]
    }
