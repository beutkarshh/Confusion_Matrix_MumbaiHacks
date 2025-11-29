from datetime import datetime, timedelta, time, timezone, date
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import pytz

from ..database.models import (
    DoctorProfile, DoctorAvailability, AppointmentSlot, 
    Appointment, DayOfWeek, SlotStatus, AppointmentStatus
)
from .schemas import DoctorAvailabilityCreate, AppointmentSlotCreate

class SlotGenerationService:
    """
    Service responsible for generating concrete time slots from doctor availability patterns
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_slots_for_doctor(
        self, 
        doctor_id: int, 
        start_date: date, 
        end_date: date,
        force_regenerate: bool = False
    ) -> List[AppointmentSlot]:
        """
        Generate appointment slots for a doctor within a date range
        
        Args:
            doctor_id: ID of the doctor
            start_date: Start date for slot generation
            end_date: End date for slot generation (inclusive)
            force_regenerate: If True, delete existing slots and regenerate
        
        Returns:
            List of generated AppointmentSlot objects
        """
        # Get doctor profile
        doctor = self.db.query(DoctorProfile).filter(DoctorProfile.id == doctor_id).first()
        if not doctor:
            raise ValueError(f"Doctor with ID {doctor_id} not found")
        
        if not doctor.is_available_for_booking:
            raise ValueError(f"Doctor {doctor_id} is not available for booking")
        
        # Get doctor's timezone
        doctor_tz = pytz.timezone(doctor.user.timezone)
        
        # If force_regenerate, delete existing slots in the range
        if force_regenerate:
            self._delete_existing_slots(doctor_id, start_date, end_date, doctor_tz)
        
        # Get doctor's availability patterns
        availabilities = self.db.query(DoctorAvailability).filter(
            and_(
                DoctorAvailability.doctor_id == doctor_id,
                DoctorAvailability.is_active == True,
                DoctorAvailability.is_blocked == False
            )
        ).all()
        
        generated_slots = []
        current_date = start_date
        
        while current_date <= end_date:
            # Skip past dates
            if current_date < date.today():
                current_date += timedelta(days=1)
                continue
            
            # Generate slots for this specific date
            day_slots = self._generate_slots_for_date(
                doctor, current_date, availabilities, doctor_tz
            )
            generated_slots.extend(day_slots)
            
            current_date += timedelta(days=1)
        
        return generated_slots
    
    def _delete_existing_slots(
        self, 
        doctor_id: int, 
        start_date: date, 
        end_date: date,
        doctor_tz: pytz.BaseTzInfo
    ):
        """Delete existing available slots in the date range"""
        # Convert date range to UTC datetime range
        start_dt = doctor_tz.localize(
            datetime.combine(start_date, time.min)
        ).astimezone(pytz.UTC)
        
        end_dt = doctor_tz.localize(
            datetime.combine(end_date, time(23, 59, 59))
        ).astimezone(pytz.UTC)
        
        # Only delete AVAILABLE slots - don't touch booked/completed slots
        self.db.query(AppointmentSlot).filter(
            and_(
                AppointmentSlot.doctor_id == doctor_id,
                AppointmentSlot.start_datetime >= start_dt,
                AppointmentSlot.start_datetime <= end_dt,
                AppointmentSlot.status == SlotStatus.AVAILABLE
            )
        ).delete()
        
        self.db.commit()
    
    def _generate_slots_for_date(
        self, 
        doctor: DoctorProfile, 
        target_date: date,
        availabilities: List[DoctorAvailability],
        doctor_tz: pytz.BaseTzInfo
    ) -> List[AppointmentSlot]:
        """Generate slots for a specific date based on availability patterns"""
        
        day_of_week = DayOfWeek(target_date.weekday())
        generated_slots = []
        
        # Check for specific date availability first (overrides weekly pattern)
        specific_availabilities = [
            av for av in availabilities 
            if av.specific_date and av.specific_date.date() == target_date
        ]
        
        if specific_availabilities:
            # Use specific date availability
            for availability in specific_availabilities:
                slots = self._create_slots_from_availability(
                    doctor, availability, target_date, doctor_tz
                )
                generated_slots.extend(slots)
        else:
            # Use weekly recurring patterns
            weekly_availabilities = [
                av for av in availabilities 
                if av.day_of_week == day_of_week and av.specific_date is None
            ]
            
            for availability in weekly_availabilities:
                slots = self._create_slots_from_availability(
                    doctor, availability, target_date, doctor_tz
                )
                generated_slots.extend(slots)
        
        return generated_slots
    
    def _create_slots_from_availability(
        self, 
        doctor: DoctorProfile, 
        availability: DoctorAvailability,
        target_date: date,
        doctor_tz: pytz.BaseTzInfo
    ) -> List[AppointmentSlot]:
        """Create individual slots from an availability pattern"""
        
        slots = []
        
        # Determine slot duration
        duration_minutes = (
            availability.slot_duration_minutes or 
            doctor.default_slot_duration_minutes
        )
        
        # Create datetime objects in doctor's timezone
        start_dt = doctor_tz.localize(
            datetime.combine(target_date, availability.start_time)
        )
        end_dt = doctor_tz.localize(
            datetime.combine(target_date, availability.end_time)
        )
        
        # Generate slots within the time range
        current_dt = start_dt
        slot_duration = timedelta(minutes=duration_minutes)
        
        while current_dt + slot_duration <= end_dt:
            # Skip if slot is in the past
            if current_dt.astimezone(pytz.UTC) <= datetime.now(pytz.UTC):
                current_dt += slot_duration
                continue
            
            # Check if slot already exists and is not available
            existing_slot = self.db.query(AppointmentSlot).filter(
                and_(
                    AppointmentSlot.doctor_id == doctor.id,
                    AppointmentSlot.start_datetime == current_dt.astimezone(pytz.UTC)
                )
            ).first()
            
            if existing_slot and existing_slot.status != SlotStatus.AVAILABLE:
                # Slot exists and is booked/completed - skip
                current_dt += slot_duration
                continue
            
            if not existing_slot:
                # Create new slot
                slot = AppointmentSlot(
                    doctor_id=doctor.id,
                    start_datetime=current_dt.astimezone(pytz.UTC),
                    end_datetime=(current_dt + slot_duration).astimezone(pytz.UTC),
                    duration_minutes=duration_minutes,
                    status=SlotStatus.AVAILABLE,
                    generated_from_availability_id=availability.id
                )
                
                self.db.add(slot)
                slots.append(slot)
            
            current_dt += slot_duration
        
        self.db.commit()
        return slots


class SchedulingService:
    """
    Main service for scheduling operations
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.slot_generator = SlotGenerationService(db)
    
    def get_available_slots(
        self, 
        doctor_id: int, 
        target_date: date
    ) -> List[AppointmentSlot]:
        """Get available slots for a doctor on a specific date"""
        
        # Get doctor timezone
        doctor = self.db.query(DoctorProfile).filter(DoctorProfile.id == doctor_id).first()
        if not doctor:
            raise ValueError(f"Doctor with ID {doctor_id} not found")
        
        doctor_tz = pytz.timezone(doctor.user.timezone)
        
        # Convert date to UTC datetime range
        start_dt = doctor_tz.localize(
            datetime.combine(target_date, time.min)
        ).astimezone(pytz.UTC)
        
        end_dt = doctor_tz.localize(
            datetime.combine(target_date, time(23, 59, 59))
        ).astimezone(pytz.UTC)
        
        # Query available slots
        slots = self.db.query(AppointmentSlot).filter(
            and_(
                AppointmentSlot.doctor_id == doctor_id,
                AppointmentSlot.start_datetime >= start_dt,
                AppointmentSlot.start_datetime <= end_dt,
                AppointmentSlot.status == SlotStatus.AVAILABLE,
                AppointmentSlot.start_datetime > datetime.now(timezone.utc)  # Future slots only
            )
        ).order_by(AppointmentSlot.start_datetime).all()
        
        return slots
    
    def book_appointment(
        self, 
        patient_id: int, 
        slot_id: int, 
        patient_symptoms: Optional[str] = None,
        patient_notes: Optional[str] = None
    ) -> Tuple[bool, Optional[Appointment], Optional[str]]:
        """
        Book an appointment slot for a patient
        
        Returns:
            (success, appointment_object, error_message)
        """
        try:
            # Get the slot
            slot = self.db.query(AppointmentSlot).filter(AppointmentSlot.id == slot_id).first()
            if not slot:
                return False, None, "Slot not found"
            
            # Check if slot is available
            if slot.status != SlotStatus.AVAILABLE:
                return False, None, "Slot is no longer available"
            
            # Check if slot is in the future
            # Ensure start_datetime is timezone aware
            slot_datetime = slot.start_datetime
            if slot_datetime.tzinfo is None:
                slot_datetime = pytz.UTC.localize(slot_datetime)
            
            if slot_datetime <= datetime.now(timezone.utc):
                return False, None, "Cannot book appointments in the past"
            
            # Check if patient exists
            from ..database.models import User
            patient = self.db.query(User).filter(User.id == patient_id).first()
            if not patient:
                return False, None, "Patient not found"
            
            # Create appointment
            appointment = Appointment(
                patient_id=patient_id,
                doctor_id=slot.doctor_id,
                slot_id=slot_id,
                status=AppointmentStatus.SCHEDULED,
                patient_symptoms=patient_symptoms,
                patient_notes=patient_notes
            )
            
            # Mark slot as booked
            slot.status = SlotStatus.BOOKED
            
            # Add to database
            self.db.add(appointment)
            self.db.commit()
            self.db.refresh(appointment)
            
            return True, appointment, None
            
        except Exception as e:
            self.db.rollback()
            return False, None, f"Booking failed: {str(e)}"
    
    def cancel_appointment(
        self, 
        appointment_id: int, 
        cancelled_by_user_id: int,
        reason: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """Cancel an appointment and optionally free up the slot"""
        
        try:
            appointment = self.db.query(Appointment).filter(Appointment.id == appointment_id).first()
            if not appointment:
                return False, "Appointment not found"
            
            if appointment.status in [AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED]:
                return False, "Appointment is already completed or cancelled"
            
            # Check cancellation policy (e.g., no cancellation within 30 minutes)
            if appointment.slot.start_datetime - datetime.now(pytz.UTC) < timedelta(minutes=30):
                return False, "Cannot cancel appointment within 30 minutes of start time"
            
            # Update appointment status
            appointment.status = AppointmentStatus.CANCELLED
            appointment.cancelled_at = datetime.now(pytz.UTC)
            
            # Free up the slot
            appointment.slot.status = SlotStatus.AVAILABLE
            
            # Log the cancellation
            from ..database.models import AppointmentHistory
            history = AppointmentHistory(
                appointment_id=appointment_id,
                old_status=AppointmentStatus.SCHEDULED,
                new_status=AppointmentStatus.CANCELLED,
                changed_by_user_id=cancelled_by_user_id,
                reason=reason
            )
            self.db.add(history)
            
            self.db.commit()
            return True, None
            
        except Exception as e:
            self.db.rollback()
            return False, f"Cancellation failed: {str(e)}"
    
    def get_doctor_appointments(
        self, 
        doctor_id: int, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status_filter: Optional[List[AppointmentStatus]] = None
    ) -> List[Appointment]:
        """Get appointments for a doctor within date range and status filters"""
        
        query = self.db.query(Appointment).filter(Appointment.doctor_id == doctor_id)
        
        if start_date:
            doctor = self.db.query(DoctorProfile).filter(DoctorProfile.id == doctor_id).first()
            doctor_tz = pytz.timezone(doctor.user.timezone)
            start_dt = doctor_tz.localize(
                datetime.combine(start_date, time.min)
            ).astimezone(pytz.UTC)
            query = query.join(AppointmentSlot).filter(AppointmentSlot.start_datetime >= start_dt)
        
        if end_date:
            doctor = self.db.query(DoctorProfile).filter(DoctorProfile.id == doctor_id).first()
            doctor_tz = pytz.timezone(doctor.user.timezone)
            end_dt = doctor_tz.localize(
                datetime.combine(end_date, time(23, 59, 59))
            ).astimezone(pytz.UTC)
            query = query.join(AppointmentSlot).filter(AppointmentSlot.start_datetime <= end_dt)
        
        if status_filter:
            query = query.filter(Appointment.status.in_(status_filter))
        
        return query.order_by(AppointmentSlot.start_datetime).all()
    
    def get_patient_appointments(
        self, 
        patient_id: int,
        include_past: bool = False
    ) -> List[Appointment]:
        """Get appointments for a patient"""
        
        query = self.db.query(Appointment).filter(Appointment.patient_id == patient_id)
        
        if not include_past:
            query = query.join(AppointmentSlot).filter(
                AppointmentSlot.start_datetime > datetime.now(pytz.UTC)
            )
        
        return query.order_by(AppointmentSlot.start_datetime).all()