import requests
import json

# Test data - sample patient case
test_case = {
    "patient_id": "TEST001",
    "age": 45,
    "gender": "male",
    "symptoms": ["fever", "cough", "fatigue"],
    "medical_history": ["diabetes"],
    "current_medications": ["metformin"],
    "vital_signs": {
        "temperature": "38.5C",
        "blood_pressure": "130/85",
        "heart_rate": "95"
    },
    "lab_results": {
        "glucose": "elevated"
    }
}

print("Testing Orchestrator Workflow...")
print("=" * 60)
print(f"Patient Case: {json.dumps(test_case, indent=2)}")
print("=" * 60)

try:
    # Test the analyze endpoint
    response = requests.post(
        "http://127.0.0.1:8000/analyze",
        json=test_case,
        timeout=120  # 2 minute timeout for agent processing
    )
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✓ Orchestrator workflow completed successfully!")
        print("\nResults:")
        print("=" * 60)
        print(json.dumps(result, indent=2))
        print("=" * 60)
    else:
        print(f"\n✗ Error: {response.status_code}")
        print(response.text)
        
except requests.exceptions.Timeout:
    print("\n✗ Request timed out - agents may be taking too long or API keys exhausted")
except requests.exceptions.ConnectionError:
    print("\n✗ Connection error - is the backend server running on port 8000?")
except Exception as e:
    print(f"\n✗ Error: {str(e)}")
