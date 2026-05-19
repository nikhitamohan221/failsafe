from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine, SessionLocal
from routers import auth, students, predictions, interventions, dashboard

# Create database tables
models.Base.metadata.create_all(bind=engine)

def auto_seed():
    db = SessionLocal()
    if db.query(models.User).count() <= 2:
        try:
            import import_real_data
            import_real_data.seed()
        except Exception as e:
            print(f"Seed error: {e}")
    db.close()

auto_seed()

app = FastAPI(
    title="FAILSAFE API",
    description="Student failure prediction and intervention system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(students.router)
app.include_router(predictions.router)
app.include_router(interventions.router)
app.include_router(dashboard.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FAILSAFE API"}