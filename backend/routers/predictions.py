from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
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

    data = {
        "G1":         float(student.g1 or 0),
        "G2":         float(student.g2 or 0),
        "absences":   int(student.absences or 0),
        "failures":   int(student.failures or 0),
        "studytime":  int(student.studytime or 2),
        "Medu":       int(student.medu or 2),
        "Fedu":       int(student.fedu or 2),
        "goout":      int(student.goout or 3),
        "Dalc":       int(student.dalc or 1),
        "Walc":       int(student.walc or 1),
        "health":     int(student.health or 3),
        "famrel":     int(student.famrel or 3),
        "freetime":   int(student.freetime or 3),
        "traveltime": int(student.traveltime or 1),
        "age":        int(student.age or 17),
    }

    result = prediction_service.predict_risk(data)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    prediction = models.Prediction(
        student_id=student_id,
        risk_score=result["risk_score"],
        risk_label=result["risk_label"],
        shap_values=str(result["shap_values"])
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction


@router.post("/batch")
def predict_batch(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.require_role(["faculty", "hod"]))):
    students = db.query(models.Student).all()
    count = 0
    for student in students:
        try:
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

    predictions = db.query(models.Prediction).filter(
        models.Prediction.student_id == student_id
    ).order_by(models.Prediction.predicted_on.desc()).all()
    return predictions