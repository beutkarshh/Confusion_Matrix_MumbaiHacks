#!/usr/bin/env python3
"""
Working backend server for the medical scheduling app
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date

# Database imports
from backend.database.config import SessionLocal, Base, engine
from backend.database.models import User, DoctorProfile, AppointmentSlot, DoctorAvailability

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI(title="Medical Scheduling API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class DoctorResponse(BaseModel):
    id: int
    name: str
    email: str
    specialization: str
    experience_years: int
    consultation_fee: float
    bio: str
    is_available: bool

class SlotResponse(BaseModel):
    id: int
    start_time: datetime
    end_time: datetime
    is_available: bool

@app.get("/")
def root():
    return {
        "message": "Medical Scheduling API is running! 🏥", 
        "endpoints": {
            "doctors": "/api/v1/doctors",
            "doctor_slots": "/api/v1/doctors/{doctor_id}/slots",
            "health": "/health"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/v1/doctors", response_model=List[DoctorResponse])
def get_doctors():
    """Get all available doctors"""
    try:
        db = SessionLocal()
        try:
            doctors = db.query(DoctorProfile).join(User).filter(
                DoctorProfile.is_available_for_booking == True
            ).all()
            
            result = []
            for doctor in doctors:
                result.append(DoctorResponse(
                    id=doctor.id,
                    name=doctor.user.name,
                    email=doctor.user.email,
                    specialization=doctor.specialization,
                    experience_years=doctor.experience_years,
                    consultation_fee=doctor.consultation_fee,
                    bio=doctor.bio,
                    is_available=doctor.is_available_for_booking
                ))
            
            return result
        finally:
            db.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/v1/doctors/{doctor_id}/slots", response_model=List[SlotResponse])
def get_doctor_slots(doctor_id: int, date_filter: Optional[str] = None):
    """Get available slots for a specific doctor"""
    try:
        db = SessionLocal()
        try:
            query = db.query(AppointmentSlot).filter(
                AppointmentSlot.doctor_id == doctor_id,
                AppointmentSlot.is_available == True
            )
            
            if date_filter:
                # Filter by date if provided
                target_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
                query = query.filter(
                    AppointmentSlot.start_time >= datetime.combine(target_date, datetime.min.time()),
                    AppointmentSlot.start_time < datetime.combine(target_date, datetime.max.time())
                )
            
            slots = query.order_by(AppointmentSlot.start_time).limit(50).all()
            
            result = []
            for slot in slots:
                result.append(SlotResponse(
                    id=slot.id,
                    start_time=slot.start_time,
                    end_time=slot.end_time,
                    is_available=slot.is_available
                ))
            
            return result
        finally:
            db.close()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/v1/doctor/{doctor_id}")
def get_doctor_details(doctor_id: int):
    """Get specific doctor details"""
    try:
        db = SessionLocal()
        try:
            doctor = db.query(DoctorProfile).join(User).filter(
                DoctorProfile.id == doctor_id
            ).first()
            
            if not doctor:
                raise HTTPException(status_code=404, detail="Doctor not found")
            
            return DoctorResponse(
                id=doctor.id,
                name=doctor.user.name,
                email=doctor.user.email,
                specialization=doctor.specialization,
                experience_years=doctor.experience_years,
                consultation_fee=doctor.consultation_fee,
                bio=doctor.bio,
                is_available=doctor.is_available_for_booking
            )
        finally:
            db.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)