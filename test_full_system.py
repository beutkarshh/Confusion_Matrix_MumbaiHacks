"""
Full System Integration Test
Tests frontend config, backend API, and complete patient analysis workflow
"""

import requests
import json

BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://localhost:8080"

def print_header(text):
    print(f"\n{'='*80}")
    print(f"{text.center(80)}")
    print(f"{'='*80}\n")

def print_success(text):
    print(f"✓ {text}")

def print_error(text):
    print(f"✗ {text}")

def print_info(text):
    print(f"ℹ {text}")

def test_backend_health():
    """Test if backend is running"""
    print_header("Testing Backend Server")
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=5)
        if response.status_code == 200:
            print_success(f"Backend is running at {BACKEND_URL}")
            print_info(f"Response: {response.json()}")
            return True
        else:
            print_error(f"Backend returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Backend not reachable: {e}")
        return False

def test_frontend_health():
    """Test if frontend is serving"""
    print_header("Testing Frontend Server")
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print_success(f"Frontend is running at {FRONTEND_URL}")
            return True
        else:
            print_error(f"Frontend returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Frontend not reachable: {e}")
        return False

def test_patient_analysis():
    """Test complete patient analysis workflow"""
    print_header("Testing Patient Analysis Workflow")
    
    payload = {
        "patient_data": {
            "age": 55,
            "gender": "male",
            "symptoms": "chest pain, shortness of breath, sweating",
            "medical_history": "hypertension, smoking history",
            "current_medications": "lisinopril"
        }
    }
    
    try:
        print_info("Sending patient case to /analyze endpoint...")
        response = requests.post(
            f"{BACKEND_URL}/analyze",
            json=payload,
            timeout=60  # Analysis can take time
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success("Analysis completed successfully!")
            
            print(f"\n{Fore.MAGENTA}Analysis Results:")
            print(f"{Fore.MAGENTA}{'-'*80}")
            
            # Patient Summary
            if "patient_summary" in result:
                print(f"\n{Fore.WHITE}Patient Summary:")
                print(f"{result['patient_summary']}")
            
            # Clinical Summary
            if "clinical_summary" in result:
                print(f"\n{Fore.WHITE}Clinical Summary:")
                print(f"{result['clinical_summary']}")
            
            # Recommendations
            if "recommendations" in result:
                print(f"\n{Fore.WHITE}Recommendations:")
                for i, rec in enumerate(result["recommendations"], 1):
                    print(f"  {i}. [{rec.get('type', 'N/A')}] {rec.get('content', 'N/A')}")
            
            # Citations
            if "citations" in result:
                print(f"\n{Fore.WHITE}Citations:")
                print(f"  PMIDs: {result['citations'].get('pmids', [])}")
                print(f"  Sources: {result['citations'].get('sources', [])}")
            
            return True
        else:
            print_error(f"Analysis failed with status {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Analysis request failed: {e}")
        return False

def test_individual_agents():
    """Test individual agent endpoints"""
    print_header("Testing Individual Agent Endpoints")
    
    agents_tested = 0
    agents_passed = 0
    
    # Test symptom analyzer
    try:
        agents_tested += 1
        response = requests.post(
            f"{BACKEND_URL}/agents/symptom-analyzer",
            json={"symptoms": "fever, cough", "age": 30, "history": "none"},
            timeout=30
        )
        if response.status_code == 200:
            print_success("Symptom Analyzer agent working")
            agents_passed += 1
        else:
            print_error(f"Symptom Analyzer failed: {response.status_code}")
    except Exception as e:
        print_error(f"Symptom Analyzer error: {e}")
    
    # Test treatment agent
    try:
        agents_tested += 1
        response = requests.post(
            f"{BACKEND_URL}/agents/treatment",
            json={"diagnosis": "Type 2 Diabetes", "patient_context": "age 45"},
            timeout=30
        )
        if response.status_code == 200:
            print_success("Treatment agent working")
            agents_passed += 1
        else:
            print_error(f"Treatment agent failed: {response.status_code}")
    except Exception as e:
        print_error(f"Treatment agent error: {e}")
    
    # Test literature agent
    try:
        agents_tested += 1
        response = requests.post(
            f"{BACKEND_URL}/agents/literature",
            json={"query": "diabetes treatment"},
            timeout=30
        )
        if response.status_code == 200:
            print_success("Literature agent working")
            agents_passed += 1
        else:
            print_error(f"Literature agent failed: {response.status_code}")
    except Exception as e:
        print_error(f"Literature agent error: {e}")
    
    print(f"\n{Fore.CYAN}Agent Test Summary: {agents_passed}/{agents_tested} passed")
    return agents_passed == agents_tested

def main():
    print(f"\n{Fore.MAGENTA}{'*'*80}")
    print(f"{Fore.MAGENTA}{'GDHS Medical AI System - Full Integration Test'.center(80)}")
    print(f"{Fore.MAGENTA}{'*'*80}")
    
    results = {
        "Backend Health": test_backend_health(),
        "Frontend Health": test_frontend_health(),
        "Individual Agents": test_individual_agents(),
        "Full Patient Analysis": test_patient_analysis(),
    }
    
    # Summary
    print_header("Test Summary")
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Fore.GREEN}PASSED" if result else f"{Fore.RED}FAILED"
        print(f"{test_name:.<50} {status}")
    
    print(f"\n{Fore.CYAN}{'='*80}")
    if passed == total:
        print(f"{Fore.GREEN}ALL TESTS PASSED! ({passed}/{total})")
        print(f"{Fore.GREEN}System is fully operational and ready for use! 🎉")
    else:
        print(f"{Fore.YELLOW}SOME TESTS FAILED ({passed}/{total})")
        print(f"{Fore.YELLOW}Please check the errors above.")
    print(f"{Fore.CYAN}{'='*80}\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
