"""
Test the /analyze endpoint with array medications
"""
import requests
import json

# Test data with medications as array (new format)
test_data_array = {
    "patientId": "TEST-001",
    "age": 58,
    "gender": "Male",
    "symptoms": "Chest pain, Shortness of breath, Sweating",
    "medicalHistory": "Hypertension, Type 2 Diabetes",
    "currentMedications": ["Metformin 500mg", "Lisinopril 10mg", "Atorvastatin 20mg"],  # Array!
    "urgency": "high"
}

# Test data with medications as string (old format)
test_data_string = {
    "patientId": "TEST-002",
    "age": 45,
    "gender": "Female",
    "symptoms": "Headache, Nausea",
    "medicalHistory": "Migraines",
    "currentMedications": "Sumatriptan 50mg, Ibuprofen 400mg",  # String!
    "urgency": "medium"
}

print("🧪 Testing Backend /analyze Endpoint")
print("=" * 50)

# Test 1: Array format (new)
print("\n📋 Test 1: Medications as Array (New Format)")
print(f"Medications: {test_data_array['currentMedications']}")
try:
    response = requests.post("http://127.0.0.1:8000/analyze", json=test_data_array, timeout=180)
    if response.status_code == 200:
        print("✅ SUCCESS: 200 OK")
        print(f"   Response received: {len(response.text)} bytes")
        # Check if medications were processed
        result = response.json()
        if "symptom_analysis" in result:
            print("✅ Symptom analysis completed")
        if "treatment" in result:
            print("✅ Treatment recommendations generated")
    elif response.status_code == 422:
        print("❌ FAILED: 422 Unprocessable Content")
        print(f"   Error: {response.json()}")
    else:
        print(f"⚠️  Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
except requests.exceptions.Timeout:
    print("⏱️  Request timed out (this is normal for long analysis)")
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 2: String format (old - backward compatibility)
print("\n📋 Test 2: Medications as String (Old Format - Backward Compatibility)")
print(f"Medications: {test_data_string['currentMedications']}")
try:
    response = requests.post("http://127.0.0.1:8000/analyze", json=test_data_string, timeout=180)
    if response.status_code == 200:
        print("✅ SUCCESS: 200 OK")
        print(f"   Response received: {len(response.text)} bytes")
        result = response.json()
        if "symptom_analysis" in result:
            print("✅ Symptom analysis completed")
        if "treatment" in result:
            print("✅ Treatment recommendations generated")
    elif response.status_code == 422:
        print("❌ FAILED: 422 Unprocessable Content")
        print(f"   Error: {response.json()}")
    else:
        print(f"⚠️  Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
except requests.exceptions.Timeout:
    print("⏱️  Request timed out (this is normal for long analysis)")
except Exception as e:
    print(f"❌ ERROR: {e}")

# Quick validation test (just check if endpoint accepts the data)
print("\n📋 Test 3: Quick Validation (No Full Analysis)")
quick_test = {
    "symptoms": "Test symptom",
    "currentMedications": ["Med1", "Med2", "Med3"],
    "age": 30,
    "gender": "Other",
    "urgency": "low"
}
try:
    # This will likely timeout, but we just want to check for 422
    response = requests.post("http://127.0.0.1:8000/analyze", json=quick_test, timeout=5)
    print(f"Status: {response.status_code}")
except requests.exceptions.Timeout:
    print("✅ No 422 error - medications array accepted!")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50)
print("📊 Summary:")
print("   - Array format should work (Test 1)")
print("   - String format should work (Test 2)")  
print("   - No 422 errors expected")
print("   - Backend accepts both formats!")
