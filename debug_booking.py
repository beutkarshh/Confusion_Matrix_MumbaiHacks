#!/usr/bin/env python3
"""
Debug appointment booking issues
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def test_booking_step_by_step():
    print("🔍 Debugging Appointment Booking Step by Step")
    print("=" * 50)
    
    # Test 1: Check if API is responding
    print("\n1. Testing API Health...")
    try:
        response = requests.get(f"{BACKEND_URL}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ API Error: {e}")
        return
    
    # Test 2: Check doctors endpoint
    print("\n2. Testing Doctors Endpoint...")
    try:
        headers = {"Authorization": "Bearer patient_token"}
        response = requests.get(f"{BACKEND_URL}/api/scheduling/doctors", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            doctors = response.json()
            print(f"   ✅ Found {len(doctors)} doctors")
            if doctors:
                print(f"   First doctor: {doctors[0]['user']['name']}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Check slots endpoint 
    print("\n3. Testing Slots Endpoint...")
    try:
        headers = {"Authorization": "Bearer patient_token"}
        response = requests.get(
            f"{BACKEND_URL}/api/scheduling/doctors/1/slots", 
            headers=headers,
            params={"date": "2025-12-01"}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        
    # Test 4: Test booking endpoint
    print("\n4. Testing Booking Endpoint...")
    try:
        headers = {"Authorization": "Bearer patient_token", "Content-Type": "application/json"}
        booking_data = {
            "slot_id": 1,
            "patient_symptoms": "Test symptoms",
            "patient_notes": "Debug test booking"
        }
        response = requests.post(
            f"{BACKEND_URL}/api/scheduling/appointments/book",
            headers=headers,
            json=booking_data
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_booking_step_by_step()