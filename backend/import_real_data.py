import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import random
from database import SessionLocal, engine
import models
from ml_model import prediction_service
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DEPARTMENTS = ["Computer Science", "Electronics", "Mechanical", "Civil", "Information Technology"]

FEATURE_NAMES = ['G1', 'G2', 'G3', 'absences', 'failures', 'studytime', 
                  'Medu', 'Fedu', 'goout', 'Dalc', 'Walc', 'health']

models.Base.metadata.create_all(bind=engine)

def get_intervention(row, risk_label):
    """Generate specific intervention based on actual student data values"""
    reasons = []
    
    if row.get('absences', 0) > 10:
        reasons.append(('absences', row['absences']))
    if row.get('failures', 0) > 0:
        reasons.append(('failures', row['failures']))
    if row.get('G3', 20) < 10:
        reasons.append(('low_grades', row['G3']))
    if row.get('studytime', 4) < 2:
        reasons.append(('studytime', row['studytime']))
    if row.get('goout', 1) > 3:
        reasons.append(('goout', row['goout']))
    if row.get('Dalc', 1) > 2 or row.get('Walc', 1) > 3:
        reasons.append(('alcohol', row.get('Dalc', 0)))
    if row.get('health', 5) < 2:
        reasons.append(('health', row['health']))

    prefix = "[Early Intervention] " if risk_label == 'Medium' else ""

    if not reasons:
        return "Academic Mentorship", prefix + "Assign academic mentor and schedule bi-weekly progress review sessions"

    # Pick most critical reason
    primary = reasons[0][0]

    if primary == 'absences':
        abs_count = int(reasons[0][1])
        return "Attendance Counseling", f"{prefix}Student has {abs_count} absences. Schedule immediate attendance counseling and set weekly check-ins with faculty advisor"
    
    elif primary == 'failures':
        fail_count = int(reasons[0][1])
        return "Remedial Support", f"{prefix}Student has {fail_count} failed subject(s). Enroll in remedial classes and assign dedicated academic mentor for revision"
    
    elif primary == 'low_grades':
        g3 = int(reasons[0][1])
        return "Academic Tutoring", f"{prefix}Student scored {g3}/20 in final exam. Provide personalized study plan and extra tutorial sessions for weak subjects"
    
    elif primary == 'studytime':
        return "Study Plan Adjustment", f"{prefix}Student studies less than 2 hours/week. Create structured weekly study schedule with faculty guidance"
    
    elif primary == 'goout':
        return "Counseling Referral", f"{prefix}High social activity affecting academics. Refer to student counselor for time management and priority guidance"
    
    elif primary == 'alcohol':
        return "Wellness Counseling", f"{prefix}Lifestyle factors affecting academic performance. Refer to student wellness counselor for support"
    
    elif primary == 'health':
        return "Health Support", f"{prefix}Poor health status reported. Connect student with campus health services and allow academic accommodations"
    
    else:
        return "Academic Support", f"{prefix}Multiple risk factors detected. Assign academic mentor and create personalized improvement plan"

def seed():
    db = SessionLocal()

    db.query(models.Prediction).delete()
    db.query(models.Intervention).delete()
    db.query(models.Student).delete()
    db.query(models.User).delete()
    db.commit()

    faculty = models.User(name="Dr. Smith", email="faculty@failsafe.com",
                          password_hash=pwd_context.hash("password"), role="faculty")
    hod = models.User(name="Prof. Johnson", email="hod@failsafe.com",
                      password_hash=pwd_context.hash("password"), role="hod")
    db.add_all([faculty, hod])
    db.commit()

    df = pd.read_csv("processed_student_data.csv")
    random.seed(42)

    for i, row in df.iterrows():
        name = f"Student {i+1}"
        email = f"student{i+1}@failsafe.com"
        cgpa = round((row['G3'] / 20.0) * 10, 2)

        user = models.User(
            name=name, email=email,
            password_hash=pwd_context.hash("password"),
            role="student"
        )
        db.add(user)
        db.commit()

        dept = random.choice(DEPARTMENTS)
        roll_no = f"{dept[:2].upper()}{200+i}"
        student = models.Student(
            user_id=user.id, roll_no=roll_no,
            department=dept, semester=random.randint(2, 8), cgpa=cgpa
        )
        db.add(student)
        db.commit()

        features = {feat: row[feat] for feat in FEATURE_NAMES if feat in row}
        try:
            result = prediction_service.predict_risk(features)
            pred = models.Prediction(
                student_id=student.id,
                risk_score=result['risk_score'],
                risk_label=result['risk_label'],
                shap_values=result['shap_values']
            )
            db.add(pred)

            if result['risk_label'] in ['High', 'Medium']:
                int_type, int_desc = get_intervention(row.to_dict(), result['risk_label'])
                intervention = models.Intervention(
                    student_id=student.id,
                    type=int_type,
                    description=int_desc,
                    assigned_by=faculty.id,
                    status="pending"
                )
                db.add(intervention)
        except Exception as e:
            print(f"Prediction error for student {i}: {e}")

        db.commit()
        if i % 10 == 0:
            print(f"Processed {i+1} students...")

    print(f"\nDone! Imported {len(df)} real students into FAILSAFE database.")
    db.close()

if __name__ == "__main__":
    seed()