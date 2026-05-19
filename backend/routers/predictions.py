from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import models, schemas, auth, database
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ml_model import prediction_service

router = APIRouter(prefix="/predict", tags=["predictions"])

@router.post("/{student_id}", response_model=schemas.PredictionResponse)
def predict_student(student_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.require_role(["faculty", "hod"]))):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Aggregate attendance
    attendances = db.query(models.Attendance).filter(models.Attendance.student_id == student_id).all()
    avg_attendance = sum(a.attendance_percentage for a in attendances) / len(attendances) if attendances else 0

    # Aggregate assignments
    assignments = db.query(models.Assignment).filter(models.Assignment.student_id == student_id).all()
    avg_assignment = sum(a.score for a in assignments) / len(assignments) if assignments else 0

    # Call ML service
    result = prediction_service.predict_risk(
        attendance=avg_attendance,
        assignments=avg_assignment,
        cgpa=student.cgpa
    )

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    prediction = models.Prediction(
        student_id=student_id,
        risk_score=result["risk_score"],
        risk_label=result["risk_label"],
        shap_values=result["shap_values"]
    )
    db.add(prediction)

    # Save suggested interventions
    for sugg in result["suggested_interventions"]:
        intervention = models.Intervention(
            student_id=student_id,
            type=sugg["type"],
            description=sugg["description"],
            assigned_by=current_user.id,
            status="suggested"
        )
        db.add(intervention)

    db.commit()
    db.refresh(prediction)
    return prediction

@router.post("/batch")
def predict_batch(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.require_role(["faculty", "hod"]))):
    students = db.query(models.Student).all()
    count = 0
    for student in students:
        try:
            # simple version, normally you'd batch this
            predict_student(student.id, db, current_user)
            count += 1
        except:
            pass
    return {"message": f"Ran predictions for {count} students."}

@router.get("/{student_id}/history", response_model=List[schemas.PredictionResponse])
def get_prediction_history(student_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role == "student":
        student_record = db.query(models.Student).filter(models.Student.user_id == current_user.id).first()
        if not student_record or student_record.id != student_id:
            raise HTTPException(status_code=403, detail="Not authorized")
            
    predictions = db.query(models.Prediction).filter(models.Prediction.student_id == student_id).order_by(models.Prediction.predicted_on.desc()).all()
    return predictions
