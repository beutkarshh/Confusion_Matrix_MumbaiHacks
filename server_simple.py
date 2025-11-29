from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.scheduling.endpoints import router as scheduling_router
from backend.database.config import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

# -------------------------------
# Initialize FastAPI 
# -------------------------------
app = FastAPI(title="GDHS Medical Scheduling API", version="1.0")

# CORS for local dev frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add scheduling routes (this is what you need for doctors/appointments)
# Note: Comment out the full router temporarily due to auth requirements
# app.include_router(scheduling_router)

# Add a simple doctors endpoint for testing
from backend.database.config import get_db
from backend.database.models import DoctorProfile, User
from sqlalchemy.orm import Session

@app.get("/api/v1/doctors-simple")
def get_doctors_simple():
    """Simple endpoint to list doctors without authentication"""
    try:
        from backend.database.config import SessionLocal
        db = SessionLocal()
        try:
            doctors = db.query(DoctorProfile).join(User).all()
            result = []
            for doctor in doctors:
                result.append({
                    "id": doctor.id,
                    "name": doctor.user.full_name,
                    "specialization": doctor.specialization,
                    "experience_years": doctor.experience_years,
                    "consultation_fee": doctor.consultation_fee,
                    "bio": doctor.bio,
                    "is_available": doctor.is_available_for_booking
                })
            return {"doctors": result, "count": len(result)}
        finally:
            db.close()
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e), "message": "Database connection failed"})

# -------------------------------
# Root Endpoint
# -------------------------------
@app.get("/")
def root():
    return {"message": "GDHS Medical Scheduling API is running 🚀", "endpoints": ["/api/v1/doctors", "/api/v1/appointments"]}

@app.get("/health")
def health():
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)