import os
import requests
import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from ..database.models import Appointment, AppointmentStatus

class DailyVideoService:
    """
    Service for integrating with Daily.co video calling platform
    """
    
    def __init__(self):
        self.api_key = os.getenv("DAILY_API_KEY")
        self.api_url = "https://api.daily.co/v1"
        
        if not self.api_key:
            raise ValueError(
                "DAILY_API_KEY environment variable is required. "
                "Get your API key from https://dashboard.daily.co/"
            )
    
    def create_room(self, appointment_id: int, expires_at: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Create a Daily.co room for an appointment
        
        Args:
            appointment_id: The appointment ID
            expires_at: When the room should expire (default: 24 hours from now)
        
        Returns:
            Dictionary containing room information
        """
        if not expires_at:
            expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        
        # Generate unique room name
        room_name = f"consultation-{appointment_id}-{uuid.uuid4().hex[:8]}"
        
        room_config = {
            "name": room_name,
            "privacy": "private",  # Room is private by default
            "properties": {
                "max_participants": 2,  # Doctor + Patient
                "enable_chat": True,
                "enable_screenshare": True,
                "start_video_off": False,
                "start_audio_off": False,
                "exp": int(expires_at.timestamp()),  # Room expiration
                "eject_at_room_exp": True,
                "enable_recording": "cloud",  # Enable cloud recording
                "meeting_join_hook": self._get_webhook_url("join"),
                "meeting_end_hook": self._get_webhook_url("end"),
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{self.api_url}/rooms",
            json=room_config,
            headers=headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to create Daily room: {response.text}")
        
        return response.json()
    
    def get_room(self, room_name: str) -> Dict[str, Any]:
        """Get room information"""
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        response = requests.get(
            f"{self.api_url}/rooms/{room_name}",
            headers=headers
        )
        
        if response.status_code == 404:
            return None
        elif response.status_code != 200:
            raise Exception(f"Failed to get room info: {response.text}")
        
        return response.json()
    
    def delete_room(self, room_name: str) -> bool:
        """Delete a room"""
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        response = requests.delete(
            f"{self.api_url}/rooms/{room_name}",
            headers=headers
        )
        
        return response.status_code == 200
    
    def create_meeting_token(
        self, 
        room_name: str, 
        user_id: str, 
        user_name: str,
        is_owner: bool = False,
        expires_in_seconds: int = 3600
    ) -> str:
        """
        Create a meeting token for a user to join a room
        
        Args:
            room_name: Name of the room
            user_id: Unique identifier for the user
            user_name: Display name for the user
            is_owner: Whether user has owner permissions
            expires_in_seconds: Token expiration (default 1 hour)
        
        Returns:
            Meeting token string
        """
        exp = datetime.now(timezone.utc) + timedelta(seconds=expires_in_seconds)
        
        token_config = {
            "properties": {
                "room_name": room_name,
                "user_id": user_id,
                "user_name": user_name,
                "is_owner": is_owner,
                "start_video_off": False,
                "start_audio_off": False,
                "exp": int(exp.timestamp())
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{self.api_url}/meeting-tokens",
            json=token_config,
            headers=headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to create meeting token: {response.text}")
        
        return response.json()["token"]
    
    def _get_webhook_url(self, event_type: str) -> str:
        """Get webhook URL for Daily.co events"""
        base_url = os.getenv("WEBHOOK_BASE_URL", "http://localhost:8000")
        return f"{base_url}/webhooks/daily/{event_type}"

class AppointmentVideoService:
    """
    Service for managing video calls in the context of appointments
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.daily_service = DailyVideoService()
    
    def setup_video_call(self, appointment_id: int) -> Dict[str, Any]:
        """
        Set up a video call for an appointment
        
        Returns:
            Dictionary with room information
        """
        appointment = self.db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise ValueError(f"Appointment {appointment_id} not found")
        
        # Check if room already exists
        if appointment.daily_room_name:
            existing_room = self.daily_service.get_room(appointment.daily_room_name)
            if existing_room:
                return existing_room
        
        # Create new room
        room_expires_at = appointment.slot.start_datetime + timedelta(hours=2)  # 2 hours after appointment start
        room_info = self.daily_service.create_room(appointment_id, room_expires_at)
        
        # Update appointment with room information
        appointment.daily_room_name = room_info["name"]
        appointment.daily_room_url = room_info["url"]
        appointment.daily_room_created_at = datetime.now(timezone.utc)
        
        self.db.commit()
        
        return room_info
    
    def get_join_info_for_user(
        self, 
        appointment_id: int, 
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get video call join information for a specific user
        
        Returns:
            Dictionary with room URL and token
        """
        appointment = self.db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise ValueError(f"Appointment {appointment_id} not found")
        
        # Verify user is authorized (patient or doctor)
        if user_id not in [appointment.patient_id, appointment.doctor.user_id]:
            raise ValueError("User is not authorized to join this appointment")
        
        # Ensure room exists
        if not appointment.daily_room_name:
            room_info = self.setup_video_call(appointment_id)
            room_name = room_info["name"]
            room_url = room_info["url"]
        else:
            room_name = appointment.daily_room_name
            room_url = appointment.daily_room_url
        
        # Determine user role and details
        if user_id == appointment.doctor.user_id:
            user_name = f"Dr. {appointment.doctor.user.name}"
            is_owner = True
        else:
            user_name = appointment.patient.name
            is_owner = False
        
        # Create meeting token
        token = self.daily_service.create_meeting_token(
            room_name=room_name,
            user_id=str(user_id),
            user_name=user_name,
            is_owner=is_owner,
            expires_in_seconds=3600  # 1 hour
        )
        
        return {
            "room_url": room_url,
            "room_name": room_name,
            "token": token,
            "user_name": user_name,
            "is_owner": is_owner
        }
    
    def start_consultation(self, appointment_id: int, started_by_user_id: int) -> bool:
        """Mark appointment as active when video call starts"""
        appointment = self.db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            return False
        
        if appointment.status == AppointmentStatus.SCHEDULED:
            appointment.status = AppointmentStatus.ACTIVE
            appointment.started_at = datetime.now(timezone.utc)
            self.db.commit()
        
        return True
    
    def end_consultation(
        self, 
        appointment_id: int, 
        ended_by_user_id: int,
        doctor_notes: Optional[str] = None,
        consultation_summary: Optional[str] = None
    ) -> bool:
        """Mark appointment as completed when video call ends"""
        appointment = self.db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            return False
        
        if appointment.status == AppointmentStatus.ACTIVE:
            appointment.status = AppointmentStatus.COMPLETED
            appointment.completed_at = datetime.now(timezone.utc)
            
            if doctor_notes:
                appointment.doctor_notes = doctor_notes
            if consultation_summary:
                appointment.consultation_summary = consultation_summary
            
            # Mark slot as completed
            appointment.slot.status = SlotStatus.COMPLETED
            
            self.db.commit()
        
        return True
    
    def cleanup_expired_rooms(self):
        """Clean up expired rooms and update appointment statuses"""
        # This would typically be run as a background job
        expired_appointments = self.db.query(Appointment).filter(
            and_(
                Appointment.daily_room_name.isnot(None),
                Appointment.slot.end_datetime < datetime.now(timezone.utc) - timedelta(hours=1),
                Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.ACTIVE])
            )
        ).all()
        
        for appointment in expired_appointments:
            # Try to delete the room
            try:
                self.daily_service.delete_room(appointment.daily_room_name)
            except:
                pass  # Room might already be deleted
            
            # Mark appointment as no-show if it was never started
            if appointment.status == AppointmentStatus.SCHEDULED:
                appointment.status = AppointmentStatus.NO_SHOW
            elif appointment.status == AppointmentStatus.ACTIVE:
                appointment.status = AppointmentStatus.COMPLETED
            
            appointment.slot.status = SlotStatus.COMPLETED
        
        self.db.commit()