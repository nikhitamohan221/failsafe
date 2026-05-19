from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String)

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    roll_no = Column(String, unique=True, index=True)
    department = Column(String, index=True)
    semester = Column(Integer)
    cgpa = Column(Float)
    # New columns for XGBoost model
    g1 = Column(Float, default=0)
    g2 = Column(Float, default=0)
    absences = Column(Integer, default=0)
    failures = Column(Integer, default=0)
    studytime = Column(Integer, default=2)
    medu = Column(Integer, default=2)
    fedu = Column(Integer, default=2)
    goout = Column(Integer, default=3)
    dalc = Column(Integer, default=1)
    walc = Column(Integer, default=1)
    health = Column(Integer, default=3)
    famrel = Column(Integer, default=3)
    freetime = Column(Integer, default=3)
    traveltime = Column(Integer, default=1)
    age = Column(Integer, default=17)

    user = relationship("User")

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    subject = Column(String)
    attendance_percentage = Column(Float)
    week = Column(Integer)

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    subject = Column(String)
    score = Column(Float)
    submitted_on = Column(DateTime, default=datetime.utcnow)

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    risk_score = Column(Float)
    risk_label = Column(String)
    predicted_on = Column(DateTime, default=datetime.utcnow)
    shap_values = Column(JSON)

class Intervention(Base):
    __tablename__ = "interventions"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    type = Column(String)
    description = Column(String)
    assigned_by = Column(Integer, ForeignKey("users.id"))
    status = Column(String)
