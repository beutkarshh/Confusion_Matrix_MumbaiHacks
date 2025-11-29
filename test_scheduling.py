import pytest
from datetime import datetime, date, time, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os

from backend.database.config import Base
from backend.database.models import User, DoctorProfile, DoctorAvailability, AppointmentSlot, Appointment, UserRole, DayOfWeek, SlotStatus, AppointmentStatus
from backend.scheduling.services import SchedulingService, SlotGenerationService

# Test database setup
@pytest.fixture(scope="function")
def test_db():
    # Create temporary database
    temp_db = tempfile.NamedTemporaryFile(delete=False)
    temp_db.close()
    
    engine = create_engine(f"sqlite:///{temp_db.name}")
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    yield db
    
    db.close()
    os.unlink(temp_db.name)

@pytest.fixture
def sample_doctor(test_db):
    """Create a sample doctor for testing"""
    user = User(
        email="doctor@test.com",
        name="Dr. Test",
        role=UserRole.DOCTOR,
        timezone="Asia/Kolkata"
    )
    test_db.add(user)
    test_db.flush()
    
    doctor = DoctorProfile(
        user_id=user.id,
        specialization="General Medicine",
        experience_years=5,
        default_slot_duration_minutes=20,
        consultation_fee=500.0,
        is_available_for_booking=True
    )
    test_db.add(doctor)
    test_db.commit()
    
    return doctor

@pytest.fixture
def sample_patient(test_db):
    """Create a sample patient for testing"""
    patient = User(
        email="patient@test.com",
        name="Test Patient",
        role=UserRole.PATIENT,
        timezone="Asia/Kolkata"
    )
    test_db.add(patient)
    test_db.commit()
    
    return patient

@pytest.fixture
def doctor_availability(test_db, sample_doctor):
    """Create sample availability for the doctor"""
    availability = DoctorAvailability(
        doctor_id=sample_doctor.id,
        day_of_week=DayOfWeek.MONDAY,
        start_time=time(9, 0),
        end_time=time(17, 0),
        slot_duration_minutes=20,
        is_active=True,
        is_blocked=False
    )
    test_db.add(availability)
    test_db.commit()
    
    return availability

class TestSlotGeneration:
    """Test slot generation functionality"""
    
    def test_generate_slots_basic(self, test_db, sample_doctor, doctor_availability):
        """Test basic slot generation"""
        slot_service = SlotGenerationService(test_db)
        
        # Generate slots for tomorrow (Monday)
        tomorrow = date.today() + timedelta(days=1)
        # Ensure tomorrow is Monday for this test
        while tomorrow.weekday() != 0:  # 0 = Monday
            tomorrow += timedelta(days=1)
        
        slots = slot_service.generate_slots_for_doctor(
            doctor_id=sample_doctor.id,
            start_date=tomorrow,
            end_date=tomorrow
        )
        
        assert len(slots) > 0
        
        # Check slot properties
        for slot in slots:
            assert slot.doctor_id == sample_doctor.id
            assert slot.status == SlotStatus.AVAILABLE
            assert slot.duration_minutes == 20
    
    def test_no_past_slots_generated(self, test_db, sample_doctor, doctor_availability):
        """Test that no slots are generated for past dates"""
        slot_service = SlotGenerationService(test_db)
        
        yesterday = date.today() - timedelta(days=1)
        
        slots = slot_service.generate_slots_for_doctor(
            doctor_id=sample_doctor.id,
            start_date=yesterday,
            end_date=yesterday
        )
        
        # Should be empty or only contain future slots
        for slot in slots:
            assert slot.start_datetime > datetime.now(timezone.utc)

class TestBookingLogic:
    """Test appointment booking functionality"""
    
    def test_successful_booking(self, test_db, sample_doctor, sample_patient, doctor_availability):
        """Test successful appointment booking"""
        # Generate slots first
        slot_service = SlotGenerationService(test_db)
        tomorrow = date.today() + timedelta(days=1)
        while tomorrow.weekday() != 0:  # Ensure Monday
            tomorrow += timedelta(days=1)
        
        slots = slot_service.generate_slots_for_doctor(
            doctor_id=sample_doctor.id,
            start_date=tomorrow,
            end_date=tomorrow
        )
        
        assert len(slots) > 0
        slot = slots[0]
        
        # Book the slot
        scheduling_service = SchedulingService(test_db)
        success, appointment, error = scheduling_service.book_appointment(
            patient_id=sample_patient.id,
            slot_id=slot.id,
            patient_symptoms="Test symptoms",
            patient_notes="Test notes"
        )
        
        assert success
        assert appointment is not None
        assert error is None
        assert appointment.patient_id == sample_patient.id
        assert appointment.doctor_id == sample_doctor.id
        assert appointment.slot_id == slot.id
        assert appointment.status == AppointmentStatus.SCHEDULED
        
        # Check that slot is marked as booked
        test_db.refresh(slot)
        assert slot.status == SlotStatus.BOOKED
    
    def test_double_booking_prevention(self, test_db, sample_doctor, sample_patient, doctor_availability):
        """Test that double booking is prevented"""
        # Generate slots
        slot_service = SlotGenerationService(test_db)
        tomorrow = date.today() + timedelta(days=1)
        while tomorrow.weekday() != 0:
            tomorrow += timedelta(days=1)
        
        slots = slot_service.generate_slots_for_doctor(
            doctor_id=sample_doctor.id,
            start_date=tomorrow,
            end_date=tomorrow
        )
        
        slot = slots[0]
        scheduling_service = SchedulingService(test_db)
        
        # First booking
        success1, _, _ = scheduling_service.book_appointment(
            patient_id=sample_patient.id,
            slot_id=slot.id
        )
        assert success1
        
        # Create another patient
        patient2 = User(
            email="patient2@test.com",
            name="Test Patient 2",
            role=UserRole.PATIENT
        )
        test_db.add(patient2)
        test_db.commit()
        
        # Second booking (should fail)
        success2, appointment2, error2 = scheduling_service.book_appointment(
            patient_id=patient2.id,
            slot_id=slot.id
        )
        
        assert not success2
        assert appointment2 is None
        assert "no longer available" in error2.lower()

class TestAvailabilityLogic:
    """Test doctor availability management"""
    
    def test_get_available_slots(self, test_db, sample_doctor, doctor_availability):
        """Test retrieving available slots for a date"""
        # Generate slots
        slot_service = SlotGenerationService(test_db)
        tomorrow = date.today() + timedelta(days=1)
        while tomorrow.weekday() != 0:
            tomorrow += timedelta(days=1)
        
        slot_service.generate_slots_for_doctor(
            doctor_id=sample_doctor.id,
            start_date=tomorrow,
            end_date=tomorrow
        )
        
        # Get available slots
        scheduling_service = SchedulingService(test_db)
        available_slots = scheduling_service.get_available_slots(
            doctor_id=sample_doctor.id,
            target_date=tomorrow
        )
        
        assert len(available_slots) > 0
        for slot in available_slots:
            assert slot.status == SlotStatus.AVAILABLE
            assert slot.doctor_id == sample_doctor.id
    
    def test_cancellation_policy(self, test_db, sample_doctor, sample_patient, doctor_availability):
        """Test appointment cancellation logic"""
        # Create a future slot and book it
        slot_service = SlotGenerationService(test_db)
        tomorrow = date.today() + timedelta(days=1)
        while tomorrow.weekday() != 0:
            tomorrow += timedelta(days=1)
        
        slots = slot_service.generate_slots_for_doctor(
            doctor_id=sample_doctor.id,
            start_date=tomorrow,
            end_date=tomorrow
        )
        
        scheduling_service = SchedulingService(test_db)
        success, appointment, _ = scheduling_service.book_appointment(
            patient_id=sample_patient.id,
            slot_id=slots[0].id
        )
        assert success
        
        # Cancel the appointment
        cancel_success, cancel_error = scheduling_service.cancel_appointment(
            appointment_id=appointment.id,
            cancelled_by_user_id=sample_patient.id,
            reason="Test cancellation"
        )
        
        assert cancel_success
        assert cancel_error is None
        
        # Check appointment status
        test_db.refresh(appointment)
        assert appointment.status == AppointmentStatus.CANCELLED
        
        # Check slot status
        slot = test_db.query(AppointmentSlot).filter(AppointmentSlot.id == slots[0].id).first()
        assert slot.status == SlotStatus.AVAILABLE  # Should be available again