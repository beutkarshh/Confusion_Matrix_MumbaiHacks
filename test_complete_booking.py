#!/usr/bin/env python3
"""
Final test to verify the complete booking system is working
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8080"

def test_full_system():
    print("🚀 Testing Complete Telemedicine Booking System")
    print("=" * 50)
    
    # Test 1: Backend Health Check
    print("\n1. Testing Backend Health...")
    try:
        response = requests.get(f"{BACKEND_URL}/")
        if response.status_code == 200:
            print("✅ Backend is running!")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return
    
    # Test 2: List Available Doctors
    print("\n2. Testing Doctor Listing...")
    try:
        headers = {"Authorization": "Bearer patient_token"}
        response = requests.get(f"{BACKEND_URL}/api/scheduling/doctors", headers=headers)
        if response.status_code == 200:
            doctors = response.json()
            print(f"✅ Found {len(doctors)} doctors available!")
            for doctor in doctors:
                print(f"   - Dr. {doctor['user']['name']} ({doctor['specialization']})")
        else:
            print(f"❌ Doctor listing failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Doctor listing error: {e}")
        return
    
    # Test 3: Get Available Slots
    print("\n3. Testing Appointment Slots...")
    try:
        headers = {"Authorization": "Bearer patient_token"}
        response = requests.get(
            f"{BACKEND_URL}/api/scheduling/doctors/1/slots",
            params={"date": "2025-12-01"},
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            slots = data.get('available_slots', [])
            print(f"✅ Found {len(slots)} available slots for Dec 1st!")
        else:
            print(f"❌ Slot listing failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Slot listing error: {e}")
    
    # Test 4: Authentication Check
    print("\n4. Testing Authentication...")
    try:
        headers = {"Authorization": "Bearer patient_token"}
        response = requests.get(f"{BACKEND_URL}/api/scheduling/appointments/my", headers=headers)
        if response.status_code == 200:
            appointments = response.json()
            print(f"✅ Authentication working! Found {len(appointments)} existing appointments")
        else:
            print(f"❌ Authentication failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Authentication error: {e}")
    
    # Test 5: Frontend Availability
    print("\n5. Testing Frontend Availability...")
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible!")
        else:
            print(f"❌ Frontend not accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend connection failed: {e}")
    
    print("\n" + "=" * 50)
    print("✨ System Test Complete!")
    print(f"📱 Frontend: {FRONTEND_URL}")
    print(f"🔧 Backend API: {BACKEND_URL}")
    print("\n🎯 Ready for patient consultations!")
    print("\nTo use the system:")
    print("1. Open the frontend URL in your browser")
    print("2. Use the quick login for patients or doctors")
    print("3. Browse available doctors and book appointments")
    print("4. Manage your appointments and consultations")

if __name__ == "__main__":
    test_full_system()