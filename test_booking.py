#!/usr/bin/env python3
"""
Test script to demonstrate appointment booking functionality
"""
import requests
import json
from datetime import datetime

# API base URL
BASE_URL = "http://127.0.0.1:8000"

def test_booking():
    print("🧪 Testing Appointment Booking System")
    print("=" * 50)
    
    # Test 1: Get doctors
    print("\n1. Getting available doctors...")
    response = requests.get(f"{BASE_URL}/api/scheduling/doctors")
    if response.status_code == 200:
        doctors = response.json()
        print(f"✅ Found {len(doctors)} doctors")
        for doctor in doctors[:2]:  # Show first 2
            print(f"   - Dr. {doctor['user']['name']} ({doctor['specialization']})")
    else:
        print(f"❌ Failed to get doctors: {response.status_code}")
        return
    
    # Test 2: Get slots for first doctor
    doctor_id = doctors[0]['id']
    print(f"\n2. Getting slots for doctor ID {doctor_id}...")
    response = requests.get(f"{BASE_URL}/api/scheduling/doctors/{doctor_id}/slots?target_date=2025-11-29")
    if response.status_code == 200:
        slots = response.json()
        print(f"✅ Found {len(slots)} available slots")
        if slots:
            print(f"   - First slot: {slots[0]['start_time']} - {slots[0]['end_time']}")
            slot_id = slots[0]['id']
        else:
            print("   ⚠️ No slots available for today")
            return
    else:
        print(f"❌ Failed to get slots: {response.status_code}")
        return
    
    # Test 3: Book an appointment (as patient ID 5 - Alice Johnson)
    print(f"\n3. Booking appointment (as patient Alice Johnson, ID 5)...")
    headers = {
        "Authorization": "Bearer 5",
        "Content-Type": "application/json"
    }
    booking_data = {
        "slot_id": slot_id,
        "notes": "Test booking from Python script"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/scheduling/appointments/book", 
        headers=headers,
        json=booking_data
    )
    
    if response.status_code == 200:
        booking = response.json()
        print("✅ Booking successful!")
        print(f"   - Appointment ID: {booking['id']}")
        print(f"   - Date: {booking['appointment_date']}")
        print(f"   - Time: {booking['start_time']} - {booking['end_time']}")
        print(f"   - Doctor: {booking['doctor']['specialization']}")
        print(f"   - Status: {booking['status']}")
    else:
        print(f"❌ Booking failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return
    
    # Test 4: Get patient's appointments
    print(f"\n4. Getting patient's appointments...")
    response = requests.get(f"{BASE_URL}/api/scheduling/appointments/my", headers=headers)
    if response.status_code == 200:
        appointments = response.json()
        print(f"✅ Patient has {len(appointments)} appointments")
        for apt in appointments:
            print(f"   - {apt['appointment_date']} at {apt['start_time']} with Dr. {apt['doctor']['user']['name']}")
    else:
        print(f"❌ Failed to get appointments: {response.status_code}")
    
    print("\n🎉 All tests completed! Your scheduling system is working perfectly!")
    print("\n💡 To use in frontend:")
    print("   1. Open browser console (F12)")
    print("   2. Run: localStorage.setItem('authToken', '5')")  
    print("   3. Refresh page and try booking appointments")

if __name__ == "__main__":
    try:
        test_booking()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server. Make sure it's running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error: {e}")