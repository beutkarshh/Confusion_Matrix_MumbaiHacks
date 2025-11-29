from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timezone, timedelta

from ..database.config import get_db
from ..database.models import User, DoctorProfile, UserRole as SQLUserRole
from .schemas import *
from .services import SchedulingService, SlotGenerationService
from .video_service import AppointmentVideoService

router = APIRouter(prefix="/api/scheduling", tags=["Scheduling"])
security = HTTPBearer()

def _normalize_role(role_obj):
    """Return role as uppercase string regardless of Enum or raw string."""
    if role_obj is None:
        return None
    if hasattr(role_obj, "value"):
        return str(role_obj.value).upper()
    return str(role_obj).upper()

# Mock authentication - replace with your real auth system
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Mock authentication function - replace with your actual auth implementation
    For development, this accepts any token and returns a user
    """
    # In production, validate the JWT token and get user from it
    # For now, we'll use the token as a user_id for demo purposes
    try:
        user_id = int(credentials.credentials)
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return user
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )

def get_current_doctor(current_user: User = Depends(get_current_user)) -> DoctorProfile:
    """Get current doctor profile - ensures user is a doctor"""
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to doctors"
        )
    
    if not current_user.doctor_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    return current_user.doctor_profile

# ================================
# Doctor Availability Management
# ================================

@router.post("/doctors/{doctor_id}/availability", response_model=List[DoctorAvailabilityResponse])
async def set_doctor_availability(
    doctor_id: int,
    schedule_request: DoctorScheduleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set up a doctor's availability schedule"""
    
    # Verify the doctor
    doctor = db.query(DoctorProfile).filter(DoctorProfile.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Authorization: only the doctor themselves or admin can set availability
    if current_user.id != doctor.user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to set this doctor's availability")
    
    created_availabilities = []
    
    # Create availability patterns
    for availability_data in schedule_request.availability_patterns:
        availability_data.doctor_id = doctor_id
        
        # Create availability record
        from ..database.models import DoctorAvailability
        availability = DoctorAvailability(**availability_data.dict())
        db.add(availability)
        created_availabilities.append(availability)
    
    db.commit()
    
    # Generate slots for the requested time period
    if schedule_request.generate_slots_for_weeks > 0:
        slot_service = SlotGenerationService(db)
        start_date = date.today()
        end_date = start_date + timedelta(weeks=schedule_request.generate_slots_for_weeks)
        
        slot_service.generate_slots_for_doctor(
            doctor_id=doctor_id,
            start_date=start_date,
            end_date=end_date,
            force_regenerate=True
        )
    
    return created_availabilities

@router.get("/doctors/{doctor_id}/availability", response_model=List[DoctorAvailabilityResponse])
async def get_doctor_availability(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    """Get a doctor's availability patterns"""
    
    doctor = db.query(DoctorProfile).filter(DoctorProfile.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    from ..database.models import DoctorAvailability
    availabilities = db.query(DoctorAvailability).filter(
        DoctorAvailability.doctor_id == doctor_id,
        DoctorAvailability.is_active == True
    ).all()
    
    return availabilities

@router.post("/doctors/{doctor_id}/generate-slots")
async def generate_slots(
    doctor_id: int,
    request: GenerateSlotsRequest,
    current_doctor: DoctorProfile = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):
    """Generate appointment slots for a doctor"""
    
    # Authorization: only the doctor themselves or admin can generate slots
    if current_doctor.id != doctor_id:
        raise HTTPException(status_code=403, detail="Can only generate slots for yourself")
    
    slot_service = SlotGenerationService(db)
    
    try:
        slots = slot_service.generate_slots_for_doctor(
            doctor_id=request.doctor_id,
            start_date=request.start_date,
            end_date=request.end_date,
            force_regenerate=request.force_regenerate
        )
        
        return {
            "message": f"Generated {len(slots)} slots",
            "slots_generated": len(slots),
            "date_range": f"{request.start_date} to {request.end_date}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ================================
# Patient Booking
# ================================

@router.get("/doctors", response_model=List[DoctorProfileResponse])
async def list_available_doctors(
    db: Session = Depends(get_db),
    specialization: Optional[str] = Query(None)
):
    """List all available doctors for booking"""
    
    from ..database.models import DoctorProfile
    query = db.query(DoctorProfile).filter(DoctorProfile.is_available_for_booking == True)
    
    if specialization:
        query = query.filter(DoctorProfile.specialization.ilike(f"%{specialization}%"))
    
    doctors = query.all()
    return doctors

@router.get("/doctors/{doctor_id}/slots", response_model=SlotAvailabilityResponse)
async def get_available_slots(
    doctor_id: int,
    target_date: date = Query(..., description="Date to check availability (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Get available appointment slots for a doctor on a specific date"""
    
    scheduling_service = SchedulingService(db)
    
    try:
        slots = scheduling_service.get_available_slots(doctor_id, target_date)
        
        # Get doctor info
        doctor = db.query(DoctorProfile).filter(DoctorProfile.id == doctor_id).first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        
        return SlotAvailabilityResponse(
            date=target_date,
            doctor=doctor,
            available_slots=slots
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/appointments/book", response_model=BookSlotResponse)
async def book_appointment(
    booking_request: BookSlotRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Book an appointment slot"""
    
    # Only patients can book appointments
    if current_user.role != SQLUserRole.PATIENT:
        raise HTTPException(
            status_code=403, 
            detail=f"Only patients can book appointments. Current role: {current_user.role}"
        )
    
    scheduling_service = SchedulingService(db)
    
    success, appointment, error = scheduling_service.book_appointment(
        patient_id=current_user.id,
        slot_id=booking_request.slot_id,
        patient_symptoms=booking_request.patient_symptoms,
        patient_notes=booking_request.patient_notes
    )
    
    if success:
        return BookSlotResponse(
            success=True,
            appointment=appointment
        )
    else:
        return BookSlotResponse(
            success=False,
            error=error
        )

# ================================
# Appointment Management
# ================================

@router.get("/appointments/my", response_model=List[AppointmentResponse])
async def get_my_appointments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    include_past: bool = Query(False, description="Include past appointments")
):
    """Get current user's appointments"""
    
    scheduling_service = SchedulingService(db)
    role_val = _normalize_role(current_user.role)
    # Debug logging to trace role comparison issues
    print(f"[appointments/my] user_id={current_user.id} role_raw={current_user.role} role_norm={role_val} type={type(current_user.role)}")
    print(f"[appointments/my] compare PATIENT={role_val == 'PATIENT'} DOCTOR={role_val == 'DOCTOR'}")

    if role_val == 'PATIENT':
        appointments = scheduling_service.get_patient_appointments(
            patient_id=current_user.id,
            include_past=include_past
        )
    elif role_val == 'DOCTOR':
        if not current_user.doctor_profile:
            raise HTTPException(status_code=404, detail="Doctor profile not found")
        
        appointments = scheduling_service.get_doctor_appointments(
            doctor_id=current_user.doctor_profile.id,
            status_filter=None if include_past else [AppointmentStatus.SCHEDULED, AppointmentStatus.ACTIVE]
        )
    else:
        raise HTTPException(status_code=403, detail="Invalid user role")
    
    return appointments

@router.put("/appointments/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    update_request: AppointmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an appointment (status, notes, etc.)"""
    
    from ..database.models import Appointment
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Authorization: patient can update their appointment, doctor can update their patients' appointments
    role_val = _normalize_role(current_user.role)
    print(f"[appointments/update] user_id={current_user.id} role_norm={role_val}")
    if role_val == 'PATIENT':
        if appointment.patient_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
    elif role_val == 'DOCTOR':
        if appointment.doctor.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
    else:
        raise HTTPException(status_code=403, detail="Invalid user role")
    
    # Apply updates
    if update_request.status:
        appointment.status = update_request.status
        
        # Set timestamps based on status
        if update_request.status == AppointmentStatus.ACTIVE:
            appointment.started_at = datetime.now(timezone.utc)
        elif update_request.status == AppointmentStatus.COMPLETED:
            appointment.completed_at = datetime.now(timezone.utc)
        elif update_request.status == AppointmentStatus.CANCELLED:
            appointment.cancelled_at = datetime.now(timezone.utc)
    
    if update_request.doctor_notes and current_user.role == UserRole.DOCTOR:
        appointment.doctor_notes = update_request.doctor_notes
    
    if update_request.consultation_summary and current_user.role == UserRole.DOCTOR:
        appointment.consultation_summary = update_request.consultation_summary
    
    if update_request.patient_notes and current_user.role == UserRole.PATIENT:
        appointment.patient_notes = update_request.patient_notes
    
    db.commit()
    db.refresh(appointment)
    
    return appointment

@router.delete("/appointments/{appointment_id}")
async def cancel_appointment(
    appointment_id: int,
    cancel_request: CancelAppointmentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel an appointment"""
    
    from ..database.models import Appointment
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Authorization
    if current_user.role == UserRole.PATIENT:
        if appointment.patient_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
    elif current_user.role == UserRole.DOCTOR:
        if appointment.doctor.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
    
    scheduling_service = SchedulingService(db)
    
    success, error = scheduling_service.cancel_appointment(
        appointment_id=appointment_id,
        cancelled_by_user_id=current_user.id,
        reason=cancel_request.reason
    )
    
    if success:
        return {"message": "Appointment cancelled successfully"}
    else:
        raise HTTPException(status_code=400, detail=error)

# ================================
# Video Call Integration
# ================================

@router.post("/appointments/{appointment_id}/video/join", response_model=VideoCallJoinResponse)
async def join_video_call(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get video call join information for an appointment"""
    
    from ..database.models import Appointment
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Authorization: only patient or doctor can join
    user_authorized = False
    if current_user.role == UserRole.PATIENT and appointment.patient_id == current_user.id:
        user_authorized = True
    elif current_user.role == UserRole.DOCTOR and appointment.doctor.user_id == current_user.id:
        user_authorized = True
    
    if not user_authorized:
        raise HTTPException(status_code=403, detail="Not authorized to join this call")
    
    # Check appointment timing (allow joining 10 minutes before to 30 minutes after start)
    now = datetime.now(timezone.utc)
    start_time = appointment.slot.start_datetime
    end_time = appointment.slot.end_datetime
    
    if now < start_time - timedelta(minutes=10):
        raise HTTPException(status_code=400, detail="Call is not yet available")
    
    if now > end_time + timedelta(minutes=30):
        raise HTTPException(status_code=400, detail="Call has ended")
    
    # Get video service and join info
    video_service = AppointmentVideoService(db)
    
    try:
        join_info = video_service.get_join_info_for_user(appointment_id, current_user.id)
        
        # Mark appointment as started if doctor joins
        if current_user.role == UserRole.DOCTOR:
            video_service.start_consultation(appointment_id, current_user.id)
        
        return VideoCallJoinResponse(
            room_url=join_info["room_url"],
            room_name=join_info["room_name"],
            token=join_info["token"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/appointments/{appointment_id}/video/end")
async def end_video_call(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    doctor_notes: Optional[str] = None,
    consultation_summary: Optional[str] = None
):
    """End a video call and mark appointment as completed"""
    
    from ..database.models import Appointment
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Only doctor can officially end the call
    if current_user.role != UserRole.DOCTOR or appointment.doctor.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the doctor can end the consultation")
    
    video_service = AppointmentVideoService(db)
    
    success = video_service.end_consultation(
        appointment_id=appointment_id,
        ended_by_user_id=current_user.id,
        doctor_notes=doctor_notes,
        consultation_summary=consultation_summary
    )
    
    if success:
        return {"message": "Consultation ended successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to end consultation")

# ================================
# AI Integration Endpoints
# ================================

@router.post("/appointments/{appointment_id}/ai-analysis")
async def trigger_ai_analysis(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    generate_pdf: bool = True
):
    """Trigger AI analysis for a completed appointment"""
    
    from ..database.models import Appointment
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Authorization: only the doctor can trigger AI analysis
    if current_user.role != UserRole.DOCTOR or appointment.doctor.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the consulting doctor can trigger AI analysis")
    
    from .ai_integration import ConsultationAIService
    ai_service = ConsultationAIService(db)
    
    try:
        result = ai_service.trigger_post_consultation_analysis(
            appointment_id=appointment_id,
            trigger_pdf=generate_pdf
        )
        
        if result["success"]:
            return {
                "message": "AI analysis completed successfully",
                "analysis_results": result.get("analysis_results"),
                "pdf_generated": result.get("pdf_path") is not None,
                "pdf_path": result.get("pdf_path")
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "AI analysis failed"))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/appointments/{appointment_id}/ai-status")
async def get_ai_analysis_status(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI analysis status for an appointment"""
    
    from ..database.models import Appointment
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Authorization: patient or doctor can check status
    if (current_user.role == UserRole.PATIENT and appointment.patient_id != current_user.id) or \
       (current_user.role == UserRole.DOCTOR and appointment.doctor.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    from .ai_integration import ConsultationAIService
    ai_service = ConsultationAIService(db)
    
    return ai_service.get_analysis_status(appointment_id)

@router.post("/appointments/{appointment_id}/regenerate-analysis")
async def regenerate_ai_analysis(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Regenerate AI analysis and PDF for an appointment"""
    
    from ..database.models import Appointment
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Authorization: only the doctor can regenerate analysis
    if current_user.role != UserRole.DOCTOR or appointment.doctor.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the consulting doctor can regenerate analysis")
    
    from .ai_integration import ConsultationAIService
    ai_service = ConsultationAIService(db)
    
    try:
        result = ai_service.regenerate_analysis(appointment_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        if result["success"]:
            return {
                "message": "AI analysis regenerated successfully",
                "analysis_results": result.get("analysis_results"),
                "pdf_generated": result.get("pdf_path") is not None
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to regenerate analysis"))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/appointments/{appointment_id}/download-pdf")
async def download_consultation_pdf(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download PDF report for an appointment"""
    
    from ..database.models import Appointment
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Authorization: patient or doctor can download PDF
    if (current_user.role == UserRole.PATIENT and appointment.patient_id != current_user.id) or \
       (current_user.role == UserRole.DOCTOR and appointment.doctor.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if not appointment.pdf_generated or not appointment.pdf_path:
        raise HTTPException(status_code=404, detail="PDF report not available")
    
    import os
    from fastapi.responses import FileResponse
    
    if not os.path.exists(appointment.pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    return FileResponse(
        path=appointment.pdf_path,
        media_type='application/pdf',
        filename=f"consultation_report_{appointment_id}.pdf"
    )

# ================================
# Webhook Endpoints (Daily.co)
# ================================

@router.post("/webhooks/daily/join")
async def daily_join_webhook(
    webhook_data: dict,
    db: Session = Depends(get_db)
):
    """Handle Daily.co join webhook"""
    # Process webhook data when someone joins a call
    # Update appointment status, log events, etc.
    pass

@router.post("/webhooks/daily/end")
async def daily_end_webhook(
    webhook_data: dict,
    db: Session = Depends(get_db)
):
    """Handle Daily.co end webhook"""
    # Process webhook data when a call ends
    # Automatically mark appointment as completed, trigger AI analysis, etc.
    pass