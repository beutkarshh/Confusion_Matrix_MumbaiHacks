from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ..database.config import get_db
from ..database.models import AppointmentStatus
from .schemas import DoctorProfileResponse, BookSlotRequest, BookSlotResponse, AppointmentResponse

router = APIRouter(prefix="/api/scheduling-demo", tags=["Scheduling-Demo"])

# In-memory demo store (per-process)
_DEMO_APPOINTMENTS = []

@router.get("/doctors/{doctor_id}/slots", response_model=dict)
def demo_slots(doctor_id: int, target_date: str, db: Session = Depends(get_db)):
    # Produce deterministic slots for the given doctor/date
    base = datetime.fromisoformat(target_date + "T03:50:00")
    slots = []
    for i in range(0, 10):
        start_dt = base + timedelta(minutes=20 * i)
        slot = {
            "id": i + 1000,  # demo ids distinct from real
            "doctor_id": doctor_id,
            "start_datetime": start_dt.isoformat(timespec="seconds"),
            "end_datetime": (start_dt + timedelta(minutes=20)).isoformat(timespec="seconds"),
            "duration_minutes": 20,
            "status": "available",
            "is_past": False,
        }
        slots.append(slot)
    return {
        "demo": True,
        "date": target_date,
        "doctor": {"id": doctor_id},
        "available_slots": slots,
    }

@router.post("/appointments/book", response_model=BookSlotResponse)
def demo_book(req: BookSlotRequest, db: Session = Depends(get_db)):
    appt_id = len(_DEMO_APPOINTMENTS) + 1
    now = datetime.now().isoformat(timespec="seconds")
    appointment = {
        "id": appt_id,
        "patient_id": 5,  # demo patient
        "doctor_id": 1,
        "slot_id": req.slot_id,
        "status": "scheduled",
        "patient_symptoms": req.patient_symptoms,
        "patient_notes": req.patient_notes,
        "booked_at": now,
        "started_at": None,
        "completed_at": None,
        "cancelled_at": None,
        "slot": {
            "id": req.slot_id,
            "doctor_id": 1,
            "start_datetime": now,
            "end_datetime": (datetime.now() + timedelta(minutes=20)).isoformat(timespec="seconds"),
            "duration_minutes": 20,
            "status": "booked",
            "is_past": False,
        },
    }
    _DEMO_APPOINTMENTS.append(appointment)
    return BookSlotResponse(success=True, appointment=appointment, error=None)

@router.get("/appointments/my", response_model=list[AppointmentResponse])
def demo_my_appointments(db: Session = Depends(get_db)):
    # Return whatever was booked in demo
    return _DEMO_APPOINTMENTS
