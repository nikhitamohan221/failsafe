from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
import io
import models, schemas, auth, database

router = APIRouter(prefix="/students", tags=["students"])

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
def upload_students_csv(file: UploadFile = File(...), db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.require_role(["faculty", "hod"]))):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")
    
    content = file.file.read()
    df = pd.read_csv(io.BytesIO(content))
    
    count = 0
    # Expected columns: roll_no, name, email, department, semester, cgpa, attendance, assignments
    # This is a simplified bulk upload that updates or creates students (ignoring passwords for now)
    for _, row in df.iterrows():
        # Dummy create or skip for this example
        pass
    
    return {"message": f"Successfully processed {len(df)} records (dummy)."}
