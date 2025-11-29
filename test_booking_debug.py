#!/usr/bin/env python3
"""
Test booking an appointment to trigger debug output
"""
import requests
import json

def test_booking():
    url = "http://localhost:8000/api/scheduling/appointments/book"
    headers = {
        "Authorization": "Bearer 5",  # Alice Johnson
        "Content-Type": "application/json"
    }
    data = {
        "slot_id": 1,
        "patient_notes": "Test booking debug"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 403:
            print("❌ 403 Forbidden - Check debug output in server logs")
        elif response.status_code == 200:
            print("✅ Booking successful!")
        else:
            print(f"⚠️ Unexpected status: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_booking()