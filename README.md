# FAILSAFE – Student Failure Prediction & Intervention System

## Overview

FAILSAFE is a full-stack student analytics platform designed to identify students at academic risk and support data-driven interventions. The project combines machine learning, a FastAPI backend, and a React frontend to provide predictive insights, dashboards, and intervention tracking.

The system analyzes student-related academic data and predicts the likelihood of student failure, helping educators proactively support students before performance declines.

---

# Tech Stack

## Frontend

* React 19
* Vite
* React Router DOM
* Axios
* Recharts
* Lucide React

## Backend

* FastAPI
* SQLAlchemy
* JWT Authentication
* SQLite
* Scikit-learn
* SHAP
* Pandas & NumPy

## Machine Learning

* Data preprocessing and cleaning
* Exploratory Data Analysis (EDA)
* Predictive modeling
* Explainability using SHAP

---

# Project Structure

```bash
failsafe-main/
│
├── backend/                     # FastAPI backend
│   ├── routers/                 # API route modules
│   ├── main.py                  # Backend entry point
│   ├── models.py                # Database models
│   ├── database.py              # Database configuration
│   ├── schemas.py               # Pydantic schemas
│   ├── auth.py                  # Authentication logic
│   ├── ml_model.py              # ML integration
│   ├── model.pkl                # Trained ML model
│   ├── requirements.txt         # Backend dependencies
│   └── seed.py                  # Sample/real data seeding
│
├── frontend/                    # React frontend
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── ml/                          # Machine learning notebooks
│   ├── 01_Data_Cleaning.ipynb
│   ├── 02_EDA_Exploration.ipynb
│   ├── 03_Model_Training.ipynb
│   └── 04_Explainability_and_Interventions.ipynb
│
├── student-mat.csv              # Original dataset
├── processed_student_data.csv   # Cleaned dataset
└── failsafe.db                  # SQLite database
```

---

# Features

## Authentication

* JWT-based authentication
* Secure login and registration
* Protected API routes

## Student Management

* Add and manage student records
* Store academic and behavioral data
* Centralized student database

## Failure Prediction

* ML-powered student risk prediction
* Real-time probability scoring
* Academic performance analysis

## Dashboard & Analytics

* Visual performance metrics
* Interactive charts using Recharts
* Student risk overview

## Intervention Tracking

* Recommend interventions for at-risk students
* Monitor intervention outcomes
* Explainability insights using SHAP

---

# Installation & Setup

## Prerequisites

Make sure the following are installed:

* Python 3.10+
* Node.js 18+
* npm

---

# Backend Setup

## 1. Navigate to Backend

```bash
cd backend
```

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Start Backend Server

```bash
uvicorn main:app --reload
```

Backend will run at:

```bash
http://127.0.0.1:8000
```

API documentation:

```bash
http://127.0.0.1:8000/docs
```

---

# Frontend Setup

## 1. Navigate to Frontend

```bash
cd frontend
```

## 2. Install Dependencies

```bash
npm install
```

## 3. Start Development Server

```bash
npm run dev
```

Frontend will run at:

```bash
http://localhost:5173
```

---

# Machine Learning Workflow

The ML pipeline is documented through Jupyter notebooks inside the `ml/` folder:

1. Data cleaning and preprocessing
2. Exploratory data analysis
3. Model training and evaluation
4. Explainability and intervention recommendations

The trained model is exported as:

```bash
backend/model.pkl
```

---

# API Modules

| Module           | Description                  |
| ---------------- | ---------------------------- |
| `/auth`          | Authentication endpoints     |
| `/students`      | Student management APIs      |
| `/predictions`   | Failure prediction APIs      |
| `/interventions` | Intervention recommendations |
| `/dashboard`     | Dashboard analytics          |

---

# Example Workflow

1. User logs into the system
2. Student data is added or imported
3. ML model evaluates student risk
4. Dashboard visualizes predictions
5. Educators apply interventions
6. Progress is monitored over time

---

# Future Improvements

* Role-based access control
* Email/SMS notifications
* Real-time analytics
* Deployment with Docker
* Cloud database integration
* Advanced ML models
* Multi-school support

---

# Development Notes

* SQLite is used as the default database for local development.
* CORS is enabled in FastAPI for frontend-backend communication.
* Initial data is automatically seeded when the backend starts.

---

# Running the Complete Application

Open two terminals:

## Terminal 1 – Backend

```bash
cd backend
uvicorn main:app --reload
```

## Terminal 2 – Frontend

```bash
cd frontend
npm install
npm run dev
```

Then open:

```bash
http://localhost:5173
```

---

# License

This project is intended for educational and academic purposes.

---

# Contributors

Developed as part of the FAILSAFE academic risk prediction and intervention platform.
