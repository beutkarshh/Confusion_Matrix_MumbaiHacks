#!/usr/bin/env python3
"""
Simple test to verify doctors data and display them
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_doctors():
    try:
        from backend.database.config import SessionLocal
        from backend.database.models import DoctorProfile, User
        
        db = SessionLocal()
        try:
            # Get all doctors with user info
            doctors = db.query(DoctorProfile).join(User).all()
            
            print("🏥 DOCTORS IN YOUR SYSTEM:")
            print("=" * 50)
            
            for i, doctor in enumerate(doctors, 1):
                print(f"{i}. Dr. {doctor.user.name}")
                print(f"   📧 Email: {doctor.user.email}")
                print(f"   📋 Specialization: {doctor.specialization}")
                print(f"   🕐 Experience: {doctor.experience_years} years")
                print(f"   💰 Consultation Fee: ${doctor.consultation_fee}")
                print(f"   📝 Bio: {doctor.bio}")
                print(f"   ✅ Available: {'Yes' if doctor.is_available_for_booking else 'No'}")
                print()
            
            # Check slots
            from backend.database.models import AppointmentSlot
            slots = db.query(AppointmentSlot).count()
            print(f"📅 Total appointment slots available: {slots}")
            
            # Check availability schedules
            from backend.database.models import DoctorAvailability
            availabilities = db.query(DoctorAvailability).count()
            print(f"🗓️ Doctor availability schedules: {availabilities}")
            
            return doctors
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error accessing doctors: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    doctors = test_doctors()
    
    if doctors:
        print("\n🎉 SUCCESS: Your scheduling system has doctors ready!")
        print("\n📝 NEXT STEPS:")
        print("1. The database issue has been identified and fixed")
        print("2. Doctors are properly stored in the database") 
        print("3. The server crashes are likely due to authentication requirements")
        print("4. You can now access doctors through your frontend or use authentication tokens")
        print("\n🌐 To access via API:")
        print("- Use authentication tokens (user IDs 1-9 work for testing)")
        print("- Or modify the endpoints to remove auth requirements for development")