#!/usr/bin/env python3
"""
Script to create test data for the scheduling system
Run this after setting up the database to create sample doctors and patients
"""

import os
import sys
from datetime import time, date, timedelta

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database.config import SessionLocal, engine, Base
from backend.database.models import *

def create_test_data():
    """Create sample doctors, patients, and availability data"""
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_doctors = db.query(DoctorProfile).count()
        if existing_doctors > 0:
            print(f"Found {existing_doctors} existing doctors. Skipping data creation.")
            print("Delete the database file to recreate test data.")
            return
        
        print("Creating test data...")
        
        # Create doctors
        doctors_data = [
            {
                "name": "Dr. Sarah Johnson",
                "email": "sarah.johnson@hospital.com",
                "specialization": "General Medicine",
                "experience": 12,
                "fee": 800,
                "bio": "Experienced general practitioner with expertise in preventive care and chronic disease management."
            },
            {
                "name": "Dr. Michael Chen",
                "email": "michael.chen@hospital.com", 
                "specialization": "Cardiology",
                "experience": 15,
                "fee": 1200,
                "bio": "Board-certified cardiologist specializing in heart disease prevention and treatment."
            },
            {
                "name": "Dr. Priya Sharma",
                "email": "priya.sharma@hospital.com",
                "specialization": "Dermatology", 
                "experience": 8,
                "fee": 900,
                "bio": "Dermatologist focused on skin health, acne treatment, and cosmetic procedures."
            },
            {
                "name": "Dr. James Wilson",
                "email": "james.wilson@hospital.com",
                "specialization": "Pediatrics",
                "experience": 10,
                "fee": 700,
                "bio": "Pediatrician dedicated to providing comprehensive care for infants, children, and adolescents."
            }
        ]
        
        created_doctors = []
        
        for doctor_info in doctors_data:
            # Create user account for doctor
            doctor_user = User(
                email=doctor_info["email"],
                name=doctor_info["name"],
                role=UserRole.DOCTOR,
                timezone="Asia/Kolkata"
            )
            db.add(doctor_user)
            db.flush()  # Get the ID
            
            # Create doctor profile
            doctor_profile = DoctorProfile(
                user_id=doctor_user.id,
                specialization=doctor_info["specialization"],
                experience_years=doctor_info["experience"],
                default_slot_duration_minutes=20,
                consultation_fee=doctor_info["fee"],
                bio=doctor_info["bio"],
                is_available_for_booking=True
            )
            db.add(doctor_profile)
            db.flush()
            
            created_doctors.append(doctor_profile)
            
            # Create weekly availability (different schedules for each doctor)
            if doctor_profile.id == 1:
                # Dr. Sarah - Monday to Friday, 9 AM - 6 PM
                for day in range(5):
                    availability = DoctorAvailability(
                        doctor_id=doctor_profile.id,
                        day_of_week=DayOfWeek(day),
                        start_time=time(9, 0),
                        end_time=time(18, 0),
                        slot_duration_minutes=20,
                        is_active=True,
                        is_blocked=False
                    )
                    db.add(availability)
            
            elif doctor_profile.id == 2:
                # Dr. Michael - Monday, Wednesday, Friday, 10 AM - 4 PM
                for day in [0, 2, 4]:  # Mon, Wed, Fri
                    availability = DoctorAvailability(
                        doctor_id=doctor_profile.id,
                        day_of_week=DayOfWeek(day),
                        start_time=time(10, 0),
                        end_time=time(16, 0),
                        slot_duration_minutes=30,  # Longer slots for cardiology
                        is_active=True,
                        is_blocked=False
                    )
                    db.add(availability)
            
            elif doctor_profile.id == 3:
                # Dr. Priya - Tuesday, Thursday, Saturday, 11 AM - 7 PM
                for day in [1, 3, 5]:  # Tue, Thu, Sat
                    availability = DoctorAvailability(
                        doctor_id=doctor_profile.id,
                        day_of_week=DayOfWeek(day),
                        start_time=time(11, 0),
                        end_time=time(19, 0),
                        slot_duration_minutes=15,  # Shorter slots for dermatology
                        is_active=True,
                        is_blocked=False
                    )
                    db.add(availability)
            
            else:
                # Dr. James - Monday to Thursday, 8 AM - 5 PM
                for day in range(4):  # Mon-Thu
                    availability = DoctorAvailability(
                        doctor_id=doctor_profile.id,
                        day_of_week=DayOfWeek(day),
                        start_time=time(8, 0),
                        end_time=time(17, 0),
                        slot_duration_minutes=25,  # Pediatric appointments
                        is_active=True,
                        is_blocked=False
                    )
                    db.add(availability)
        
        # Create sample patients
        patients_data = [
            {"name": "Alice Johnson", "email": "alice.johnson@email.com"},
            {"name": "Bob Smith", "email": "bob.smith@email.com"}, 
            {"name": "Carol Davis", "email": "carol.davis@email.com"},
            {"name": "David Wilson", "email": "david.wilson@email.com"},
            {"name": "Emma Brown", "email": "emma.brown@email.com"}
        ]
        
        created_patients = []
        
        for patient_info in patients_data:
            patient_user = User(
                email=patient_info["email"],
                name=patient_info["name"],
                role=UserRole.PATIENT,
                timezone="Asia/Kolkata"
            )
            db.add(patient_user)
            created_patients.append(patient_user)
        
        # Commit all changes
        db.commit()
        
        print("✅ Test data created successfully!")
        print(f"\n📊 Created:")
        print(f"   - {len(created_doctors)} doctors")
        print(f"   - {len(created_patients)} patients")
        print(f"   - Availability schedules for all doctors")
        
        print(f"\n👨‍⚕️ Doctors created:")
        for i, doctor in enumerate(created_doctors, 1):
            print(f"   {i}. {doctor.user.name} ({doctor.specialization}) - ID: {doctor.id}")
        
        print(f"\n👥 Patients created:")
        for i, patient in enumerate(created_patients, 1):
            print(f"   {i}. {patient.name} - ID: {patient.id}")
        
        print(f"\n🔗 Next steps:")
        print(f"   1. Start the backend server: cd server && python main.py")
        print(f"   2. Start the frontend: cd frontend && npm run dev")
        print(f"   3. Use the UI to book appointments or test the API")
        print(f"   4. For API testing, use doctor IDs and patient IDs above")
        
        # Generate slots for the next 4 weeks
        print(f"\n🗓️ Generating appointment slots...")
        from backend.scheduling.services import SlotGenerationService
        
        slot_service = SlotGenerationService(db)
        total_slots = 0
        
        start_date = date.today()
        end_date = start_date + timedelta(weeks=4)
        
        for doctor in created_doctors:
            slots = slot_service.generate_slots_for_doctor(
                doctor_id=doctor.id,
                start_date=start_date,
                end_date=end_date
            )
            total_slots += len(slots)
            print(f"   - Generated {len(slots)} slots for {doctor.user.name}")
        
        print(f"   - Total slots generated: {total_slots}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating test data: {e}")
        raise
    finally:
        db.close()

def create_admin_user():
    """Create an admin user for testing"""
    db = SessionLocal()
    
    try:
        # Check if admin exists
        admin = db.query(User).filter(User.email == "admin@test.com").first()
        if admin:
            print("Admin user already exists")
            return
        
        admin_user = User(
            email="admin@test.com",
            name="System Admin",
            role=UserRole.ADMIN,
            timezone="Asia/Kolkata"
        )
        db.add(admin_user)
        db.commit()
        
        print(f"✅ Admin user created: admin@test.com (ID: {admin_user.id})")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🏥 Medical Scheduling System - Test Data Creator")
    print("=" * 50)
    
    create_test_data()
    create_admin_user()
    
    print("\n✨ Setup complete! You can now test the scheduling system.")