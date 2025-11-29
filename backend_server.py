from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from backend.database.config import Base, engine, SessionLocal
from backend.database.models import DoctorProfile, User, AppointmentSlot, UserRole
from typing import List
import uvicorn

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Medical Scheduling API", version="1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        pass

@app.get("/")
async def root():
    return {
        "message": "Medical Scheduling API is running! 🏥", 
        "endpoints": {
            "doctors": "/api/v1/doctors",
            "doctor_slots": "/api/v1/doctors/{doctor_id}/slots",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    try:
        db = get_db()
        doctors_count = db.query(DoctorProfile).count()
        slots_count = db.query(AppointmentSlot).count()
        db.close()
        return {
            "status": "healthy",
            "database": "connected",
            "doctors": doctors_count,
            "slots": slots_count
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "unhealthy", "error": str(e)})

@app.get("/api/v1/doctors")
async def get_doctors(specialization: str = None):
    """Get list of available doctors"""
    try:
        db = get_db()
        try:
            query = db.query(DoctorProfile).join(User).filter(
                DoctorProfile.is_available_for_booking == True,
                User.is_active == True
            )
            
            if specialization:
                query = query.filter(DoctorProfile.specialization.ilike(f"%{specialization}%"))
            
            doctors = query.all()
            
            result = []
            for doctor in doctors:
                result.append({
                    "id": doctor.id,
                    "name": doctor.user.name,
                    "email": doctor.user.email,
                    "specialization": doctor.specialization,
                    "experience_years": doctor.experience_years,
                    "consultation_fee": doctor.consultation_fee,
                    "bio": doctor.bio,
                    "default_slot_duration": doctor.default_slot_duration_minutes,
                    "is_available": doctor.is_available_for_booking
                })
            
            return {
                "doctors": result,
                "count": len(result),
                "message": f"Found {len(result)} available doctors"
            }
        finally:
            db.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching doctors: {str(e)}")

@app.get("/api/v1/doctors/{doctor_id}")
async def get_doctor_details(doctor_id: int):
    """Get detailed information about a specific doctor"""
    try:
        db = get_db()
        try:
            doctor = db.query(DoctorProfile).join(User).filter(DoctorProfile.id == doctor_id).first()
            
            if not doctor:
                raise HTTPException(status_code=404, detail="Doctor not found")
            
            # Get available slots count
            available_slots = db.query(AppointmentSlot).filter(
                AppointmentSlot.doctor_id == doctor_id,
                AppointmentSlot.is_available == True
            ).count()
            
            return {
                "id": doctor.id,
                "name": doctor.user.name,
                "email": doctor.user.email,
                "specialization": doctor.specialization,
                "experience_years": doctor.experience_years,
                "consultation_fee": doctor.consultation_fee,
                "bio": doctor.bio,
                "license_number": doctor.license_number,
                "default_slot_duration": doctor.default_slot_duration_minutes,
                "is_available": doctor.is_available_for_booking,
                "available_slots_count": available_slots,
                "timezone": doctor.user.timezone
            }
        finally:
            db.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching doctor details: {str(e)}")

@app.get("/api/v1/doctors/{doctor_id}/slots")
async def get_doctor_slots(doctor_id: int, date: str = None):
    """Get available appointment slots for a doctor"""
    try:
        db = get_db()
        try:
            # Verify doctor exists
            doctor = db.query(DoctorProfile).filter(DoctorProfile.id == doctor_id).first()
            if not doctor:
                raise HTTPException(status_code=404, detail="Doctor not found")
            
            # Get available slots
            query = db.query(AppointmentSlot).filter(
                AppointmentSlot.doctor_id == doctor_id,
                AppointmentSlot.is_available == True
            )
            
            if date:
                # Filter by date if provided (format: YYYY-MM-DD)
                from datetime import datetime
                try:
                    target_date = datetime.strptime(date, "%Y-%m-%d").date()
                    query = query.filter(AppointmentSlot.date == target_date)
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
            
            slots = query.order_by(AppointmentSlot.date, AppointmentSlot.start_time).limit(50).all()
            
            result = []
            for slot in slots:
                result.append({
                    "id": slot.id,
                    "date": slot.date.isoformat(),
                    "start_time": slot.start_time.strftime("%H:%M"),
                    "end_time": slot.end_time.strftime("%H:%M"),
                    "duration_minutes": slot.duration_minutes,
                    "is_available": slot.is_available
                })
            
            return {
                "doctor_id": doctor_id,
                "doctor_name": doctor.user.name,
                "slots": result,
                "count": len(result),
                "message": f"Found {len(result)} available slots"
            }
        finally:
            db.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching slots: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002)