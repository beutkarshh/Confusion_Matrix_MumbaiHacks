#!/usr/bin/env python3
"""
Working backend server for the medical scheduling system
This version removes authentication requirements for development
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, time
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database.config import Base, engine, SessionLocal
from backend.database.models import User, DoctorProfile, DoctorAvailability, AppointmentSlot, Appointment, UserRole

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Medical Scheduling API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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

class AppointmentSlotResponse(BaseModel):
    id: int
    date: str
    start_time: str
    end_time: str
    status: str
    doctor_id: int

# Helper function to get database session
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Don't close here, close in the endpoint

@app.get("/")
def root():
    return {
        "message": "Medical Scheduling API is running! 🏥",
        "endpoints": {
            "doctors": "/api/v1/doctors",
            "slots": "/api/v1/doctors/{doctor_id}/slots",
            "health": "/health"
        }
    }

@app.get("/health")
def health_check():
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
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.get("/api/v1/doctors", response_model=List[DoctorResponse])
def get_doctors(specialization: Optional[str] = Query(None)):
    """Get all available doctors, optionally filtered by specialization"""
    try:
        db = get_db()
        
        query = db.query(DoctorProfile).join(User).filter(
            DoctorProfile.is_available_for_booking == True
        )
        
        if specialization:
            query = query.filter(
                DoctorProfile.specialization.ilike(f"%{specialization}%")
            )
        
        doctors = query.all()
        
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
        
        db.close()
        return result
        
    except Exception as e:
        if 'db' in locals():
            db.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/v1/doctors/{doctor_id}/slots")
def get_doctor_slots(
    doctor_id: int,
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get available slots for a specific doctor"""
    try:
        db = get_db()
        
        # Check if doctor exists
        doctor = db.query(DoctorProfile).filter(DoctorProfile.id == doctor_id).first()
        if not doctor:
            db.close()
            raise HTTPException(status_code=404, detail="Doctor not found")
        
        query = db.query(AppointmentSlot).filter(
            AppointmentSlot.doctor_id == doctor_id,
            AppointmentSlot.status == "available"
        )
        
        # Add date filters if provided
        if date_from:
            try:
                from_date = datetime.strptime(date_from, "%Y-%m-%d").date()
                query = query.filter(AppointmentSlot.date >= from_date)
            except ValueError:
                db.close()
                raise HTTPException(status_code=400, detail="Invalid date_from format. Use YYYY-MM-DD")
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, "%Y-%m-%d").date()
                query = query.filter(AppointmentSlot.date <= to_date)
            except ValueError:
                db.close()
                raise HTTPException(status_code=400, detail="Invalid date_to format. Use YYYY-MM-DD")
        
        slots = query.order_by(AppointmentSlot.date, AppointmentSlot.start_time).limit(50).all()
        
        result = []
        for slot in slots:
            result.append(AppointmentSlotResponse(
                id=slot.id,
                date=slot.date.isoformat(),
                start_time=slot.start_time.strftime("%H:%M"),
                end_time=slot.end_time.strftime("%H:%M"),
                status=slot.status.value if hasattr(slot.status, 'value') else slot.status,
                doctor_id=slot.doctor_id
            ))
        
        db.close()
        return {
            "doctor": {
                "id": doctor.id,
                "name": doctor.user.name,
                "specialization": doctor.specialization
            },
            "slots": result,
            "total_slots": len(result)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        if 'db' in locals():
            db.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/v1/doctors/{doctor_id}")
def get_doctor_details(doctor_id: int):
    """Get detailed information about a specific doctor"""
    try:
        db = get_db()
        
        doctor = db.query(DoctorProfile).join(User).filter(DoctorProfile.id == doctor_id).first()
        if not doctor:
            db.close()
            raise HTTPException(status_code=404, detail="Doctor not found")
        
        # Get availability info
        availabilities = db.query(DoctorAvailability).filter(
            DoctorAvailability.doctor_id == doctor_id
        ).all()
        
        # Get slot counts
        total_slots = db.query(AppointmentSlot).filter(
            AppointmentSlot.doctor_id == doctor_id
        ).count()
        
        available_slots = db.query(AppointmentSlot).filter(
            AppointmentSlot.doctor_id == doctor_id,
            AppointmentSlot.status == "available"
        ).count()
        
        result = {
            "id": doctor.id,
            "name": doctor.user.name,
            "email": doctor.user.email,
            "specialization": doctor.specialization,
            "experience_years": doctor.experience_years,
            "consultation_fee": doctor.consultation_fee,
            "bio": doctor.bio,
            "is_available": doctor.is_available_for_booking,
            "availability_schedules": len(availabilities),
            "total_slots": total_slots,
            "available_slots": available_slots
        }
        
        db.close()
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        if 'db' in locals():
            db.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🏥 Starting Medical Scheduling API...")
    print("📋 Available endpoints:")
    print("  - GET /api/v1/doctors - List all doctors")
    print("  - GET /api/v1/doctors/{id} - Get doctor details")
    print("  - GET /api/v1/doctors/{id}/slots - Get doctor's available slots")
    print("  - GET /health - Health check")
    
    uvicorn.run(app, host="127.0.0.1", port=8001)