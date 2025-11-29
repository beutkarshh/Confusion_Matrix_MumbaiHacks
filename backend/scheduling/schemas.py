from pydantic import BaseModel, Field, validator
from datetime import datetime, time, date
from typing import Optional, List
from enum import Enum

# Enums matching SQLAlchemy models
class UserRole(str, Enum):
    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"
    ADMIN = "ADMIN"

class SlotStatus(str, Enum):
    AVAILABLE = "available"
    BOOKED = "booked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class DayOfWeek(int, Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

# Base schemas
class UserBase(BaseModel):
    email: str
    name: str
    role: UserRole
    phone: Optional[str] = None
    timezone: str = "Asia/Kolkata"

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class DoctorProfileBase(BaseModel):
    specialization: Optional[str] = None
    experience_years: Optional[int] = None
    license_number: Optional[str] = None
    default_slot_duration_minutes: int = 20
    consultation_fee: Optional[float] = None
    bio: Optional[str] = None
    is_available_for_booking: bool = True

class DoctorProfileCreate(DoctorProfileBase):
    user_id: int

class DoctorProfileUpdate(BaseModel):
    specialization: Optional[str] = None
    experience_years: Optional[int] = None
    default_slot_duration_minutes: Optional[int] = None
    consultation_fee: Optional[float] = None
    bio: Optional[str] = None
    is_available_for_booking: Optional[bool] = None

class DoctorProfileResponse(DoctorProfileBase):
    id: int
    user_id: int
    user: UserResponse
    created_at: datetime

    class Config:
        from_attributes = True

# Availability schemas
class DoctorAvailabilityBase(BaseModel):
    day_of_week: Optional[DayOfWeek] = None
    specific_date: Optional[datetime] = None
    start_time: time
    end_time: time
    slot_duration_minutes: Optional[int] = None
    is_active: bool = True
    is_blocked: bool = False
    notes: Optional[str] = None

    @validator('specific_date')
    def validate_date_or_day(cls, v, values):
        # Either day_of_week OR specific_date should be set, not both
        if v is not None and values.get('day_of_week') is not None:
            raise ValueError('Cannot set both day_of_week and specific_date')
        if v is None and values.get('day_of_week') is None:
            raise ValueError('Must set either day_of_week or specific_date')
        return v

class DoctorAvailabilityCreate(DoctorAvailabilityBase):
    doctor_id: int

class DoctorAvailabilityUpdate(BaseModel):
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    slot_duration_minutes: Optional[int] = None
    is_active: Optional[bool] = None
    is_blocked: Optional[bool] = None
    notes: Optional[str] = None

class DoctorAvailabilityResponse(DoctorAvailabilityBase):
    id: int
    doctor_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Slot schemas
class AppointmentSlotBase(BaseModel):
    doctor_id: int
    start_datetime: datetime
    end_datetime: datetime
    duration_minutes: int
    status: SlotStatus = SlotStatus.AVAILABLE

class AppointmentSlotCreate(AppointmentSlotBase):
    generated_from_availability_id: Optional[int] = None

class AppointmentSlotResponse(AppointmentSlotBase):
    id: int
    doctor: DoctorProfileResponse
    is_past: bool = False

    class Config:
        from_attributes = True

# Appointment schemas
class AppointmentBase(BaseModel):
    patient_symptoms: Optional[str] = None
    patient_notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    patient_id: int
    doctor_id: int
    slot_id: int

class AppointmentUpdate(BaseModel):
    status: Optional[AppointmentStatus] = None
    doctor_notes: Optional[str] = None
    consultation_summary: Optional[str] = None
    patient_notes: Optional[str] = None

class AppointmentResponse(AppointmentBase):
    id: int
    patient_id: int
    doctor_id: int
    slot_id: int
    status: AppointmentStatus
    doctor_notes: Optional[str] = None
    consultation_summary: Optional[str] = None
    daily_room_name: Optional[str] = None
    daily_room_url: Optional[str] = None
    ai_analysis_triggered: bool
    pdf_generated: bool
    booked_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    
    # Related data
    patient: UserResponse
    doctor: DoctorProfileResponse
    slot: AppointmentSlotResponse

    class Config:
        from_attributes = True

# Request/Response schemas for API endpoints
class SlotAvailabilityRequest(BaseModel):
    doctor_id: int
    date: date

class SlotAvailabilityResponse(BaseModel):
    date: date
    doctor: DoctorProfileResponse
    available_slots: List[AppointmentSlotResponse]

class BookSlotRequest(BaseModel):
    slot_id: int
    patient_symptoms: Optional[str] = None
    patient_notes: Optional[str] = None

class BookSlotResponse(BaseModel):
    success: bool
    appointment: Optional[AppointmentResponse] = None
    error: Optional[str] = None

class CancelAppointmentRequest(BaseModel):
    reason: Optional[str] = None

class DoctorScheduleRequest(BaseModel):
    """Request to set up doctor's weekly availability"""
    availability_patterns: List[DoctorAvailabilityCreate]
    generate_slots_for_weeks: int = 4  # Generate slots for next 4 weeks by default

class GenerateSlotsRequest(BaseModel):
    doctor_id: int
    start_date: date
    end_date: date
    force_regenerate: bool = False  # Regenerate even if slots already exist

class VideoCallJoinRequest(BaseModel):
    appointment_id: int

class VideoCallJoinResponse(BaseModel):
    room_url: str
    room_name: str
    token: Optional[str] = None  # Daily.co token for secure access

# Bulk operations
class BulkSlotUpdateRequest(BaseModel):
    slot_ids: List[int]
    new_status: SlotStatus
    reason: Optional[str] = None