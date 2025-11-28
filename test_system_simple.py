"""
Simple Full System Test - Tests backend, frontend, and patient analysis
"""
import requests
import json

BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://localhost:8080"

print("\n" + "="*80)
print("GDHS Medical AI System - Integration Test".center(80))
print("="*80 + "\n")

# Test 1: Backend Health
print("1. Testing Backend Server...")
try:
    resp = requests.get(f"{BACKEND_URL}/", timeout=5)
    if resp.status_code == 200:
        print("   ✓ Backend is running")
        print(f"   Response: {resp.json()}")
    else:
        print(f"   ✗ Backend error: {resp.status_code}")
except Exception as e:
    print(f"   ✗ Backend not reachable: {e}")

# Test 2: Frontend Health
print("\n2. Testing Frontend Server...")
try:
    resp = requests.get(FRONTEND_URL, timeout=5)
    if resp.status_code == 200:
        print("   ✓ Frontend is running")
    else:
        print(f"   ✗ Frontend error: {resp.status_code}")
except Exception as e:
    print(f"   ✗ Frontend not reachable: {e}")

# Test 3: Patient Analysis
print("\n3. Testing Patient Analysis Workflow...")
payload = {
    "symptoms": "chest pain, shortness of breath, sweating",
    "age": 55,
    "gender": "male",
    "medicalHistory": "hypertension, smoking history",
    "currentMedications": "lisinopril",
    "urgency": "high"
}

try:
    print("   Sending patient case to /analyze endpoint...")
    resp = requests.post(f"{BACKEND_URL}/analyze", json=payload, timeout=60)
    
    if resp.status_code == 200:
        result = resp.json()
        print("   ✓ Analysis completed successfully!\n")
        
        print("   " + "-"*76)
        print("   ANALYSIS RESULTS")
        print("   " + "-"*76)
        
        if "patient_summary" in result:
            print(f"\n   Patient Summary:\n   {result['patient_summary']}\n")
        
        if "clinical_summary" in result:
            print(f"   Clinical Summary:\n   {result['clinical_summary']}\n")
        
        if "recommendations" in result:
            print("   Recommendations:")
            for i, rec in enumerate(result["recommendations"], 1):
                print(f"     {i}. [{rec.get('type', 'N/A')}] {rec.get('content', 'N/A')}")
        
        if "citations" in result:
            print(f"\n   Citations:")
            print(f"     PMIDs: {result['citations'].get('pmids', [])}")
            print(f"     Sources: {', '.join(result['citations'].get('sources', []))}")
    else:
        print(f"   ✗ Analysis failed: {resp.status_code}")
        print(f"   {resp.text}")
except Exception as e:
    print(f"   ✗ Analysis error: {e}")

# Summary
print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
print("\nSystem Status:")
print("  - Backend API: http://127.0.0.1:8000")
print("  - Frontend UI: http://localhost:8080")
print("  - API Docs: http://127.0.0.1:8000/docs")
print("\nNext steps:")
print("  1. Open http://localhost:8080 to test login/signup")
print("  2. Submit a patient case through the UI")
print("  3. Review the AI-generated analysis\n")
