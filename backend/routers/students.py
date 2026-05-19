

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
import io
import random
import models, schemas, auth, database
from ml_model import prediction_service

router = APIRouter(prefix="/students", tags=["students"])

FEATURE_NAMES = ['school', 'sex', 'age', 'address', 'famsize', 'Pstatus',
                 'Medu', 'Fedu', 'Mjob', 'Fjob', 'reason', 'guardian',
                 'traveltime', 'studytime', 'failures', 'schoolsup', 'famsup',
                 'paid', 'activities', 'nursery', 'higher', 'internet', 'romantic',
                 'famrel', 'freetime', 'goout', 'Dalc', 'Walc', 'health',
                 'absences', 'G1', 'G2', 'G3']

DEPARTMENTS = ["Computer Science", "Electronics", "Mechanical", "Civil", "Information Technology"]

def get_intervention(row, risk_label):
    prefix = "[Early Intervention] " if risk_label == 'Medium' else ""
    if row.get('absences', 0) > 10:
        return "Attendance Counseling", f"{prefix}Student has {int(row['absences'])} absences. Schedule immediate attendance counseling."
    elif row.get('failures', 0) > 0:
        return "Remedial Support", f"{prefix}Student has {int(row['failures'])} failed subject(s). Enroll in remedial classes."
    elif row.get('G3', 20) < 10:
        return "Academic Tutoring", f"{prefix}Student scored {int(row['G3'])}/20. Provide personalized study plan."
    elif row.get('studytime', 4) < 2:
        return "Study Plan Adjustment", f"{prefix}Low study time. Create structured weekly study schedule."
    elif row.get('goout', 1) > 3:
        return "Counseling Referral", f"{prefix}High social activity. Refer to student counselor for time management."
    else:
        return "Academic Mentorship", f"{prefix}Multiple risk factors. Assign academic mentor and bi-weekly reviews."

@router.get("/", response_model=List[schemas.StudentResponse])
def get_students(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.require_role(["faculty", "hod"]))):
    students = db.query(models.Student).all()
    return students

@router.get("/{student_id}", response_model=schemas.StudentResponse)
def get_student(student_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role == "student":
        student_record = db.query(models.Student).filter(models.Student.user_id == current_user.id).first()
        if not student_record or student_record.id != student_id:
            raise HTTPException(status_code=403, detail="Not authorized to view this student")
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.post("/upload")
def upload_students_csv(
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_role(["faculty", "hod"]))
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")

    content = file.file.read()
    df = pd.read_csv(io.BytesIO(content))

    # Check required columns
    missing = [f for f in FEATURE_NAMES if f not in df.columns]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing columns: {missing}. Required: {FEATURE_NAMES}"
        )

    created = 0
    predicted = 0
    errors = 0

    for i, row in df.iterrows():
        try:
            # Create user account for student
            name = row.get('name', f"Student {i+1}")
            email = row.get('email', f"uploaded_student_{i+1}_{random.randint(1000,9999)}@failsafe.com")

            # Check if email already exists
            existing_user = db.query(models.User).filter(models.User.email == email).first()
            if existing_user:
                # Update existing student predictions
                student = db.query(models.Student).filter(models.Student.user_id == existing_user.id).first()
            else:
                # Create new user
                from passlib.context import CryptContext
                pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                user = models.User(
                    name=name,
                    email=email,
                    password_hash=pwd_context.hash("password123"),
                    role="student"
                )
                db.add(user)
                db.commit()

                # Create student record
                cgpa = round((float(row.get('G3', 10)) / 20.0) * 10, 2)
                dept = row.get('department', random.choice(DEPARTMENTS))
                roll_no = row.get('roll_no', f"UP{200+i}")

                student = models.Student(
                    user_id=user.id,
                    roll_no=str(roll_no),
                    department=str(dept),
                    semester=int(row.get('semester', random.randint(2, 8))),
                    cgpa=cgpa
                )
                db.add(student)
                db.commit()
                created += 1

            # Run ML prediction
            features = {feat: row[feat] for feat in FEATURE_NAMES if feat in row}
            result = prediction_service.predict_risk(features)

            pred = models.Prediction(
                student_id=student.id,
                risk_score=result['risk_score'],
                risk_label=result['risk_label'],
                shap_values=result['shap_values']
            )
            db.add(pred)

            # Auto-assign intervention for High/Medium risk
            if result['risk_label'] in ['High', 'Medium']:
                int_type, int_desc = get_intervention(row.to_dict(), result['risk_label'])
                intervention = models.Intervention(
                    student_id=student.id,
                    type=int_type,
                    description=int_desc,
                    assigned_by=current_user.id,
                    status="pending"
                )
                db.add(intervention)

            db.commit()
            predicted += 1

        except Exception as e:
            errors += 1
            print(f"Error processing row {i}: {e}")
            continue

    return {
        "message": f"CSV processed successfully!",
        "total_rows": len(df),
        "students_created": created,
        "predictions_made": predicted,
        "errors": errors,
        "high_risk": db.query(models.Prediction).filter(models.Prediction.risk_label == "High").count(),
        "medium_risk": db.query(models.Prediction).filter(models.Prediction.risk_label == "Medium").count(),
        "low_risk": db.query(models.Prediction).filter(models.Prediction.risk_label == "Low").count()
    }