from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, Time, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"
    ADMIN = "ADMIN"

class SlotStatus(enum.Enum):
    AVAILABLE = "available"
    BOOKED = "booked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class AppointmentStatus(enum.Enum):
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class DayOfWeek(enum.Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

class User(Base):
    """
    Basic user model to represent both patients and doctors
    In production, you might have separate Patient/Doctor tables
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    phone = Column(String)
    timezone = Column(String, default="Asia/Kolkata")  # Default to IST
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)

    # Relationships
    doctor_profile = relationship("DoctorProfile", back_populates="user", uselist=False)
    patient_appointments = relationship("Appointment", back_populates="patient", foreign_keys="Appointment.patient_id")

class DoctorProfile(Base):
    """
    Extended profile for doctors with scheduling preferences
    """
    __tablename__ = "doctor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    specialization = Column(String)
    experience_years = Column(Integer)
    license_number = Column(String)
    default_slot_duration_minutes = Column(Integer, default=20)  # Default 20-minute slots
    consultation_fee = Column(Float)
    bio = Column(Text)
    is_available_for_booking = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="doctor_profile")
    availabilities = relationship("DoctorAvailability", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")
    slots = relationship("AppointmentSlot", back_populates="doctor")

class DoctorAvailability(Base):
    """
    Template for doctor's recurring availability patterns
    Supports both recurring weekly patterns and specific date overrides
    """
    __tablename__ = "doctor_availabilities"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctor_profiles.id"), nullable=False)
    
    # For recurring weekly availability
    day_of_week = Column(Enum(DayOfWeek), nullable=True)  # None for specific dates
    
    # For specific date availability (overrides or one-time)
    specific_date = Column(DateTime, nullable=True)  # None for recurring patterns
    
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    slot_duration_minutes = Column(Integer)  # Override default if needed
    
    is_active = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)  # For blocking out specific times
    notes = Column(Text)  # e.g., "Holiday", "Conference", etc.
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    doctor = relationship("DoctorProfile", back_populates="availabilities")

class AppointmentSlot(Base):
    """
    Concrete time slots generated from doctor availability patterns
    These are the actual bookable slots
    """
    __tablename__ = "appointment_slots"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctor_profiles.id"), nullable=False)
    start_datetime = Column(DateTime, nullable=False)  # UTC timezone
    end_datetime = Column(DateTime, nullable=False)    # UTC timezone
    status = Column(Enum(SlotStatus), default=SlotStatus.AVAILABLE, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    
    # Generation metadata
    generated_from_availability_id = Column(Integer, ForeignKey("doctor_availabilities.id"))
    generation_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    doctor = relationship("DoctorProfile", back_populates="slots")
    appointment = relationship("Appointment", back_populates="slot", uselist=False)

class Appointment(Base):
    """
    Represents a booked consultation session between patient and doctor
    """
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctor_profiles.id"), nullable=False)
    slot_id = Column(Integer, ForeignKey("appointment_slots.id"), unique=True, nullable=False)
    
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED, nullable=False)
    
    # Patient information at time of booking
    patient_symptoms = Column(Text)
    patient_notes = Column(Text)
    
    # Doctor notes after consultation
    doctor_notes = Column(Text)
    consultation_summary = Column(Text)
    
    # Daily.co integration
    daily_room_name = Column(String, unique=True)
    daily_room_url = Column(String)
    daily_room_created_at = Column(DateTime)
    
    # AI integration
    ai_analysis_triggered = Column(Boolean, default=False)
    pdf_generated = Column(Boolean, default=False)
    pdf_path = Column(String)
    
    # Timestamps
    booked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    cancelled_at = Column(DateTime)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    patient = relationship("User", back_populates="patient_appointments", foreign_keys=[patient_id])
    doctor = relationship("DoctorProfile", back_populates="appointments")
    slot = relationship("AppointmentSlot", back_populates="appointment")

class AppointmentHistory(Base):
    """
    Audit trail for appointment status changes
    """
    __tablename__ = "appointment_history"

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=False)
    old_status = Column(Enum(AppointmentStatus))
    new_status = Column(Enum(AppointmentStatus), nullable=False)
    changed_by_user_id = Column(Integer, ForeignKey("users.id"))
    reason = Column(Text)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))