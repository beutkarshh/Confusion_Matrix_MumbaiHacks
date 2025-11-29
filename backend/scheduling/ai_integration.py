from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from ..database.models import Appointment, AppointmentStatus
from ..orchestrator.orchestrator import build_orchestrator_graph
from ..utils.pdf_generator import generate_pdf_from_analysis

class ConsultationAIService:
    """
    Service for integrating appointment consultations with AI analysis pipeline
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_graph = build_orchestrator_graph()
    
    def trigger_post_consultation_analysis(
        self, 
        appointment_id: int,
        trigger_pdf: bool = True
    ) -> Dict[str, Any]:
        """
        Trigger AI analysis after a consultation is completed
        
        Args:
            appointment_id: ID of the completed appointment
            trigger_pdf: Whether to generate PDF report automatically
        
        Returns:
            Dictionary containing analysis results and PDF info
        """
        
        # Get appointment details
        appointment = self.db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise ValueError(f"Appointment {appointment_id} not found")
        
        if appointment.status != AppointmentStatus.COMPLETED:
            raise ValueError(f"Appointment {appointment_id} is not completed")
        
        # Prepare input for AI analysis
        ai_input = self._prepare_ai_input(appointment)
        
        # Run AI analysis
        try:
            analysis_results = self.ai_graph.invoke(ai_input)
            
            # Mark AI analysis as triggered
            appointment.ai_analysis_triggered = True
            
            # Generate PDF if requested
            pdf_path = None
            if trigger_pdf:
                pdf_path = self._generate_consultation_pdf(appointment, analysis_results)
                if pdf_path:
                    appointment.pdf_generated = True
                    appointment.pdf_path = pdf_path
            
            self.db.commit()
            
            return {
                "success": True,
                "analysis_results": analysis_results,
                "pdf_path": pdf_path,
                "appointment_id": appointment_id
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "error": str(e),
                "appointment_id": appointment_id
            }
    
    def _prepare_ai_input(self, appointment: Appointment) -> Dict[str, Any]:
        """Prepare input data for AI analysis from appointment details"""
        
        # Extract patient information from appointment
        patient = appointment.patient
        doctor = appointment.doctor
        
        # Combine symptoms from booking and doctor's observations
        symptoms = []
        if appointment.patient_symptoms:
            symptoms.append(f"Patient reported: {appointment.patient_symptoms}")
        if appointment.doctor_notes:
            symptoms.append(f"Doctor observed: {appointment.doctor_notes}")
        
        combined_symptoms = ". ".join(symptoms)
        
        # Prepare input in the format expected by the AI pipeline
        ai_input = {
            "symptoms": combined_symptoms or "General consultation",
            "age": getattr(patient, 'age', None),  # Add age field to User model if needed
            "gender": getattr(patient, 'gender', None),  # Add gender field if needed
            "medicalHistory": getattr(patient, 'medical_history', None),  # Add if needed
            "currentMedications": getattr(patient, 'current_medications', None),  # Add if needed
            "urgency": "routine",  # Default for scheduled appointments
            
            # Additional context from consultation
            "consultationNotes": appointment.doctor_notes or "",
            "consultationSummary": appointment.consultation_summary or "",
            "consultationDate": appointment.completed_at.isoformat() if appointment.completed_at else "",
            "doctorSpecialization": doctor.specialization or "General Medicine"
        }
        
        return ai_input
    
    def _generate_consultation_pdf(
        self, 
        appointment: Appointment, 
        analysis_results: Dict[str, Any]
    ) -> Optional[str]:
        """Generate PDF report from consultation and AI analysis"""
        
        try:
            # Prepare PDF payload with consultation context
            pdf_payload = {
                "patient_info": {
                    "name": appointment.patient.name,
                    "email": appointment.patient.email,
                    "consultation_date": appointment.completed_at.isoformat() if appointment.completed_at else "",
                    "doctor": f"Dr. {appointment.doctor.user.name}",
                    "specialization": appointment.doctor.specialization,
                    "appointment_duration": f"{appointment.slot.duration_minutes} minutes",
                    "symptoms_reported": appointment.patient_symptoms,
                    "patient_notes": appointment.patient_notes
                },
                "consultation_details": {
                    "doctor_notes": appointment.doctor_notes,
                    "consultation_summary": appointment.consultation_summary,
                    "appointment_type": "Video Consultation",
                    "status": "Completed"
                }
            }
            
            # Add AI analysis results to payload
            if "symptom_analysis" in analysis_results:
                pdf_payload["symptom_analysis"] = analysis_results["symptom_analysis"]
            
            if "literature" in analysis_results:
                pdf_payload["literature"] = analysis_results["literature"]
            
            if "case_matcher" in analysis_results:
                pdf_payload["case_matcher"] = analysis_results["case_matcher"]
            
            if "treatment" in analysis_results:
                pdf_payload["treatment"] = analysis_results["treatment"]
            
            if "summary" in analysis_results:
                pdf_payload["summary"] = analysis_results["summary"]
            
            # Generate PDF
            pdf_bytes = generate_pdf_from_analysis(pdf_payload)
            
            # Save PDF to file system (in production, use cloud storage)
            import os
            pdf_dir = "generated_reports"
            os.makedirs(pdf_dir, exist_ok=True)
            
            pdf_filename = f"consultation_report_{appointment.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf_path = os.path.join(pdf_dir, pdf_filename)
            
            with open(pdf_path, 'wb') as f:
                f.write(pdf_bytes if isinstance(pdf_bytes, bytes) else bytes(pdf_bytes))
            
            return pdf_path
            
        except Exception as e:
            print(f"Failed to generate PDF for appointment {appointment.id}: {e}")
            return None
    
    def get_analysis_status(self, appointment_id: int) -> Dict[str, Any]:
        """Get the status of AI analysis for an appointment"""
        
        appointment = self.db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            return {"error": "Appointment not found"}
        
        return {
            "appointment_id": appointment_id,
            "status": appointment.status,
            "ai_analysis_triggered": appointment.ai_analysis_triggered,
            "pdf_generated": appointment.pdf_generated,
            "pdf_path": appointment.pdf_path,
            "completed_at": appointment.completed_at.isoformat() if appointment.completed_at else None
        }
    
    def regenerate_analysis(self, appointment_id: int) -> Dict[str, Any]:
        """Regenerate AI analysis and PDF for an appointment"""
        
        appointment = self.db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            return {"error": "Appointment not found"}
        
        if appointment.status != AppointmentStatus.COMPLETED:
            return {"error": "Can only regenerate analysis for completed appointments"}
        
        # Reset flags
        appointment.ai_analysis_triggered = False
        appointment.pdf_generated = False
        self.db.commit()
        
        # Trigger new analysis
        return self.trigger_post_consultation_analysis(appointment_id, trigger_pdf=True)